#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["httpx>=0.27", "pyyaml>=6.0"]
# ///
"""build-gap-analysis.py — run InfraNodus gap analysis over LATTICE corpora.

Used by:
  - infranodus / analyze_text  (ingests registry text into graph)
  - infranodus / generate_topical_clusters  (surfaces cluster gaps)

Reads:
  - analysis/capabilities/*.yaml  (flattened into text corpus)
  - meta/harness/GOAL.md          (goals corpus)
  - meta/harness/CURRENT-STATE.md (implementation corpus)

Writes:
  - analysis/infranodus/goal-vs-implementation.diff.json
    (output of InfraNodus difference_between_texts)

Environment:
  INFRANODUS_API_KEY — required. Set in shell rc; inherited by this script.

Usage:
  uv run meta/harness/bootstrap/build-gap-analysis.py
  uv run meta/harness/bootstrap/build-gap-analysis.py --dry
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
OUT_DIR = REPO_ROOT / "analysis" / "infranodus"
OUT_DIR.mkdir(parents=True, exist_ok=True)

DRY = "--dry" in sys.argv


def load_corpus() -> dict[str, str]:
    """Load text corpora for InfraNodus analysis."""
    corpora: dict[str, str] = {}

    # Goals corpus
    goal_path = REPO_ROOT / "meta" / "harness" / "GOAL.md"
    if goal_path.exists():
        corpora["goals"] = goal_path.read_text()

    # Implementation corpus
    state_path = REPO_ROOT / "meta" / "harness" / "CURRENT-STATE.md"
    if state_path.exists():
        corpora["implementation"] = state_path.read_text()

    return corpora


def main() -> None:
    """Run InfraNodus gap analysis and write diff JSON to analysis/infranodus/."""
    api_key = os.environ.get("INFRANODUS_API_KEY", "")
    if not api_key and not DRY:
        print(
            "ERROR: INFRANODUS_API_KEY not set. "
            "Export it in your shell rc and restart.",
            file=sys.stderr,
        )
        sys.exit(1)

    corpora = load_corpus()
    print(f"[build-gap-analysis] loaded {len(corpora)} corpora: {list(corpora)}")

    if DRY:
        print("[build-gap-analysis] dry-run — skipping InfraNodus API calls")
        stub = {
            "dry_run": True,
            "corpora": list(corpora),
            "gaps": [],
            "note": "Run without --dry and with INFRANODUS_API_KEY set to populate.",
        }
        out_path = OUT_DIR / "goal-vs-implementation.diff.json"
        out_path.write_text(json.dumps(stub, indent=2))
        print(f"[build-gap-analysis] stub written to {out_path}")
        return

    # Live path: call InfraNodus via MCP tool (claude -p orchestration) or REST.
    # The MCP path is preferred; this script is the CLI fallback for cron/CI use.
    try:
        import httpx  # type: ignore[import]
    except ImportError:
        print("ERROR: httpx not available — run with uv run", file=sys.stderr)
        sys.exit(1)

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    goals_text = corpora.get("goals", "")
    impl_text = corpora.get("implementation", "")
    if not goals_text or not impl_text:
        print("[build-gap-analysis] WARNING: missing corpus — check GOAL.md / CURRENT-STATE.md")
        return

    # difference_between_texts endpoint
    resp = httpx.post(
        "https://infranodus.com/api/v1/difference",
        headers=headers,
        json={"text1": goals_text, "text2": impl_text},
        timeout=60,
    )
    if resp.status_code != 200:
        print(f"ERROR: InfraNodus API returned {resp.status_code}: {resp.text}", file=sys.stderr)
        sys.exit(1)

    diff = resp.json()
    out_path = OUT_DIR / "goal-vs-implementation.diff.json"
    out_path.write_text(json.dumps(diff, indent=2))
    print(f"[build-gap-analysis] gap analysis written to {out_path}")


if __name__ == "__main__":
    main()
