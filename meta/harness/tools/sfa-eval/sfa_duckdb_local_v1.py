#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "openai>=1.63.0",
#   "rich>=13.7.0",
#   "pydantic>=2.0.0",
# ]
# ///
"""sfa_duckdb_local_v1.py — DuckDB query agent over a local MLX model.

LATTICE-adapted port of:
    https://github.com/disler/single-file-agents/blob/main/sfa_duckdb_openai_v2.py

The Disler original calls OpenAI directly. This port routes through the
llama-swap proxy at http://localhost:9090 — meaning the same code can hit
ANY model in `meta/harness/bin/llama-swap/config.yaml`:

    bonsai-4b      ← default — PrismML Ternary Bonsai 4B (1.1 GB ternary)
    bonsai-8b      ← bigger, slower
    hermes-3-8b    ← Llama 3.1 derivative
    qwen3.6-35b    ← Qwen MoE

Status: PRE-CAPABILITY evaluation. This SFA lives in `sfa-eval/` to
prove the local-model swap works end-to-end. If it does, it earns a row
in the capability registry as ACTIVE. If it does not, the evidence file
documents what failed and the row stays DEFERRED with `reason:
awaiting-upstream-dep` (model lacks tool-calling support).

Pattern preserved from Disler
-----------------------------
- 5 Pydantic tool models (list / describe / sample / test-sql / final-sql)
- OpenAI-style function calling with tool_choice="required"
- Compute loop: model picks a tool → we execute → feed result back → repeat
- Final answer comes when the model invokes RunFinalSQLQuery

Pattern changed for LATTICE
---------------------------
- `openai.OpenAI(base_url='http://localhost:9090/v1', api_key='not-needed')`
- `--model` flag defaults to `bonsai-4b` (llama-swap-friendly name)
- Marker JSON written at end per SPEC_SFA_PATTERN.md §3
- Full transcript captured for evaluation evidence

Usage
-----
    # Prerequisite: llama-swap running + DuckDB cache populated
    bash meta/harness/bin/llama-swap/llama-swap \\
        -config meta/harness/bin/llama-swap/config.yaml -listen :9090 &
    uv run meta/harness/tools/sfa-eval/sfa_init_caches.py

    # Run the agent
    uv run meta/harness/tools/sfa-eval/sfa_duckdb_local_v1.py \\
        --prompt "What is the tallest plant in the cache, and how tall is it?"

    # Use a different model from llama-swap
    uv run meta/harness/tools/sfa-eval/sfa_duckdb_local_v1.py \\
        --model bonsai-8b \\
        --prompt "List all plants native to the Mediterranean."
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import openai
from openai import pydantic_function_tool
from pydantic import BaseModel, Field, ValidationError
from rich.console import Console
from rich.panel import Panel

# ── LATTICE config ───────────────────────────────────────────────────────────
_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent.parent.parent.parent
DEFAULT_DB = str(_REPO / "meta" / "harness" / "state" / "cache" / "sfa-eval.duckdb")
DEFAULT_BASE_URL = "http://localhost:9090/v1"
DEFAULT_MODEL = "bonsai-4b"
STATE_DIR = _REPO / "meta" / "harness" / "state"
SESSIONS_DIR = _REPO / "meta" / "harness" / "docs" / "sessions"

console = Console()

# Global, set in main()
DB_PATH: str = DEFAULT_DB

# ── Pydantic tool models (preserved from Disler) ─────────────────────────────


class ListTablesArgs(BaseModel):
    reasoning: str = Field(..., description="Explanation for listing tables relative to the user request")


class DescribeTableArgs(BaseModel):
    reasoning: str = Field(..., description="Reason why the table schema is needed")
    table_name: str = Field(..., description="Name of the table to describe")


class SampleTableArgs(BaseModel):
    reasoning: str = Field(..., description="Explanation for sampling the table")
    table_name: str = Field(..., description="Name of the table to sample")
    row_sample_size: int = Field(..., description="Number of rows to sample (aim for 3-5 rows)")


class RunTestSQLQuery(BaseModel):
    reasoning: str = Field(..., description="Reason for testing this query")
    sql_query: str = Field(..., description="The SQL query to test")


class RunFinalSQLQuery(BaseModel):
    reasoning: str = Field(..., description="Final explanation of how this query satisfies the user request")
    sql_query: str = Field(..., description="The validated SQL query to run")


# ── Local-model tool-call fallback parsers ──────────────────────────────────
#
# OpenAI tool calling round-trips through the dedicated `tool_calls` field in
# the API response. Many local MLX models (Qwen-family, including Bonsai) are
# trained to emit a Qwen-style `<tool_call>{"name": ..., "arguments": ...}
# </tool_call>` block in the message content instead — and mlx_lm.server does
# not currently translate that to OpenAI's wire format. This fallback walks
# the message content looking for those patterns.

_QWEN_TOOL_RE = re.compile(r"<tool_call>\s*(.*?)\s*</tool_call>", re.DOTALL)
_PLAIN_JSON_TOOL_RE = re.compile(r'\{\s*"name"\s*:\s*"(\w+)"\s*,\s*"arguments"\s*:\s*\{.*?\}\s*\}', re.DOTALL)
_KNOWN_TOOLS = {"ListTablesArgs", "DescribeTableArgs", "SampleTableArgs", "RunTestSQLQuery", "RunFinalSQLQuery"}


class _PseudoToolCall:
    """Mimics openai.types.chat.ChatCompletionMessageToolCall enough for the loop."""

    def __init__(self, name: str, arguments: str):
        self.id = f"local-{uuid.uuid4().hex[:8]}"
        self.type = "function"
        self.function = type("F", (), {"name": name, "arguments": arguments})()


def extract_pseudo_tool_calls(content: str | None) -> list[_PseudoToolCall]:
    """Parse Qwen-style `<tool_call>...</tool_call>` or bare JSON tool blocks."""
    if not content:
        return []
    calls: list[_PseudoToolCall] = []
    # Prefer XML-delimited blocks
    for match in _QWEN_TOOL_RE.findall(content):
        try:
            payload = json.loads(match)
            name = payload.get("name")
            args = payload.get("arguments") or {}
            if name in _KNOWN_TOOLS:
                calls.append(_PseudoToolCall(name, json.dumps(args)))
        except json.JSONDecodeError:
            continue
    if calls:
        return calls
    # Fallback: bare JSON object {"name": "...", "arguments": {...}}
    for match in _PLAIN_JSON_TOOL_RE.finditer(content):
        try:
            payload = json.loads(match.group(0))
            name = payload.get("name")
            args = payload.get("arguments") or {}
            if name in _KNOWN_TOOLS:
                calls.append(_PseudoToolCall(name, json.dumps(args)))
        except json.JSONDecodeError:
            continue
    return calls


def _build_tools() -> list[dict]:
    return [
        pydantic_function_tool(ListTablesArgs),
        pydantic_function_tool(DescribeTableArgs),
        pydantic_function_tool(SampleTableArgs),
        pydantic_function_tool(RunTestSQLQuery),
        pydantic_function_tool(RunFinalSQLQuery),
    ]


# ── Tool implementations (subprocess to the `duckdb` CLI for portability) ────


def _duckdb_sh(sql: str) -> str:
    """Run a SQL statement via the duckdb CLI; return stdout."""
    try:
        result = subprocess.run(
            ["duckdb", DB_PATH, "-c", sql],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if result.returncode != 0:
            return f"DuckDB error (rc={result.returncode}): {result.stderr.strip()}"
        return result.stdout.strip()
    except FileNotFoundError:
        # Fallback to python duckdb if CLI isn't installed
        import duckdb

        con = duckdb.connect(DB_PATH, read_only=False)
        try:
            rows = con.execute(sql).fetchall()
            cols = [d[0] for d in con.description] if con.description else []
            if cols:
                lines = ["\t".join(cols)] + ["\t".join(str(v) for v in r) for r in rows]
                return "\n".join(lines)
            return f"affected {len(rows)} rows"
        finally:
            con.close()


def list_tables(reasoning: str) -> str:
    console.print(Panel(f"[cyan]list_tables[/cyan]\n[dim]{reasoning}[/dim]", expand=False))
    return _duckdb_sh("SHOW TABLES")


def describe_table(reasoning: str, table_name: str) -> str:
    console.print(Panel(f"[cyan]describe_table {table_name}[/cyan]\n[dim]{reasoning}[/dim]", expand=False))
    return _duckdb_sh(f"DESCRIBE {table_name}")


def sample_table(reasoning: str, table_name: str, row_sample_size: int) -> str:
    n = max(1, min(20, int(row_sample_size)))
    console.print(Panel(f"[cyan]sample_table {table_name} ({n} rows)[/cyan]\n[dim]{reasoning}[/dim]", expand=False))
    return _duckdb_sh(f"SELECT * FROM {table_name} LIMIT {n}")


def run_test_sql_query(reasoning: str, sql_query: str) -> str:
    console.print(Panel(f"[cyan]test SQL[/cyan]\n[dim]{reasoning}[/dim]\n\n[yellow]{sql_query}[/yellow]", expand=False))
    return _duckdb_sh(sql_query)


def run_final_sql_query(reasoning: str, sql_query: str) -> str:
    console.print(Panel(f"[green]FINAL SQL[/green]\n[dim]{reasoning}[/dim]\n\n[yellow]{sql_query}[/yellow]", expand=False))
    return _duckdb_sh(sql_query)


# ── Prompt template (preserved structure from Disler) ────────────────────────


AGENT_PROMPT = """<purpose>
You are a senior data engineer. Answer the user request by querying the DuckDB
database. Use ONLY the function tools provided — never produce free-form prose.
</purpose>

<process>
1. Call ListTablesArgs to see what's in the database.
2. Call DescribeTableArgs on the table you intend to query.
3. Optionally call SampleTableArgs to see a few rows (max 5).
4. Call RunTestSQLQuery to test your query; iterate if it errors.
5. Call RunFinalSQLQuery with your validated query — this ends the task.
</process>

<rules>
- Each call MUST include a non-empty `reasoning` field explaining why.
- Prefer the simplest query that answers the user request.
- Never run a final query that hasn't been tested first.
- Maximum 8 tool calls total; budget your steps.
</rules>

<user-request>
{{user_request}}
</user-request>
"""


# ── Main compute loop ────────────────────────────────────────────────────────


def write_marker(payload: dict) -> Path:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    marker = STATE_DIR / "_duckdb_local_v1.done.json"
    marker.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return marker


def write_session(payload: dict, name: str) -> Path:
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    fname = f"{datetime.now(timezone.utc).strftime('%Y-%m-%d-%H%M%S')}-duckdb-local-{name}.json"
    path = SESSIONS_DIR / fname
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--prompt", "-p", required=True, help="Natural-language data question")
    parser.add_argument("--db", default=DEFAULT_DB, help=f"DuckDB file (default {DEFAULT_DB})")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Model name from llama-swap (default {DEFAULT_MODEL})")
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"OpenAI-compatible base URL (default {DEFAULT_BASE_URL}, points at llama-swap)",
    )
    parser.add_argument("--compute", type=int, default=10, help="Maximum compute loops (default 10)")
    parser.add_argument("--session-tag", default="adhoc", help="Tag for the session log filename")
    args = parser.parse_args()

    global DB_PATH
    DB_PATH = args.db
    if not Path(DB_PATH).exists():
        console.print(f"[red]DuckDB file not found: {DB_PATH}[/red]")
        console.print(f"[yellow]Run: uv run meta/harness/tools/sfa-eval/sfa_init_caches.py[/yellow]")
        return 2

    client = openai.OpenAI(base_url=args.base_url, api_key=os.getenv("OPENAI_API_KEY", "not-needed"))
    tools = _build_tools()

    completed_prompt = AGENT_PROMPT.replace("{{user_request}}", args.prompt)
    messages: list[dict] = [{"role": "user", "content": completed_prompt}]

    transcript: list[dict] = []
    final_result: str | None = None
    final_query: str | None = None
    final_reasoning: str | None = None
    error: str | None = None
    started_at = time.time()

    for iteration in range(1, args.compute + 1):
        console.rule(f"[yellow]Loop {iteration}/{args.compute} — model={args.model}[/yellow]")
        try:
            response = client.chat.completions.create(
                model=args.model,
                messages=messages,
                tools=tools,
                tool_choice="required",
                timeout=120,
            )
        except Exception as e:
            error = f"chat.completions.create raised: {type(e).__name__}: {e}"
            console.print(f"[red]{error}[/red]")
            break

        if not response.choices:
            error = "no choices in response"
            break
        message = response.choices[0].message
        transcript.append({"role": "assistant", "content": message.content, "tool_calls": [
            {"id": tc.id, "name": tc.function.name, "arguments": tc.function.arguments}
            for tc in (message.tool_calls or [])
        ]})

        local_calls: list[_PseudoToolCall] = []
        if not message.tool_calls:
            # Local-model fallback: parse Qwen-style <tool_call>...</tool_call>
            local_calls = extract_pseudo_tool_calls(message.content)
            if not local_calls:
                console.print(
                    f"[yellow]No native or Qwen-style tool call in response:[/yellow]\n{(message.content or '')[:400]}"
                )
                error = "model produced neither a tool_calls field nor a parseable <tool_call> block"
                break
            console.print(f"[magenta]Parsed Qwen-style tool call from content: {local_calls[0].function.name}[/magenta]")

        tool_call = message.tool_calls[0] if message.tool_calls else local_calls[0]
        func_name = tool_call.function.name
        func_args_str = tool_call.function.arguments

        messages.append(
            {
                "role": "assistant",
                "tool_calls": [
                    {"id": tool_call.id, "type": "function", "function": {"name": func_name, "arguments": func_args_str}}
                ],
            }
        )

        try:
            if func_name == "ListTablesArgs":
                parsed = ListTablesArgs.model_validate_json(func_args_str)
                result = list_tables(reasoning=parsed.reasoning)
            elif func_name == "DescribeTableArgs":
                parsed = DescribeTableArgs.model_validate_json(func_args_str)
                result = describe_table(reasoning=parsed.reasoning, table_name=parsed.table_name)
            elif func_name == "SampleTableArgs":
                parsed = SampleTableArgs.model_validate_json(func_args_str)
                result = sample_table(
                    reasoning=parsed.reasoning, table_name=parsed.table_name, row_sample_size=parsed.row_sample_size
                )
            elif func_name == "RunTestSQLQuery":
                parsed = RunTestSQLQuery.model_validate_json(func_args_str)
                result = run_test_sql_query(reasoning=parsed.reasoning, sql_query=parsed.sql_query)
            elif func_name == "RunFinalSQLQuery":
                parsed = RunFinalSQLQuery.model_validate_json(func_args_str)
                result = run_final_sql_query(reasoning=parsed.reasoning, sql_query=parsed.sql_query)
                console.print("\n[green]── FINAL RESULT ──[/green]")
                console.print(result)
                final_result = result
                final_query = parsed.sql_query
                final_reasoning = parsed.reasoning
                messages.append(
                    {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps({"result": str(result)})}
                )
                transcript.append({"role": "tool", "name": func_name, "content": result})
                break
            else:
                raise ValueError(f"unknown tool: {func_name}")
        except (ValidationError, Exception) as e:
            err = f"tool {func_name} validation/exec failed: {e}"
            console.print(f"[red]{err}[/red]")
            messages.append(
                {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps({"error": err})}
            )
            transcript.append({"role": "tool", "name": func_name, "error": err})
            continue

        messages.append(
            {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps({"result": str(result)})}
        )
        transcript.append({"role": "tool", "name": func_name, "content": result})

    elapsed = time.time() - started_at

    ok = error is None and final_result is not None
    marker = {
        "ok": ok,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "model": args.model,
        "base_url": args.base_url,
        "db_path": DB_PATH,
        "prompt": args.prompt,
        "compute_iterations": iteration if 'iteration' in dir() else 0,
        "elapsed_seconds": round(elapsed, 2),
        "final_query": final_query,
        "final_reasoning": final_reasoning,
        "final_result_preview": (final_result or "")[:1000] if final_result else None,
        "error": error,
    }

    marker_path = write_marker(marker)
    session_path = write_session({**marker, "transcript": transcript}, name=args.session_tag)

    console.print(f"\n[bold]marker[/bold] → {marker_path}")
    console.print(f"[bold]session[/bold] → {session_path}")
    console.print(
        f"\n[{'green' if ok else 'red'}]ok={ok}  iters={marker['compute_iterations']}  "
        f"elapsed={marker['elapsed_seconds']}s  model={args.model}[/]"
    )

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
