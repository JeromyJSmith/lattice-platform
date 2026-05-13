#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "openai>=1.63.0",
#   "rich>=13.7.0",
#   "pydantic>=2.0.0",
#   "polars>=1.22.0",
# ]
# ///
"""sfa_polars_local_v1.py — LATTICE port of Disler sfa_polars_csv_agent_openai_v2.py
through the llama-swap local-model pattern.

Capability lineage
------------------
  - disler/single-file-agents  sfa_polars_csv_agent_openai_v2.py
  - PrismML Ternary Bonsai 8B  (driver — text + tool calls)
  - mostlygeek/llama-swap                                  (single OpenAI-compat endpoint)

Tool surface (preserved from Disler):
  ListColumnsArgs(reasoning, csv_path)
  SampleCSVArgs(reasoning, csv_path, row_count)
  RunTestPolarsCodeArgs(reasoning, polars_python_code, csv_path)
  RunFinalPolarsCodeArgs(reasoning, polars_python_code, csv_path, output_file?)   — terminates

What changes from Disler's original:
  - openai.OpenAI() points at llama-swap (auto-detect portless then port 9090)
  - Qwen-style <tool_call>...</tool_call> fallback parser for mlx_lm.server gap
  - Auto-seeds a CSV fixture (the same 8-plant table used by sqlite/duckdb SFAs)
    so the same "tallest plant?" prompt works against all three backends
  - Writes marker JSON + session JSON per LATTICE marker contract

Status: PRE-CAPABILITY evaluation. On successful proof, promote the
corresponding row in single-file-agents-capability-registry.yaml.

Usage
-----
    uv run meta/harness/tools/sfa-eval/sfa_polars_local_v1.py \\
        --prompt "What is the tallest plant in the CSV?" \\
        --session-tag tallest-plant

    # Override fixture:
    uv run meta/harness/tools/sfa-eval/sfa_polars_local_v1.py \\
        --csv path/to/your.csv \\
        --prompt "Group by category and show counts"
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

import openai
import polars as pl
from openai import pydantic_function_tool
from pydantic import BaseModel, Field, ValidationError
from rich.console import Console
from rich.panel import Panel


# ── LATTICE config ───────────────────────────────────────────────────────────
_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent.parent.parent.parent

DEFAULT_CSV = str(_REPO / "meta" / "harness" / "state" / "cache" / "plants.csv")
DEFAULT_DRIVER_MODEL = "bonsai-8b"

_PORTLESS_URL = "https://llm.localhost/v1"
_PORT_URL = "http://localhost:9090/v1"

STATE_DIR = _REPO / "meta" / "harness" / "state"
SESSIONS_DIR = _REPO / "meta" / "harness" / "docs" / "sessions"
MARKER_PATH = STATE_DIR / "_polars_local_v1.done.json"
TMP_DIR = STATE_DIR / "tmp"

console = Console()


# ── Pydantic tool models (preserved verbatim from Disler) ────────────────────


class ListColumnsArgs(BaseModel):
    """List the columns of a CSV file."""

    reasoning: str = Field(
        ..., description="Explanation for listing columns relative to the user request"
    )
    csv_path: str = Field(..., description="Path to the CSV file")


class SampleCSVArgs(BaseModel):
    """Return N sample rows from a CSV file."""

    reasoning: str = Field(..., description="Explanation for sampling the CSV data")
    csv_path: str = Field(..., description="Path to the CSV file")
    row_count: int = Field(
        ..., description="Number of rows to sample (aim for 3-5 rows)"
    )


class RunTestPolarsCodeArgs(BaseModel):
    """Execute a test Polars Python snippet against the CSV (only visible to agent)."""

    reasoning: str = Field(..., description="Reason for testing this Polars code")
    polars_python_code: str = Field(..., description="The Polars Python code to test")
    csv_path: str = Field(..., description="Path to the CSV file")


class RunFinalPolarsCodeArgs(BaseModel):
    """Execute the final Polars Python snippet and terminate the loop."""

    reasoning: str = Field(
        ...,
        description="Final explanation of how this code satisfies the user request",
    )
    csv_path: str = Field(..., description="Path to the CSV file")
    polars_python_code: str = Field(
        ..., description="The validated Polars Python code to run"
    )
    output_file: str | None = Field(
        default=None, description="Optional path to save results to"
    )


def _build_tools() -> list[dict]:
    """Build the OpenAI tools array from Pydantic models."""
    return [
        pydantic_function_tool(ListColumnsArgs),
        pydantic_function_tool(SampleCSVArgs),
        pydantic_function_tool(RunTestPolarsCodeArgs),
        pydantic_function_tool(RunFinalPolarsCodeArgs),
    ]


_KNOWN_TOOLS = {
    "ListColumnsArgs",
    "SampleCSVArgs",
    "RunTestPolarsCodeArgs",
    "RunFinalPolarsCodeArgs",
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
    """Scan message.content for Qwen-style <tool_call> blocks and bare JSON."""
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


# ── Auto-seed CSV fixture ─────────────────────────────────────────────────────


def ensure_test_csv(csv_path: str) -> bool:
    """Seed an 8-plant CSV fixture if missing. Returns True if a fresh CSV was written."""
    p = Path(csv_path)
    if p.exists():
        return False
    p.parent.mkdir(parents=True, exist_ok=True)
    df = pl.DataFrame({
        "common_name": [
            "Southern Magnolia", "Live Oak", "Crepe Myrtle", "Azalea",
            "Bermuda Grass", "Saw Palmetto", "Bald Cypress", "Spanish Moss",
        ],
        "latin_name": [
            "Magnolia grandiflora", "Quercus virginiana", "Lagerstroemia indica",
            "Rhododendron canescens", "Cynodon dactylon", "Serenoa repens",
            "Taxodium distichum", "Tillandsia usneoides",
        ],
        "category": [
            "tree", "tree", "shrub", "shrub", "grass", "shrub", "tree", "epiphyte",
        ],
        "mature_height_ft": [80.0, 60.0, 30.0, 8.0, 0.5, 7.0, 100.0, 0.0],
        "native_range": [
            "Southeastern US", "Southeastern US", "South Asia", "Southeastern US",
            "Africa", "Southeastern US", "Southeastern US", "Americas",
        ],
    })
    df.write_csv(str(p))
    return True


# ── Tool implementations (semantics preserved from Disler) ───────────────────


def list_columns(reasoning: str, csv_path: str) -> str:
    """Return the list of column names in the CSV."""
    try:
        df = pl.scan_csv(csv_path).collect()
        cols = df.columns
        console.log(f"[blue]ListColumns[/blue] - Reasoning: {reasoning}")
        return json.dumps(cols)
    except Exception as e:
        console.log(f"[red]Error listing columns: {e}[/red]")
        return str(e)


def sample_csv(reasoning: str, csv_path: str, row_count: int) -> str:
    """Return up to row_count rows of the CSV as CSV-formatted text."""
    try:
        df = pl.scan_csv(csv_path).limit(int(row_count)).collect()
        out = df.write_csv()
        console.log(f"[blue]SampleCSV[/blue] - n={row_count} - Reasoning: {reasoning}")
        return out
    except Exception as e:
        console.log(f"[red]Error sampling CSV: {e}[/red]")
        return str(e)


def _exec_polars_code(polars_python_code: str) -> str:
    """Run a Polars Python snippet in an isolated uv subprocess; return stdout+stderr."""
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    name = f"polars_eval_{uuid.uuid4().hex[:8]}.py"
    path = TMP_DIR / name
    path.write_text(polars_python_code)
    try:
        result = subprocess.run(
            ["uv", "run", "--with", "polars", str(path)],
            text=True, capture_output=True, timeout=60,
        )
        return (result.stdout + result.stderr).strip()
    finally:
        try:
            path.unlink()
        except FileNotFoundError:
            pass


def run_test_polars_code(reasoning: str, polars_python_code: str, csv_path: str) -> str:
    """Execute a test Polars snippet against the CSV path."""
    console.log(f"[blue]TestCode[/blue] - Reasoning: {reasoning}")
    console.log(Panel(polars_python_code[:600], title="test snippet", expand=False))
    return _exec_polars_code(polars_python_code)


def run_final_polars_code(reasoning: str, polars_python_code: str, csv_path: str, output_file: str | None) -> str:
    """Execute the final Polars snippet, return stdout+stderr."""
    console.print(Panel(
        f"[green]FinalCode[/green]\nReasoning: {reasoning}",
        expand=False,
    ))
    out = _exec_polars_code(polars_python_code)
    if output_file:
        try:
            Path(output_file).write_text(out)
        except Exception as e:
            out += f"\n[output_file write failed: {e}]"
    return out


# ── Prompt template (preserved from Disler, with LATTICE tool-name updates) ──


AGENT_PROMPT = """<purpose>
    You are a world-class expert at crafting precise Polars data transformations in Python.
    Your goal is to generate accurate code that exactly matches the user's data analysis needs.
</purpose>

<instructions>
    <instruction>Use the provided tools to explore the CSV data and construct the perfect Polars transformation.</instruction>
    <instruction>Start by listing columns to understand what's available in the CSV.</instruction>
    <instruction>Sample the CSV to see actual data patterns.</instruction>
    <instruction>Test Polars code with RunTestPolarsCodeArgs before finalizing it. Run it as many times as needed to get the code working.</instruction>
    <instruction>Only call RunFinalPolarsCodeArgs when you're confident the code is perfect.</instruction>
    <instruction>If a test errors or doesn't satisfy the user request, fix the code or try a different approach.</instruction>
    <instruction>Think step by step about what information you need.</instruction>
    <instruction>Be sure to specify every parameter for each tool call.</instruction>
    <instruction>Every tool call should have a `reasoning` parameter explaining why.</instruction>
    <instruction>Each Polars code snippet must include `import polars as pl` and end with a `print(...)` so the result is visible.</instruction>
</instructions>

The CSV file is at: {{csv_path}}

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
    path = SESSIONS_DIR / f"{ts}-polars-local-{name}.json"
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
    """Entry point: parse args, ensure CSV, run loop, write evidence."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--csv", default=DEFAULT_CSV,
                        help=f"CSV path (default {DEFAULT_CSV})")
    parser.add_argument("--prompt", "-p", required=True, help="Natural-language task")
    parser.add_argument("--driver-model", default=DEFAULT_DRIVER_MODEL,
                        help=f"Driver model (default {DEFAULT_DRIVER_MODEL})")
    parser.add_argument("--base-url", default=None, help="Override base URL")
    parser.add_argument("--compute", type=int, default=10,
                        help="Max compute loops (default 10)")
    parser.add_argument("--session-tag", default="adhoc", help="Session filename tag")
    args = parser.parse_args()

    csv_path = args.csv
    seeded = ensure_test_csv(csv_path)
    if seeded:
        console.print(f"[dim]auto-seeded CSV fixture → {csv_path}[/dim]")

    base_url = args.base_url or resolve_base_url()
    client = openai.OpenAI(base_url=base_url, api_key=os.getenv("OPENAI_API_KEY", "not-needed"))
    console.print(f"[dim]base_url={base_url}  driver={args.driver_model}  csv={csv_path}[/dim]")

    tools = _build_tools()
    completed_prompt = AGENT_PROMPT.replace("{{user_request}}", args.prompt).replace("{{csv_path}}", csv_path)
    messages: list[dict] = [{"role": "user", "content": completed_prompt}]

    transcript: list[dict] = []
    final_answer: str | None = None
    final_code: str | None = None
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
            if func_name == "ListColumnsArgs":
                parsed = ListColumnsArgs.model_validate_json(func_args_str)
                result = list_columns(parsed.reasoning, parsed.csv_path)
            elif func_name == "SampleCSVArgs":
                parsed = SampleCSVArgs.model_validate_json(func_args_str)
                result = sample_csv(parsed.reasoning, parsed.csv_path, parsed.row_count)
            elif func_name == "RunTestPolarsCodeArgs":
                parsed = RunTestPolarsCodeArgs.model_validate_json(func_args_str)
                result = run_test_polars_code(parsed.reasoning, parsed.polars_python_code, parsed.csv_path)
            elif func_name == "RunFinalPolarsCodeArgs":
                parsed = RunFinalPolarsCodeArgs.model_validate_json(func_args_str)
                result = run_final_polars_code(parsed.reasoning, parsed.polars_python_code, parsed.csv_path, parsed.output_file)
                final_answer = result
                final_code = parsed.polars_python_code
                messages.append({
                    "role": "tool", "tool_call_id": tool_call.id,
                    "content": json.dumps({"result": result}),
                })
                transcript.append({"loop": iteration, "role": "tool", "name": func_name,
                                   "code": parsed.polars_python_code, "content": str(result)[:1500]})
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
        "csv_path": csv_path,
        "csv_seeded_this_run": seeded,
        "prompt": args.prompt,
        "compute_iterations": iteration,
        "elapsed_seconds": round(elapsed, 2),
        "final_polars_code": final_code,
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
