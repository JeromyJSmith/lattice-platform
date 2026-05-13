#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "openai>=1.63.0",
#   "rich>=13.7.0",
#   "pydantic>=2.0.0",
# ]
# ///
"""sfa_sqlite_local_v1.py — LATTICE port of Disler sfa_sqlite_openai_v2.py
through the llama-swap local-model pattern.

Capability lineage
------------------
  - disler/single-file-agents  sfa_sqlite_openai_v2.py  (tool surface + agent prompt)
  - PrismML Ternary Bonsai 8B  (driver — text + tool calls)
  - mostlygeek/llama-swap                                  (single OpenAI-compat endpoint)

Tool surface (preserved from Disler):
  ListTablesArgs(reasoning)
  DescribeTableArgs(reasoning, table_name)
  SampleTableArgs(reasoning, table_name, row_sample_size)
  RunTestSQLQuery(reasoning, sql_query)
  RunFinalSQLQuery(reasoning, sql_query)         — terminates the loop

What changes from Disler's original:
  - openai.OpenAI() now points at llama-swap (http://localhost:9090 or
    https://llm.localhost via portless)
  - Adds the Qwen-style <tool_call>...</tool_call> fallback parser
    (mlx_lm.server doesn't translate Qwen-format tool calls into the
    OpenAI tool_calls wire field — Bonsai is Qwen-derived, so this is
    required for tool-calling to work at all)
  - Auto-seeds an 8-plant SQLite test fixture on first run if --db
    target is missing, so this SFA is verifiable out of the box
  - Writes marker JSON + session JSON per the LATTICE marker contract

Status: PRE-CAPABILITY evaluation. Lives in meta/harness/tools/sfa-eval/.
On successful proof, promote the corresponding rows in
analysis/capabilities/single-file-agents-capability-registry.yaml from
DEFERRED → ACTIVE in the same commit that adds proof_evidence.

Usage
-----
    # Auto-seed test DB and ask a question:
    uv run meta/harness/tools/sfa-eval/sfa_sqlite_local_v1.py \\
        --prompt "What is the tallest plant?" \\
        --session-tag tallest-plant

    # Or point at an existing SQLite DB (.db, .sqlite, .bim):
    uv run meta/harness/tools/sfa-eval/sfa_sqlite_local_v1.py \\
        --db path/to/file.bim \\
        --prompt "How many bis_Element rows are there?"
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import openai
from openai import pydantic_function_tool
from pydantic import BaseModel, Field, ValidationError
from rich.console import Console
from rich.panel import Panel


# ── LATTICE config ───────────────────────────────────────────────────────────
_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent.parent.parent.parent

DEFAULT_DB = str(_REPO / "meta" / "harness" / "state" / "cache" / "sfa-eval.sqlite")
DEFAULT_DRIVER_MODEL = "bonsai-8b"

_PORTLESS_URL = "https://llm.localhost/v1"
_PORT_URL = "http://localhost:9090/v1"

STATE_DIR = _REPO / "meta" / "harness" / "state"
SESSIONS_DIR = _REPO / "meta" / "harness" / "docs" / "sessions"
MARKER_PATH = STATE_DIR / "_sqlite_local_v1.done.json"

console = Console()


# ── Pydantic tool models (preserved verbatim from Disler) ────────────────────


class ListTablesArgs(BaseModel):
    """List all tables in the SQLite database."""

    reasoning: str = Field(
        ..., description="Explanation for listing tables relative to the user request"
    )


class DescribeTableArgs(BaseModel):
    """Describe the schema of one named table."""

    reasoning: str = Field(..., description="Reason why the table schema is needed")
    table_name: str = Field(..., description="Name of the table to describe")


class SampleTableArgs(BaseModel):
    """Return N sample rows from a named table."""

    reasoning: str = Field(..., description="Explanation for sampling the table")
    table_name: str = Field(..., description="Name of the table to sample")
    row_sample_size: int = Field(
        ..., description="Number of rows to sample (aim for 3-5 rows)"
    )


class RunTestSQLQuery(BaseModel):
    """Test a SQL query without committing it as the final result."""

    reasoning: str = Field(..., description="Reason for testing this query")
    sql_query: str = Field(..., description="The SQL query to test")


class RunFinalSQLQuery(BaseModel):
    """Emit the final SQL query as the answer and terminate the loop."""

    reasoning: str = Field(
        ...,
        description="Final explanation of how this query satisfies the user request",
    )
    sql_query: str = Field(..., description="The validated SQL query to run")


def _build_tools() -> list[dict]:
    """Build the OpenAI tools array from Pydantic models."""
    return [
        pydantic_function_tool(ListTablesArgs),
        pydantic_function_tool(DescribeTableArgs),
        pydantic_function_tool(SampleTableArgs),
        pydantic_function_tool(RunTestSQLQuery),
        pydantic_function_tool(RunFinalSQLQuery),
    ]


_KNOWN_TOOLS = {
    "ListTablesArgs",
    "DescribeTableArgs",
    "SampleTableArgs",
    "RunTestSQLQuery",
    "RunFinalSQLQuery",
}


# ── Qwen-style tool-call fallback parser ────────────────────────────────────


_QWEN_TOOL_RE = re.compile(r"<tool_call>\s*(.*?)\s*</tool_call>", re.DOTALL)
_PLAIN_JSON_TOOL_RE = re.compile(
    r'\{\s*"name"\s*:\s*"(\w+)"\s*,\s*"arguments"\s*:\s*\{.*?\}\s*\}',
    re.DOTALL,
)


class _PseudoToolCall:
    """OpenAI-shaped tool_call synthesized from a Qwen <tool_call> block."""

    def __init__(self, name: str, arguments: str):
        """Init with the function name and JSON-string arguments."""
        self.id = f"local-{uuid.uuid4().hex[:8]}"
        self.type = "function"
        self.function = type("F", (), {"name": name, "arguments": arguments})()


def extract_pseudo_tool_calls(content: str | None) -> list[_PseudoToolCall]:
    """Scan message.content for Qwen-style <tool_call> blocks and bare JSON.

    mlx_lm.server does not translate <tool_call>...</tool_call> content
    blocks into the OpenAI tool_calls wire field. Bonsai (Qwen-family)
    emits them in content. We parse them out here.
    """
    if not content:
        return []
    calls: list[_PseudoToolCall] = []
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


# ── Auto-seed test fixture ────────────────────────────────────────────────────


def ensure_test_db(db_path: str) -> bool:
    """Auto-seed an 8-plant fixture if the DB is missing.

    Mirrors the DuckDB fixture in sfa_init_caches.py so the same
    "tallest plant?" prompt works against either backend. Returns
    True if a fresh DB was created, False if one already existed.
    """
    p = Path(db_path)
    if p.exists():
        return False
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(p))
    try:
        conn.execute("""
            CREATE TABLE plants (
                id INTEGER PRIMARY KEY,
                common_name TEXT NOT NULL,
                latin_name TEXT NOT NULL,
                category TEXT NOT NULL,
                mature_height_ft REAL,
                native_range TEXT
            )
        """)
        rows = [
            ("Southern Magnolia", "Magnolia grandiflora", "tree", 80.0, "Southeastern US"),
            ("Live Oak", "Quercus virginiana", "tree", 60.0, "Southeastern US"),
            ("Crepe Myrtle", "Lagerstroemia indica", "shrub", 30.0, "South Asia"),
            ("Azalea", "Rhododendron canescens", "shrub", 8.0, "Southeastern US"),
            ("Bermuda Grass", "Cynodon dactylon", "grass", 0.5, "Africa"),
            ("Saw Palmetto", "Serenoa repens", "shrub", 7.0, "Southeastern US"),
            ("Bald Cypress", "Taxodium distichum", "tree", 100.0, "Southeastern US"),
            ("Spanish Moss", "Tillandsia usneoides", "epiphyte", 0.0, "Americas"),
        ]
        conn.executemany(
            "INSERT INTO plants (common_name, latin_name, category, mature_height_ft, native_range) VALUES (?, ?, ?, ?, ?)",
            rows,
        )
        conn.commit()
    finally:
        conn.close()
    return True


# ── Tool implementations (semantics preserved from Disler) ───────────────────


def list_tables(reasoning: str, db_path: str) -> str:
    """Return all table names in the SQLite database."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [r[0] for r in cursor.fetchall()]
        conn.close()
        console.log(f"[blue]ListTables[/blue] - Reasoning: {reasoning}")
        return "\n".join(tables)
    except Exception as e:
        console.log(f"[red]Error listing tables: {e}[/red]")
        return str(e)


def describe_table(reasoning: str, table_name: str, db_path: str) -> str:
    """Return the schema of one named table."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name});")
        cols = cursor.fetchall()
        conn.close()
        out = "\n".join(f"{c[1]}  {c[2]}" + (" NOT NULL" if c[3] else "") for c in cols)
        console.log(f"[blue]DescribeTable[/blue] - {table_name} - Reasoning: {reasoning}")
        return out
    except Exception as e:
        console.log(f"[red]Error describing table: {e}[/red]")
        return str(e)


def sample_table(reasoning: str, table_name: str, row_sample_size: int, db_path: str) -> str:
    """Return up to row_sample_size rows from the named table."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name} LIMIT ?", (int(row_sample_size),))
        rows = cursor.fetchall()
        conn.close()
        console.log(f"[blue]SampleTable[/blue] - {table_name} - n={row_sample_size} - Reasoning: {reasoning}")
        return "\n".join(str(r) for r in rows)
    except Exception as e:
        console.log(f"[red]Error sampling table: {e}[/red]")
        return str(e)


def run_test_sql_query(reasoning: str, sql_query: str, db_path: str) -> str:
    """Execute a test query and return rows (or error string)."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        conn.commit()
        conn.close()
        console.log(f"[blue]TestQuery[/blue] - Reasoning: {reasoning}")
        console.log(f"[dim]Query: {sql_query}[/dim]")
        return "\n".join(str(r) for r in rows)
    except Exception as e:
        console.log(f"[red]Test query error: {e}[/red]")
        return str(e)


def run_final_sql_query(reasoning: str, sql_query: str, db_path: str) -> str:
    """Execute the final query, format result, return to the loop for FinalAnswer-style termination."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        conn.commit()
        conn.close()
        out = "\n".join(str(r) for r in rows)
        console.print(Panel(
            f"[green]FinalQuery[/green]\nReasoning: {reasoning}\nQuery: {sql_query}\n\n{out}",
            expand=False,
        ))
        return out
    except Exception as e:
        console.log(f"[red]Final query error: {e}[/red]")
        return str(e)


# ── Prompt template (preserved from Disler) ──────────────────────────────────


AGENT_PROMPT = """<purpose>
    You are a world-class expert at crafting precise SQLite SQL queries.
    Your goal is to generate accurate queries that exactly match the user's data needs.
</purpose>

<instructions>
    <instruction>Use the provided tools to explore the database and construct the perfect query.</instruction>
    <instruction>Start by listing tables to understand what's available.</instruction>
    <instruction>Describe tables to understand their schema and columns.</instruction>
    <instruction>Sample tables to see actual data patterns.</instruction>
    <instruction>Test queries before finalizing them.</instruction>
    <instruction>Only call RunFinalSQLQuery when you're confident the query is perfect.</instruction>
    <instruction>Be thorough but efficient with tool usage.</instruction>
    <instruction>If a test query errors or doesn't satisfy the user request, try to fix it.</instruction>
    <instruction>Think step by step about what information you need.</instruction>
    <instruction>Be sure to specify every parameter for each tool call.</instruction>
    <instruction>Every tool call should have a `reasoning` parameter explaining why.</instruction>
</instructions>

User request:
{{user_request}}
"""


# ── Loop scaffolding ─────────────────────────────────────────────────────────


def write_marker(payload: dict) -> Path:
    """Write the L1→L2 handoff marker."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    MARKER_PATH.write_text(json.dumps(payload, indent=2))
    return MARKER_PATH


def write_session(payload: dict, name: str) -> Path:
    """Write the per-session evidence file."""
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")
    path = SESSIONS_DIR / f"{ts}-sqlite-local-{name}.json"
    path.write_text(json.dumps(payload, indent=2))
    return path


def resolve_base_url(prefer_portless: bool = True) -> str:
    """Return the OpenAI base URL, preferring portless when reachable."""
    if not prefer_portless:
        return _PORT_URL
    try:
        import urllib.request
        urllib.request.urlopen(
            _PORTLESS_URL.rsplit("/v1", 1)[0] + "/v1/models", timeout=1.0
        ).read(1)
        return _PORTLESS_URL
    except Exception:
        return _PORT_URL


def main() -> int:
    """Entry point: parse args, ensure DB, run loop, write evidence."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--db", default=DEFAULT_DB,
                        help=f"SQLite DB path (default {DEFAULT_DB})")
    parser.add_argument("--prompt", "-p", required=True, help="Natural-language task")
    parser.add_argument("--driver-model", default=DEFAULT_DRIVER_MODEL,
                        help=f"Driver model (default {DEFAULT_DRIVER_MODEL})")
    parser.add_argument("--base-url", default=None,
                        help="Override base URL (default: auto-detect)")
    parser.add_argument("--compute", type=int, default=10,
                        help="Max compute loops (default 10)")
    parser.add_argument("--session-tag", default="adhoc", help="Session filename tag")
    args = parser.parse_args()

    db_path = args.db
    seeded = ensure_test_db(db_path)
    if seeded:
        console.print(f"[dim]auto-seeded SQLite fixture → {db_path}[/dim]")

    base_url = args.base_url or resolve_base_url()
    client = openai.OpenAI(base_url=base_url, api_key=os.getenv("OPENAI_API_KEY", "not-needed"))
    console.print(f"[dim]base_url={base_url}  driver={args.driver_model}  db={db_path}[/dim]")

    tools = _build_tools()
    completed_prompt = AGENT_PROMPT.replace("{{user_request}}", args.prompt)
    messages: list[dict] = [{"role": "user", "content": completed_prompt}]

    transcript: list[dict] = []
    final_answer: str | None = None
    final_query: str | None = None
    error: str | None = None
    iteration = 0
    started_at = time.time()

    for iteration in range(1, args.compute + 1):
        console.rule(f"[yellow]Loop {iteration}/{args.compute} — driver={args.driver_model}[/yellow]")
        try:
            response = client.chat.completions.create(
                model=args.driver_model,
                messages=messages,
                tools=tools,
                tool_choice="required",
                timeout=180,
            )
        except Exception as e:
            error = f"chat.completions.create raised: {type(e).__name__}: {e}"
            console.print(f"[red]{error}[/red]")
            break

        if not response.choices:
            error = "no choices in response"
            break
        message = response.choices[0].message
        transcript.append({
            "loop": iteration,
            "role": "assistant",
            "content": message.content,
            "native_tool_calls": [
                {"id": tc.id, "name": tc.function.name, "arguments": tc.function.arguments}
                for tc in (message.tool_calls or [])
            ],
        })

        local_calls: list[_PseudoToolCall] = []
        if not message.tool_calls:
            local_calls = extract_pseudo_tool_calls(message.content)
            if not local_calls:
                console.print(f"[yellow]No tool call:[/yellow]\n{(message.content or '')[:400]}")
                error = "model produced neither tool_calls nor a parseable <tool_call> block"
                break

        tool_call = message.tool_calls[0] if message.tool_calls else local_calls[0]
        func_name = tool_call.function.name
        func_args_str = tool_call.function.arguments

        messages.append({
            "role": "assistant",
            "tool_calls": [
                {"id": tool_call.id, "type": "function",
                 "function": {"name": func_name, "arguments": func_args_str}}
            ],
        })

        try:
            if func_name == "ListTablesArgs":
                parsed = ListTablesArgs.model_validate_json(func_args_str)
                result = list_tables(parsed.reasoning, db_path)
            elif func_name == "DescribeTableArgs":
                parsed = DescribeTableArgs.model_validate_json(func_args_str)
                result = describe_table(parsed.reasoning, parsed.table_name, db_path)
            elif func_name == "SampleTableArgs":
                parsed = SampleTableArgs.model_validate_json(func_args_str)
                result = sample_table(parsed.reasoning, parsed.table_name, parsed.row_sample_size, db_path)
            elif func_name == "RunTestSQLQuery":
                parsed = RunTestSQLQuery.model_validate_json(func_args_str)
                result = run_test_sql_query(parsed.reasoning, parsed.sql_query, db_path)
            elif func_name == "RunFinalSQLQuery":
                parsed = RunFinalSQLQuery.model_validate_json(func_args_str)
                result = run_final_sql_query(parsed.reasoning, parsed.sql_query, db_path)
                final_answer = result
                final_query = parsed.sql_query
                messages.append({
                    "role": "tool", "tool_call_id": tool_call.id,
                    "content": json.dumps({"result": result}),
                })
                transcript.append({"loop": iteration, "role": "tool", "name": func_name,
                                   "sql": parsed.sql_query, "content": str(result)[:1500]})
                break
            else:
                raise ValueError(f"unknown tool: {func_name}")
        except (ValidationError, Exception) as e:
            err = f"tool {func_name} failed: {type(e).__name__}: {e}"
            console.print(f"[red]{err}[/red]")
            messages.append({"role": "tool", "tool_call_id": tool_call.id,
                             "content": json.dumps({"error": err})})
            transcript.append({"loop": iteration, "role": "tool", "name": func_name, "error": err})
            continue

        messages.append({"role": "tool", "tool_call_id": tool_call.id,
                         "content": json.dumps({"result": str(result)[:4000]})})
        transcript.append({"loop": iteration, "role": "tool", "name": func_name,
                           "content": str(result)[:1500]})

    elapsed = time.time() - started_at
    ok = error is None and final_answer is not None

    marker = {
        "ok": ok,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "driver_model": args.driver_model,
        "base_url": base_url,
        "db_path": db_path,
        "db_seeded_this_run": seeded,
        "prompt": args.prompt,
        "compute_iterations": iteration,
        "elapsed_seconds": round(elapsed, 2),
        "final_sql_query": final_query,
        "final_answer": final_answer,
        "error": error,
    }
    marker_path = write_marker(marker)
    session_path = write_session({**marker, "transcript": transcript}, name=args.session_tag)

    console.print(f"\n[bold]marker[/bold] → {marker_path}")
    console.print(f"[bold]session[/bold] → {session_path}")
    console.print(
        f"\n[{'green' if ok else 'red'}]ok={ok}  iters={iteration}  "
        f"elapsed={marker['elapsed_seconds']}s[/]"
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
