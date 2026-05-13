#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "openai>=1.63.0",
#   "rich>=13.7.0",
#   "pydantic>=2.0.0",
# ]
# ///
"""sfa_in_tab_bonsai_v1.py — drive an in-tab WebGPU Bonsai from a server SFA.

Composition:
  driver model       bonsai-8b on llama-swap (text + tool calls)
  in-tab model       onnx-community/Ternary-Bonsai-1.7B-ONNX
                     loaded via transformers.js in a Chrome tab
                     attached to browser-harness
  bridge             browser-harness js() — driver-side Python calls
                     `await window.bonsai.generate(prompt)` inside the tab
  host page          meta/harness/in-tab-llm/bonsai-host.html
  static server      meta/harness/in-tab-llm/serve.py
                     127.0.0.1:8765 (auto-started by this SFA)

The driver model never sees the in-tab model's weights or output tokens
directly. It picks BootInTabBonsai once, then issues
RunInBrowserLLM(prompt) for any number of follow-up generations. Each
call returns a string — the in-tab model's generated_text — exactly the
same shape the driver gets from any other tool.

Lineage
-------
  - sfa_browser_bonsai_v1.py    (compute loop, fallback parser, browser-harness wrapper)
  - PrismML Ternary Bonsai 8B   (driver model)
  - onnx-community/Ternary-Bonsai-1.7B-ONNX  (in-tab model)
  - transformers.js v3+          (loader + WebGPU device)
  - browser-use/browser-harness  (CDP + js() wrapper)
  - mostlygeek/llama-swap        (driver model serving)

Status: PRE-CAPABILITY. Lives in meta/harness/tools/sfa-eval/ until its
proof_evidence lands in analysis/capabilities/transformersjs-capability-registry.yaml
and the relevant rows are promoted DEFERRED → ACTIVE.

Usage
-----
    # llama-swap must be reachable (https://llm.localhost or :9090).
    uv run meta/harness/tools/sfa-eval/sfa_in_tab_bonsai_v1.py \\
        --prompt "Ask the in-tab Bonsai: write a one-line haiku about Pixeltable." \\
        --session-tag haiku

    # Manual host-page test (no SFA), useful for debugging:
    uv run meta/harness/in-tab-llm/serve.py
    # then in Chrome:  http://127.0.0.1:8765/bonsai-host.html
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import signal
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
# _HERE = meta/harness/tools/sfa-eval — 4 levels deep from repo root.
_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent.parent.parent.parent
_HOST_DIR = _REPO / "meta" / "harness" / "in-tab-llm"
_SERVE_PY = _HOST_DIR / "serve.py"
_HOST_HTML = _HOST_DIR / "bonsai-host.html"

DEFAULT_HOST_PORT = 8765
DEFAULT_HOST_URL = f"http://127.0.0.1:{DEFAULT_HOST_PORT}/bonsai-host.html"

DEFAULT_DRIVER_MODEL = "bonsai-8b"

_PORTLESS_URL = "https://llm.localhost/v1"
_PORT_URL = "http://localhost:9090/v1"

STATE_DIR = _REPO / "meta" / "harness" / "state"
SESSIONS_DIR = _REPO / "meta" / "harness" / "docs" / "sessions"
MARKER_PATH = STATE_DIR / "_in_tab_bonsai_v1.done.json"

console = Console()
LLM_CLIENT: openai.OpenAI | None = None
SERVE_PROC: subprocess.Popen | None = None


# ── Pydantic tool models ─────────────────────────────────────────────────────


class BootInTabBonsaiArgs(BaseModel):
    """Boot the in-tab Bonsai host. Navigates Chrome to the local host page,
    waits for transformers.js to load the ONNX weights, and reports back.

    Call this once at the start of any session that needs in-tab inference.
    Returns a JSON blob: {status, device, model_id, elapsed_ms, error}.
    """

    reasoning: str = Field(..., description="Why you are booting now.")


class RunInBrowserLLMArgs(BaseModel):
    """Run text-generation inside the user's Chrome tab via WebGPU Bonsai.

    The host page must already be booted (BootInTabBonsai). Each call hits
    `window.bonsai.generate(prompt, opts)` and returns its result.
    """

    reasoning: str = Field(..., description="Why this in-tab generation matters.")
    prompt: str = Field(..., description="The prompt text for the in-tab model.")
    max_new_tokens: int = Field(default=128, description="Cap on new tokens.")


class FinalAnswerArgs(BaseModel):
    """Emit the final answer string and stop."""

    reasoning: str = Field(..., description="Why this answer satisfies the user.")
    answer: str = Field(..., description="Final answer text to return.")


def _build_tools() -> list[dict]:
    """Build the OpenAI tools array from Pydantic models."""
    return [
        pydantic_function_tool(BootInTabBonsaiArgs),
        pydantic_function_tool(RunInBrowserLLMArgs),
        pydantic_function_tool(FinalAnswerArgs),
    ]


_KNOWN_TOOLS = {
    "BootInTabBonsaiArgs",
    "RunInBrowserLLMArgs",
    "FinalAnswerArgs",
}


# ── Qwen-style tool-call fallback parser ────────────────────────────────────


_QWEN_TOOL_RE = re.compile(r"<tool_call>\s*(.*?)\s*</tool_call>", re.DOTALL)
_PLAIN_JSON_TOOL_RE = re.compile(
    r'\{\s*"name"\s*:\s*"(\w+)"\s*,\s*"arguments"\s*:\s*\{.*?\}\s*\}',
    re.DOTALL,
)


class _PseudoToolCall:
    """Synthesises an OpenAI-shaped tool_call from a Qwen <tool_call> block."""

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


# ── Static server lifecycle ─────────────────────────────────────────────────


def start_static_server(port: int) -> subprocess.Popen | None:
    """Spawn serve.py in a subprocess; return the Popen handle or None on fail."""
    if not _SERVE_PY.exists():
        console.print(f"[red]serve.py not found at {_SERVE_PY}[/red]")
        return None
    if not _HOST_HTML.exists():
        console.print(f"[red]bonsai-host.html not found at {_HOST_HTML}[/red]")
        return None
    cmd = ["uv", "run", str(_SERVE_PY), "--port", str(port)]
    console.print(f"[dim]starting static server: {' '.join(cmd)}[/dim]")
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid if hasattr(os, "setsid") else None,
    )
    # Give the server a moment to bind
    for _ in range(20):
        time.sleep(0.1)
        try:
            import urllib.request
            urllib.request.urlopen(f"http://127.0.0.1:{port}/bonsai-host.html", timeout=0.5).read(1)
            console.print(f"[dim]static server reachable on http://127.0.0.1:{port}/[/dim]")
            return proc
        except Exception:
            continue
    console.print("[yellow]static server did not become reachable within 2s[/yellow]")
    return proc


def stop_static_server(proc: subprocess.Popen | None) -> None:
    """Tear down the static server subprocess group."""
    if proc is None:
        return
    try:
        if hasattr(os, "killpg"):
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        else:
            proc.terminate()
        proc.wait(timeout=3)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


# ── Tool implementations ─────────────────────────────────────────────────────


def _browser_harness_py(snippet: str, timeout: int = 60) -> str:
    """Execute a browser-harness python snippet via the `browser-harness -c` CLI."""
    if not shutil.which("browser-harness"):
        return "browser-harness not on PATH — install per ~/browser-harness/install.md"
    try:
        result = subprocess.run(
            ["browser-harness", "-c", snippet],
            capture_output=True, text=True, timeout=timeout, check=False,
        )
        if result.returncode != 0:
            return f"browser-harness error (rc={result.returncode}):\n{result.stderr.strip()[-500:]}"
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return f"browser-harness timed out ({timeout}s)"


def tool_boot_in_tab_bonsai(args: BootInTabBonsaiArgs, host_url: str, boot_timeout_s: int) -> str:
    """Navigate to the host page and poll window.bonsai.status until ready.

    First boot downloads ~hundreds of MB of ONNX weights from HuggingFace
    on demand. Subsequent boots hit the browser cache (~seconds).
    """
    console.print(Panel(
        f"[cyan]BootInTabBonsai[/cyan] [dim]{args.reasoning}[/dim]\n\n"
        f"[yellow]→ {host_url}[/yellow]\n"
        f"[dim]boot timeout: {boot_timeout_s}s[/dim]",
        expand=False,
    ))
    nav_snippet = (
        f"new_tab({json.dumps(host_url)})\n"
        f"wait_for_load()\n"
        f"print(json.dumps(page_info()))"
    )
    nav_result = _browser_harness_py(nav_snippet)
    console.print(f"[dim]navigate: {nav_result[:200]}[/dim]")

    poll_js = (
        "({ status: window.bonsai?.status ?? 'unset', "
        "device: window.bonsai?.device, "
        "model_id: window.bonsai?.model_id, "
        "error: window.bonsai?.error })"
    )
    poll_snippet = f'import json; print(json.dumps(js({json.dumps(poll_js)})))'

    deadline = time.time() + boot_timeout_s
    last_state: dict | None = None
    while time.time() < deadline:
        out = _browser_harness_py(poll_snippet, timeout=20)
        try:
            state = json.loads(out)
        except Exception:
            time.sleep(1.0)
            continue
        last_state = state
        status = state.get("status")
        if status == "ready":
            return json.dumps({"ok": True, "elapsed_to_ready_s": round(time.time() - (deadline - boot_timeout_s), 2), **state})
        if status == "error":
            return json.dumps({"ok": False, **state})
        time.sleep(1.5)
    return json.dumps({"ok": False, "error": f"boot timed out after {boot_timeout_s}s", "last_state": last_state})


def tool_run_in_browser_llm(args: RunInBrowserLLMArgs) -> str:
    """Call window.bonsai.generate(prompt) inside the tab and return its result."""
    console.print(Panel(
        f"[cyan]RunInBrowserLLM[/cyan] [dim]{args.reasoning}[/dim]\n\n"
        f"[yellow]{args.prompt[:200]}{'…' if len(args.prompt) > 200 else ''}[/yellow]\n"
        f"[dim]max_new_tokens={args.max_new_tokens}[/dim]",
        expand=False,
    ))
    payload = {"prompt": args.prompt, "max_new_tokens": args.max_new_tokens}
    # We use Promise.resolve(...).then(JSON.stringify) so js() can return the
    # awaited value back as a JSON-decodable object.
    generate_js = (
        "(async () => {"
        "  if (!window.bonsai || window.bonsai.status !== 'ready') {"
        f"    return {{ ok: false, error: 'bonsai not ready', status: window.bonsai?.status }};"
        "  }"
        f"  const out = await window.bonsai.generate({json.dumps(payload['prompt'])}, "
        f"{{ max_new_tokens: {payload['max_new_tokens']} }});"
        "  return { ok: true, ...out };"
        "})()"
    )
    snippet = f'import json; print(json.dumps(js({json.dumps(generate_js)})))'
    out = _browser_harness_py(snippet, timeout=180)
    return out


# ── Prompt template ──────────────────────────────────────────────────────────


AGENT_PROMPT = """You are an agent that drives an in-tab WebGPU Bonsai model via tool calls.

Your job: satisfy the user's request by orchestrating the in-tab Bonsai. You
choose what to ask it; you do NOT generate the answer yourself when an in-tab
generation is needed.

Available tools:
- BootInTabBonsaiArgs(reasoning)                      — boot the in-tab host page; call ONCE at the start
- RunInBrowserLLMArgs(reasoning, prompt, max_new_tokens?) — run one generation inside the tab
- FinalAnswerArgs(reasoning, answer)                 — emit the answer and stop

Loop discipline:
- First action: BootInTabBonsai. Always.
- After boot returns ok=true, call RunInBrowserLLM with a single focused prompt.
- Inspect the generated_text in the tool result. If it answers the user's question,
  immediately call FinalAnswerArgs with the answer. Do not call the LLM twice
  for the same thing.
- If the boot result has ok=false, do NOT keep generating — call FinalAnswerArgs
  with a clear failure summary.

Be terse. Use the in-tab model for the substantive work, not yourself.

User request:
{{user_request}}
"""


# ── Compute loop scaffolding ─────────────────────────────────────────────────


def write_marker(payload: dict) -> Path:
    """Write the L1→L2 handoff marker."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    MARKER_PATH.write_text(json.dumps(payload, indent=2))
    return MARKER_PATH


def write_session(payload: dict, name: str) -> Path:
    """Write the per-session evidence file under meta/harness/docs/sessions/."""
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")
    path = SESSIONS_DIR / f"{ts}-in-tab-bonsai-{name}.json"
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
    """Entry point: parse args, run the loop, write evidence."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--prompt", "-p", required=True, help="Natural-language task")
    parser.add_argument("--driver-model", default=DEFAULT_DRIVER_MODEL,
                        help=f"Text driver model (default {DEFAULT_DRIVER_MODEL})")
    parser.add_argument("--base-url", default=None,
                        help="Override OpenAI base URL (default: auto-detect)")
    parser.add_argument("--host-port", type=int, default=DEFAULT_HOST_PORT,
                        help=f"Port for the local static server (default {DEFAULT_HOST_PORT})")
    parser.add_argument("--boot-timeout", type=int, default=120,
                        help="Seconds to wait for window.bonsai.status=ready (default 120)")
    parser.add_argument("--compute", type=int, default=6,
                        help="Max compute loops (default 6)")
    parser.add_argument("--session-tag", default="adhoc", help="Session log filename tag")
    parser.add_argument("--no-server", action="store_true",
                        help="Don't start serve.py — assume a server already running")
    args = parser.parse_args()

    global LLM_CLIENT, SERVE_PROC

    base_url = args.base_url or resolve_base_url()
    LLM_CLIENT = openai.OpenAI(base_url=base_url, api_key=os.getenv("OPENAI_API_KEY", "not-needed"))
    host_url = f"http://127.0.0.1:{args.host_port}/bonsai-host.html"

    console.print(
        f"[dim]base_url={base_url}  driver={args.driver_model}  host={host_url}[/dim]"
    )

    if not args.no_server:
        SERVE_PROC = start_static_server(args.host_port)

    tools = _build_tools()
    completed_prompt = AGENT_PROMPT.replace("{{user_request}}", args.prompt)
    messages: list[dict] = [{"role": "user", "content": completed_prompt}]

    transcript: list[dict] = []
    final_answer: str | None = None
    error: str | None = None
    iteration = 0
    started_at = time.time()
    boot_calls = 0
    in_tab_generations = 0

    try:
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

            messages.append({
                "role": "assistant",
                "tool_calls": [
                    {"id": tool_call.id, "type": "function",
                     "function": {"name": func_name, "arguments": func_args_str}}
                ],
            })

            try:
                if func_name == "BootInTabBonsaiArgs":
                    parsed = BootInTabBonsaiArgs.model_validate_json(func_args_str)
                    result = tool_boot_in_tab_bonsai(parsed, host_url, args.boot_timeout)
                    boot_calls += 1
                elif func_name == "RunInBrowserLLMArgs":
                    parsed = RunInBrowserLLMArgs.model_validate_json(func_args_str)
                    result = tool_run_in_browser_llm(parsed)
                    in_tab_generations += 1
                elif func_name == "FinalAnswerArgs":
                    parsed = FinalAnswerArgs.model_validate_json(func_args_str)
                    final_answer = parsed.answer
                    console.print(Panel(f"[green]FINAL ANSWER[/green]\n{parsed.answer}", expand=False))
                    messages.append({
                        "role": "tool", "tool_call_id": tool_call.id,
                        "content": json.dumps({"result": parsed.answer}),
                    })
                    transcript.append({"loop": iteration, "role": "tool", "name": func_name, "content": parsed.answer})
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
    finally:
        if SERVE_PROC is not None:
            stop_static_server(SERVE_PROC)

    elapsed = time.time() - started_at
    ok = error is None and final_answer is not None

    marker = {
        "ok": ok,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "driver_model": args.driver_model,
        "base_url": base_url,
        "host_url": host_url,
        "prompt": args.prompt,
        "compute_iterations": iteration,
        "elapsed_seconds": round(elapsed, 2),
        "boot_calls": boot_calls,
        "in_tab_generations": in_tab_generations,
        "final_answer": final_answer,
        "error": error,
    }
    marker_path = write_marker(marker)
    session_path = write_session({**marker, "transcript": transcript}, name=args.session_tag)

    console.print(f"\n[bold]marker[/bold] → {marker_path}")
    console.print(f"[bold]session[/bold] → {session_path}")
    console.print(
        f"\n[{'green' if ok else 'red'}]ok={ok}  iters={iteration}  "
        f"elapsed={marker['elapsed_seconds']}s  boots={boot_calls}  "
        f"in_tab_gens={in_tab_generations}[/]"
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
