#!/usr/bin/env python3
"""Thin Python API client for a local ComfyUI server.

ComfyUI exposes:
- POST /prompt          submit a workflow
- GET  /history/{id}    fetch outputs once complete
- WS   /ws              live progress updates

Stub. Acceptance criteria on the matching GitHub issue.
"""

from __future__ import annotations

import sys


COMFY_URL = "http://localhost:8188"


def submit(workflow_json: dict) -> str:
    """Return the prompt_id ComfyUI assigns to the submitted workflow."""
    raise NotImplementedError("comfyui submit stub")


def wait_for(prompt_id: str, timeout_s: int = 600) -> dict:
    """Poll /history/{prompt_id} until done; return outputs."""
    raise NotImplementedError("comfyui wait stub")


if __name__ == "__main__":
    print("ComfyUI client stub. See genai/comfyui/README.md.", file=sys.stderr)
    raise SystemExit(2)
