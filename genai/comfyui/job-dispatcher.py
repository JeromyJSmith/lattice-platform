#!/usr/bin/env python3
"""ComfyUI job dispatcher — drains `lattice/genai/comfyui_jobs` for pending rows.

Mirrors the pattern in pixeltable/service/worker.py: poll, claim, run, write
result back. Each comfyui_jobs row corresponds to one workflow invocation.

Stub. Acceptance criteria on the matching GitHub issue.
"""

from __future__ import annotations

import sys


def claim_pending() -> list[dict]:
    """Return pending comfyui_jobs rows; flip them to 'running'."""
    raise NotImplementedError


def run_job(job: dict) -> dict:
    """Submit to ComfyUI, wait, return output paths."""
    raise NotImplementedError


if __name__ == "__main__":
    print("ComfyUI dispatcher stub. See genai/comfyui/README.md.", file=sys.stderr)
    raise SystemExit(2)
