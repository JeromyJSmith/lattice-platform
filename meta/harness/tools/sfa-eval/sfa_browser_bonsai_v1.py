#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "openai>=1.63.0",
#   "rich>=13.7.0",
#   "pydantic>=2.0.0",
# ]
# ///
"""sfa_browser_bonsai_v1.py — multi-model browser SFA via llama-swap.

One compute loop, multiple models, hot-swapped per tool. The driver model
(bonsai-8b, text) decides what to do next. When it picks DescribeScreenshot,
THIS script transparently swaps to a vision model (qwen3vl-2b) for that ONE
call, then swaps back. Bonsai never knows the swap happened — it just sees
the vision model's text output as a tool result.

The browser tools wrap `browser-harness` (browser-use/browser-harness) —
the harness attaches to the user's already-running Chrome via CDP and
exposes js(), capture_screenshot(), new_tab(), etc.

Capability lineage
------------------
  - disler/single-file-agents  sfa_duckdb_openai_v2.py     (compute loop shape)
  - PrismML Ternary Bonsai 8B  (driver model — text + tool calls)
  - mlx-community Qwen3-VL-2B  (vision model — screenshot description)
  - browser-use/browser-harness                            (CDP + js() wrapper)
  - mostlygeek/llama-swap                                  (model hot-swap)
  - vercel-labs/portless                                   (stable HTTPS subdomain)

Status: PRE-CAPABILITY evaluation. Lives in `meta/harness/tools/sfa-eval/`
until its capability registry rows (in
analysis/capabilities/browser-harness-capability-registry.yaml and
analysis/capabilities/portless-capability-registry.yaml) get promoted
DEFERRED → ACTIVE in the same commit that moves the SFA to its final
harness home with proof_evidence attached.

Usage
-----
    # Prereqs (in separate terminals — see scripts/setup-portless.sh output)
    bash scripts/portless/llm.sh                     # llama-swap @ https://llm.localhost
    # OR plain :9090 if portless not running

    uv run meta/harness/tools/sfa-eval/sfa_browser_bonsai_v1.py \\
        --prompt "Open example.com and tell me the page title." \\
        --session-tag browser-title

    uv run meta/harness/tools/sfa-eval/sfa_browser_bonsai_v1.py \\
        --prompt "Open /tmp/test_geometry.png in a viewer, take a screenshot, \\
                  and tell me what dimensions are shown." \\
        --session-tag vision-swap
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
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

# Prefer portless subdomain; fall back to bare port if portless not running.
_PORTLESS_URL = "https://llm.localhost/v1"
_PORT_URL = "http://localhost:9090/v1"

DEFAULT_DRIVER_MODEL = "bonsai-8b"          # text reasoning + tool calls
DEFAULT_VISION_MODEL = "qwen3vl-2b"         # screenshot description

STATE_DIR = _REPO / "meta" / "harness" / "state"
SESSIONS_DIR = _REPO / "meta" / "harness" / "docs" / "sessions"
SCREENSHOTS_DIR = STATE_DIR / "screenshots"

console = Console()

# Globals set in main()
DB_PATH: str = DEFAULT_DB
VISION_MODEL: str = DEFAULT_VISION_MODEL
LLM_CLIENT: openai.OpenAI | None = None


# ── Pydantic tool models ─────────────────────────────────────────────────────


class QueryDuckDBArgs(BaseModel):
    """Run a SQL query against the local DuckDB cache and return rows as text."""

    reasoning: str = Field(..., description="Why this query is needed")
    sql: str = Field(..., description="The SQL to execute. Read-only or DDL/DML — all run.")


class NavigateArgs(BaseModel):
    """Open a URL in a new browser tab via browser-harness."""

    reasoning: str = Field(..., description="Why this URL is being opened")
    url: str = Field(..., description="The URL to open in a new tab")


class RunInBrowserArgs(BaseModel):
    """Execute a JavaScript expression in the active browser tab via browser-harness.

    The expression's evaluated value is returned as a JSON-stringified string.
    Use to read DOM (e.g. `document.title`), poll page state, or call any
    page-attached JS API (e.g. `await window.bonsai.generate('...')`).
    """

    reasoning: str = Field(..., description="Why this JS is being executed")
    expression: str = Field(..., description="The JavaScript expression to evaluate in the active tab")


class CaptureScreenshotArgs(BaseModel):
    """Capture a PNG screenshot of the active browser tab to disk."""

    reasoning: str = Field(..., description="Why a screenshot is being captured")
    filename: str = Field(..., description="Filename (relative, no path). Saved under meta/harness/state/screenshots/.")


class DescribeScreenshotArgs(BaseModel):
    """Send a screenshot to a vision model and return its text description.

    Internally swaps the LLM endpoint from the driver model to the vision
    model for this one call. The driver model never sees raw pixels — only
    the returned description.
    """

    reasoning: str = Field(..., description="Why this image needs description")
    image_path: str = Field(..., description="Absolute path or filename under meta/harness/state/screenshots/")
    question: str = Field(..., description="What to ask the vision model about the image")


class FinalAnswerArgs(BaseModel):
    """Emit the final answer and end the compute loop."""

    reasoning: str = Field(..., description="Final summary of how the task was completed")
    answer: str = Field(..., description="The user-facing answer text")


def _build_tools() -> list[dict]:
    return [
        pydantic_function_tool(QueryDuckDBArgs),
        pydantic_function_tool(NavigateArgs),
        pydantic_function_tool(RunInBrowserArgs),
        pydantic_function_tool(CaptureScreenshotArgs),
        pydantic_function_tool(DescribeScreenshotArgs),
        pydantic_function_tool(FinalAnswerArgs),
    ]


_KNOWN_TOOLS = {
    "QueryDuckDBArgs",
    "NavigateArgs",
    "RunInBrowserArgs",
    "CaptureScreenshotArgs",
    "DescribeScreenshotArgs",
    "FinalAnswerArgs",
}


# ── Qwen-style tool-call fallback parser (lifted from sfa_duckdb_local_v1) ──

_QWEN_TOOL_RE = re.compile(r"<tool_call>\s*(.*?)\s*</tool_call>", re.DOTALL)
_PLAIN_JSON_TOOL_RE = re.compile(r'\{\s*"name"\s*:\s*"(\w+)"\s*,\s*"arguments"\s*:\s*\{.*?\}\s*\}', re.DOTALL)


class _PseudoToolCall:
    def __init__(self, name: str, arguments: str):
        self.id = f"local-{uuid.uuid4().hex[:8]}"
        self.type = "function"
        self.function = type("F", (), {"name": name, "arguments": arguments})()


def extract_pseudo_tool_calls(content: str | None) -> list[_PseudoToolCall]:
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


# ── Tool implementations ─────────────────────────────────────────────────────


def _duckdb_sh(sql: str) -> str:
    """Run SQL via the duckdb CLI; fall back to python duckdb on missing CLI."""
    try:
        result = subprocess.run(
            ["duckdb", DB_PATH, "-c", sql],
            capture_output=True, text=True, timeout=30, check=False,
        )
        if result.returncode != 0:
            return f"DuckDB error (rc={result.returncode}): {result.stderr.strip()}"
        return result.stdout.strip()
    except FileNotFoundError:
        import duckdb
        con = duckdb.connect(DB_PATH, read_only=False)
        try:
            rows = con.execute(sql).fetchall()
            cols = [d[0] for d in con.description] if con.description else []
            if cols:
                return "\n".join(["\t".join(cols)] + ["\t".join(str(v) for v in r) for r in rows])
            return f"affected {len(rows)} rows"
        finally:
            con.close()


def _browser_harness_py(snippet: str) -> str:
    """Execute a browser-harness python snippet via the `browser-harness -c` CLI.

    The CLI auto-starts the daemon and pre-imports the helpers (`js`,
    `new_tab`, `capture_screenshot`, etc.). Returns whatever the snippet
    prints to stdout.
    """
    if not shutil.which("browser-harness"):
        return "browser-harness not on PATH — install per ~/browser-harness/install.md"
    try:
        result = subprocess.run(
            ["browser-harness", "-c", snippet],
            capture_output=True, text=True, timeout=60, check=False,
        )
        if result.returncode != 0:
            return f"browser-harness error (rc={result.returncode}):\n{result.stderr.strip()[-500:]}"
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "browser-harness timed out (60s)"


def tool_query_duckdb(args: QueryDuckDBArgs) -> str:
    console.print(Panel(f"[cyan]QueryDuckDB[/cyan] [dim]{args.reasoning}[/dim]\n\n[yellow]{args.sql}[/yellow]", expand=False))
    return _duckdb_sh(args.sql)


def tool_navigate(args: NavigateArgs) -> str:
    console.print(Panel(f"[cyan]Navigate[/cyan] [dim]{args.reasoning}[/dim]\n\n[yellow]{args.url}[/yellow]", expand=False))
    snippet = f'new_tab({json.dumps(args.url)}); wait_for_load(); print(json.dumps(page_info()))'
    return _browser_harness_py(snippet)


def tool_run_in_browser(args: RunInBrowserArgs) -> str:
    expr = args.expression.replace('"""', '\\"\\"\\"')
    console.print(Panel(f"[cyan]RunInBrowser[/cyan] [dim]{args.reasoning}[/dim]\n\n[yellow]{args.expression[:200]}[/yellow]", expand=False))
    # `js()` returns the JS value already JSON-stringified by browser-harness
    snippet = f'import json; print(json.dumps(js("""{expr}""")))'
    return _browser_harness_py(snippet)


def tool_capture_screenshot(args: CaptureScreenshotArgs) -> str:
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^a-zA-Z0-9._-]", "_", args.filename)
    if not safe.endswith(".png"):
        safe = safe + ".png"
    path = SCREENSHOTS_DIR / safe
    console.print(Panel(f"[cyan]CaptureScreenshot[/cyan] [dim]{args.reasoning}[/dim]\n\n[yellow]→ {path}[/yellow]", expand=False))
    snippet = f'capture_screenshot({json.dumps(str(path))}); print({json.dumps(str(path))})'
    out = _browser_harness_py(snippet)
    if path.exists():
        return f"saved {path} ({path.stat().st_size} bytes)"
    return f"capture failed or path missing — output: {out[:300]}"


def tool_describe_screenshot(args: DescribeScreenshotArgs) -> str:
    """Hot-swap to vision model for ONE call, then return to driver model.

    The model swap is invisible to the driver model — it just sees a string
    of description text in the tool result.
    """
    # Resolve image path: absolute path or filename in screenshots dir
    p = Path(args.image_path)
    if not p.is_absolute():
        p = SCREENSHOTS_DIR / p.name
    if not p.is_file():
        return f"image not found: {p}"

    console.print(
        Panel(
            f"[magenta]DescribeScreenshot[/magenta] [dim]→ swap to {VISION_MODEL}[/dim]\n"
            f"[dim]{args.reasoning}[/dim]\n\n[yellow]{p}[/yellow]\n\n[cyan]Q: {args.question}[/cyan]",
            expand=False,
        )
    )

    import base64
    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    data_url = f"data:image/png;base64,{b64}" if p.suffix.lower() == ".png" else f"data:image/jpeg;base64,{b64}"

    assert LLM_CLIENT is not None
    try:
        resp = LLM_CLIENT.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": args.question},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                }
            ],
            max_tokens=400,
            timeout=120,
        )
        text = resp.choices[0].message.content or ""
        console.print(f"[magenta]← {VISION_MODEL}:[/magenta] {text[:300]}")
        return text
    except Exception as e:
        return f"vision model error: {type(e).__name__}: {e}"


# ── Prompt template ──────────────────────────────────────────────────────────


AGENT_PROMPT = """<purpose>
You are a senior systems engineer with access to a local DuckDB cache,
a browser tab (via the browser-harness), and a vision model. Answer the
user request using ONLY the function tools provided. Do not produce
free-form prose outside of tool call reasoning fields.
</purpose>

<tools-available>
- QueryDuckDBArgs(reasoning, sql)             — run SQL against meta/harness/state/cache/sfa-eval.duckdb
- NavigateArgs(reasoning, url)                 — open a URL in a new browser tab (returns page_info JSON)
- RunInBrowserArgs(reasoning, expression)     — execute arbitrary JavaScript in the active tab and return its value
- CaptureScreenshotArgs(reasoning, filename)  — save a PNG of the active tab
- DescribeScreenshotArgs(reasoning, image_path, question) — describe an image via a vision model
- FinalAnswerArgs(reasoning, answer)          — emit the answer and stop
</tools-available>

<rules>
- Every call MUST include a non-empty `reasoning` field.
- Budget: maximum 10 tool calls total. Plan accordingly.
- Prefer the lightest tool that gets the job done.
- For browser tasks, NavigateArgs first, then read state via RunInBrowserArgs.
- Only call DescribeScreenshotArgs when you actually need to interpret pixels.
- End with FinalAnswerArgs.
</rules>

<user-request>
{{user_request}}
</user-request>
"""


# ── Main compute loop ────────────────────────────────────────────────────────


def write_marker(payload: dict) -> Path:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    marker = STATE_DIR / "_browser_bonsai_v1.done.json"
    marker.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return marker


def write_session(payload: dict, name: str) -> Path:
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    fname = f"{datetime.now(timezone.utc).strftime('%Y-%m-%d-%H%M%S')}-browser-bonsai-{name}.json"
    path = SESSIONS_DIR / fname
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return path


def resolve_base_url(prefer_portless: bool = True) -> str:
    """Return the OpenAI base URL, preferring the portless subdomain when reachable."""
    if not prefer_portless:
        return _PORT_URL
    # Quick health-check: if portless is up, use it; else fall back to bare port
    import socket
    try:
        # Test hostname resolution + a TCP connect — keep this fast
        import urllib.request
        urllib.request.urlopen(_PORTLESS_URL.rsplit("/v1", 1)[0] + "/v1/models", timeout=1.0).read(1)
        return _PORTLESS_URL
    except Exception:
        return _PORT_URL


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--prompt", "-p", required=True, help="Natural-language task")
    parser.add_argument("--db", default=DEFAULT_DB, help=f"DuckDB cache (default {DEFAULT_DB})")
    parser.add_argument("--driver-model", default=DEFAULT_DRIVER_MODEL, help=f"Text driver (default {DEFAULT_DRIVER_MODEL})")
    parser.add_argument("--vision-model", default=DEFAULT_VISION_MODEL, help=f"Vision model (default {DEFAULT_VISION_MODEL})")
    parser.add_argument("--base-url", default=None, help="Override OpenAI base URL (default: auto-detect portless then port 9090)")
    parser.add_argument("--compute", type=int, default=10, help="Max compute loops (default 10)")
    parser.add_argument("--session-tag", default="adhoc", help="Session log filename tag")
    args = parser.parse_args()

    global DB_PATH, VISION_MODEL, LLM_CLIENT
    DB_PATH = args.db
    VISION_MODEL = args.vision_model
    base_url = args.base_url or resolve_base_url()

    if not Path(DB_PATH).exists():
        console.print(f"[yellow]DuckDB file not found: {DB_PATH}[/yellow]")
        console.print("[yellow]Hint: uv run meta/harness/tools/sfa-eval/sfa_init_caches.py[/yellow]")

    LLM_CLIENT = openai.OpenAI(base_url=base_url, api_key=os.getenv("OPENAI_API_KEY", "not-needed"))
    console.print(f"[dim]base_url={base_url}  driver={args.driver_model}  vision={args.vision_model}[/dim]")

    tools = _build_tools()
    completed_prompt = AGENT_PROMPT.replace("{{user_request}}", args.prompt)
    messages: list[dict] = [{"role": "user", "content": completed_prompt}]

    transcript: list[dict] = []
    final_answer: str | None = None
    error: str | None = None
    started_at = time.time()
    model_swaps = 0

    for iteration in range(1, args.compute + 1):
        console.rule(f"[yellow]Loop {iteration}/{args.compute} — driver={args.driver_model}[/yellow]")
        try:
            response = LLM_CLIENT.chat.completions.create(
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
                console.print(f"[yellow]No tool call in response:[/yellow]\n{(message.content or '')[:400]}")
                error = "model produced neither tool_calls nor a parseable <tool_call> block"
                break

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
            if func_name == "QueryDuckDBArgs":
                parsed = QueryDuckDBArgs.model_validate_json(func_args_str)
                result = tool_query_duckdb(parsed)
            elif func_name == "NavigateArgs":
                parsed = NavigateArgs.model_validate_json(func_args_str)
                result = tool_navigate(parsed)
            elif func_name == "RunInBrowserArgs":
                parsed = RunInBrowserArgs.model_validate_json(func_args_str)
                result = tool_run_in_browser(parsed)
            elif func_name == "CaptureScreenshotArgs":
                parsed = CaptureScreenshotArgs.model_validate_json(func_args_str)
                result = tool_capture_screenshot(parsed)
            elif func_name == "DescribeScreenshotArgs":
                parsed = DescribeScreenshotArgs.model_validate_json(func_args_str)
                result = tool_describe_screenshot(parsed)
                model_swaps += 1
            elif func_name == "FinalAnswerArgs":
                parsed = FinalAnswerArgs.model_validate_json(func_args_str)
                final_answer = parsed.answer
                console.print(Panel(f"[green]FINAL ANSWER[/green]\n{parsed.answer}", expand=False))
                messages.append(
                    {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps({"result": parsed.answer})}
                )
                transcript.append({"loop": iteration, "role": "tool", "name": func_name, "content": parsed.answer})
                break
            else:
                raise ValueError(f"unknown tool: {func_name}")
        except (ValidationError, Exception) as e:
            err = f"tool {func_name} failed: {type(e).__name__}: {e}"
            console.print(f"[red]{err}[/red]")
            messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps({"error": err})})
            transcript.append({"loop": iteration, "role": "tool", "name": func_name, "error": err})
            continue

        messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps({"result": str(result)[:4000]})})
        transcript.append({"loop": iteration, "role": "tool", "name": func_name, "content": str(result)[:1500]})

    elapsed = time.time() - started_at
    ok = error is None and final_answer is not None

    marker = {
        "ok": ok,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "driver_model": args.driver_model,
        "vision_model": args.vision_model,
        "base_url": base_url,
        "prompt": args.prompt,
        "compute_iterations": iteration,
        "elapsed_seconds": round(elapsed, 2),
        "model_swaps": model_swaps,
        "final_answer": final_answer,
        "error": error,
    }
    marker_path = write_marker(marker)
    session_path = write_session({**marker, "transcript": transcript}, name=args.session_tag)

    console.print(f"\n[bold]marker[/bold] → {marker_path}")
    console.print(f"[bold]session[/bold] → {session_path}")
    console.print(
        f"\n[{'green' if ok else 'red'}]ok={ok}  iters={iteration}  "
        f"elapsed={marker['elapsed_seconds']}s  swaps={model_swaps}[/]"
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
