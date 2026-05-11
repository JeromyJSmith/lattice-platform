#!/usr/bin/env python3
"""LATTICE LLM router — picks between `claude -p` and local Ollama models per task.

Routing policy (default):
- "complex_aec_reasoning"   -> claude -p   (Claude Max, no API key)
- "structured_code_output"  -> qwen2.5-coder:32b (Ollama, local)
- "fast_classify"           -> mistral-nemo:12b  (Ollama, local)
- "embed_text"              -> nomic-embed-text  (Ollama, local)
- otherwise                 -> claude -p

Reads `lattice/genai/model_registry` for live availability. Stub — full
implementation is tracked in meta/FEATURE_BACKLOG.md § LOCAL AI / GENAI.
"""

from __future__ import annotations

import argparse
import sys


def route(task_type: str) -> dict:
    raise NotImplementedError(
        "model-router stub. Acceptance criteria on the matching GitHub issue."
    )


def sync_registry() -> int:
    """Probe `ollama list` and upsert every model into lattice/genai/model_registry."""
    raise NotImplementedError("registry sync stub")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--sync-registry", action="store_true")
    p.add_argument("--task", default="complex_aec_reasoning")
    args = p.parse_args()
    if args.sync_registry:
        return sync_registry()
    print(route(args.task))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
