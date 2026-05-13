#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "openai>=1.63.0",
#   "rich>=13.7.0",
# ]
# ///
"""sfa_meta_prompt_local_v1.py — LATTICE port of Disler sfa_meta_prompt_openai_v1.py.

Capability lineage
------------------
  - disler/single-file-agents  sfa_meta_prompt_openai_v1.py
  - mostlygeek/llama-swap                                  (local-model endpoint)

This is a single-shot prompt-generation SFA — NOT a tool-calling loop.
The driver model reads the META_PROMPT template (preserved verbatim from
Disler) with the user's purpose + instructions + optional sections /
examples / variables substituted in, and emits a structured prompt
template as plain text output. Because there is no tool loop, there is
no need for the Qwen-style fallback parser here.

What changes from Disler's original:
  - openai.OpenAI() points at llama-swap (auto-detect portless then port 9090)
  - Default driver: bonsai-8b. Override with --driver-model for sharper output
    (e.g., qwen3.6-35b or hermes-3-8b for richer instruction-following).
  - Dropped the OpenAI-specific `reasoning_effort="high"` parameter.
  - Writes marker JSON + session JSON per LATTICE marker contract.

Status: PRE-CAPABILITY evaluation.

Usage
-----
    uv run meta/harness/tools/sfa-eval/sfa_meta_prompt_local_v1.py \\
        --purpose "Generate Pixeltable migration files" \\
        --instructions "Use pxt.String for geometry, helpers from migrations._helpers" \\
        --sections "constraints, examples" \\
        --variables "namespace, tables"

    # Or pin a different driver:
    uv run meta/harness/tools/sfa-eval/sfa_meta_prompt_local_v1.py \\
        --purpose "..." --instructions "..." \\
        --driver-model qwen3.6-35b
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import openai
from rich.console import Console
from rich.panel import Panel


# ── LATTICE config ───────────────────────────────────────────────────────────
_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent.parent.parent.parent

DEFAULT_DRIVER_MODEL = "bonsai-8b"

_PORTLESS_URL = "https://llm.localhost/v1"
_PORT_URL = "http://localhost:9090/v1"

STATE_DIR = _REPO / "meta" / "harness" / "state"
SESSIONS_DIR = _REPO / "meta" / "harness" / "docs" / "sessions"
MARKER_PATH = STATE_DIR / "_meta_prompt_local_v1.done.json"

console = Console()


# ── META_PROMPT template (preserved verbatim from Disler) ────────────────────


META_PROMPT = """<purpose>
    You are an expert prompt engineer, capable of creating detailed and effective prompts for language models.
    Your task is to generate a comprehensive prompt based on the user's input structure.
    Follow the instructions closely to generate a new prompt template.
</purpose>

<instructions>
    <instruction>Analyze the user-input carefully, paying attention to the purpose, required sections, and variables.</instruction>
    <instruction>Create a detailed prompt that includes all specified sections and incorporates the provided variables.</instruction>
    <instruction>Use clear and concise language in the generated prompt.</instruction>
    <instruction>Ensure that the generated prompt maintains a logical flow and structure.</instruction>
    <instruction>Include placeholders for variables values in the format [[variable-name]].</instruction>
    <instruction>If a section is plural, create a nested section with three items in the singular form.</instruction>
    <instruction>The key xml blocks are purpose, instructions, sections, examples, user-prompt.</instruction>
    <instruction>Purpose defines the high level goal of the prompt.</instruction>
    <instruction>Instructions are the detailed instructions for the prompt.</instruction>
    <instruction>Sections are arbitrary blocks to include in the prompt.</instruction>
    <instruction>Examples are showcases of what the output should be for the prompt.</instruction>
    <instruction>Variables are placeholders for values to be substituted in the prompt.</instruction>
    <instruction>Not every section is required, but purpose and instructions are typically essential.</instruction>
    <instruction>Use the examples to understand the structure of the output.</instruction>
    <instruction>Your output should be in XML format, mirroring the structure of the examples output.</instruction>
    <instruction>Exclude CDATA sections in your output.</instruction>
    <instruction>Respond exclusively with the desired output, no other text.</instruction>
    <instruction>If the user-input is structured like the input-format, use it as is. If it's not, infer the purpose, sections, and variables from the user-input.</instruction>
    <instruction>The goal is to fill in the blanks and best infer the purpose, instructions, sections, and variables from the user-input. If instructions are given, use them to guide the other xml blocks.</instruction>
    <instruction>Emphasize exact XML structure and nesting. Clearly define which blocks must contain which elements to ensure a well-formed output.</instruction>
    <instruction>Use direct, simple language and avoid unnecessary complexity to make the final prompt easy to understand.</instruction>
    <instruction>After creating the full prompt, perform a final validation to confirm that all placeholders, instructions, and examples are included, properly formatted, and consistent.</instruction>
    <instruction>If examples are not requested, don't create them.</instruction>
    <instruction>If sections are not requested, don't create them.</instruction>
    <instruction>If variables are not requested, just create a section for the user-input.</instruction>
</instructions>

<input-format>
    Purpose: [main purpose of the prompt], Instructions: [list of details of how to generate the output comma sep], Sections: [list of additional sections to include, e.g., examples, user-prompt], Examples: [list of examples of the output for the prompt], Variables: [list of variables to be used in the prompt]
</input-format>

<user-input>
    {{user-input}}
</user-input>
"""


# ── Helpers ──────────────────────────────────────────────────────────────────


def write_marker(payload: dict) -> Path:
    """Write the L1→L2 handoff marker."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    MARKER_PATH.write_text(json.dumps(payload, indent=2))
    return MARKER_PATH


def write_session(payload: dict, name: str) -> Path:
    """Write the per-session evidence file."""
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")
    path = SESSIONS_DIR / f"{ts}-meta-prompt-local-{name}.json"
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


def build_user_input(purpose: str, instructions: str, sections: str, examples: str, variables: str) -> str:
    """Concatenate user-supplied fields into the input-format string Disler expects."""
    parts = [f"Purpose: {purpose}", f"Instructions: {instructions}"]
    if sections:
        parts.append(f"Sections: {sections}")
    if examples:
        parts.append(f"Examples: {examples}")
    if variables:
        parts.append(f"Variables: {variables}")
    return ", ".join(parts)


def main() -> int:
    """Entry point: parse args, call the model once, emit the generated prompt."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--purpose", required=True, help="Main purpose of the prompt")
    parser.add_argument("--instructions", required=True, help="Detailed instructions for the output")
    parser.add_argument("--sections", default="", help="Optional comma-separated section names")
    parser.add_argument("--examples", default="", help="Optional examples directive")
    parser.add_argument("--variables", default="", help="Optional comma-separated variable names")
    parser.add_argument("--driver-model", default=DEFAULT_DRIVER_MODEL,
                        help=f"Driver model (default {DEFAULT_DRIVER_MODEL})")
    parser.add_argument("--base-url", default=None,
                        help="Override base URL (default: auto-detect)")
    parser.add_argument("--max-tokens", type=int, default=2048,
                        help="Max output tokens (default 2048)")
    parser.add_argument("--session-tag", default="adhoc", help="Session filename tag")
    args = parser.parse_args()

    base_url = args.base_url or resolve_base_url()
    client = openai.OpenAI(base_url=base_url, api_key=os.getenv("OPENAI_API_KEY", "not-needed"))
    user_input = build_user_input(
        args.purpose, args.instructions, args.sections, args.examples, args.variables
    )
    prompt = META_PROMPT.replace("{{user-input}}", user_input)

    console.print(f"[dim]base_url={base_url}  driver={args.driver_model}[/dim]")
    console.print(Panel(user_input, title="user-input (concatenated)", expand=False))

    started_at = time.time()
    error: str | None = None
    generated: str | None = None

    try:
        response = client.chat.completions.create(
            model=args.driver_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=args.max_tokens,
            timeout=300,
        )
        generated = response.choices[0].message.content
        if generated:
            generated = generated.strip()
    except Exception as e:
        error = f"chat.completions.create raised: {type(e).__name__}: {e}"
        console.print(f"[red]{error}[/red]")

    elapsed = time.time() - started_at
    ok = error is None and generated is not None and len(generated) > 0

    if ok:
        console.print(Panel(generated, title="generated prompt", expand=False))

    marker = {
        "ok": ok,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "driver_model": args.driver_model,
        "base_url": base_url,
        "purpose": args.purpose,
        "instructions": args.instructions,
        "sections": args.sections,
        "examples": args.examples,
        "variables": args.variables,
        "elapsed_seconds": round(elapsed, 2),
        "generated_chars": len(generated) if generated else 0,
        "error": error,
    }
    marker_path = write_marker(marker)
    session_path = write_session({**marker, "generated_prompt": generated, "user_input": user_input}, name=args.session_tag)

    console.print(f"\n[bold]marker[/bold] → {marker_path}")
    console.print(f"[bold]session[/bold] → {session_path}")
    console.print(
        f"\n[{'green' if ok else 'red'}]ok={ok}  elapsed={marker['elapsed_seconds']}s  "
        f"chars={marker['generated_chars']}[/]"
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
