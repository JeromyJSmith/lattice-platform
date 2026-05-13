#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml>=6.0"]
# ///
"""health-report.py — emit a JSON health summary for the meta-harness.

Reads capability registries and gitnexus/graphify tool metadata to produce
a structured report consumed by:
  - mcp-community_detection (gitnexus)
  - mcp-entry_points (gitnexus)
  - cli-stats (graphify)
  - cli-hotspots (graphify)
  - cli-cycles (graphify)
  - optimize-mode-router-skill (infranodus)

Output (stdout): JSON object with keys:
  timestamp, total_rows, by_state, by_registry, tool_versions
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from scripts.registry_parser import parse_registries, summary  # type: ignore[import]

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent


def tool_version(cmd: list[str]) -> str:
    """Return version string for a CLI tool, or 'unknown' if unavailable."""
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True)
        return out.strip().splitlines()[0]
    except Exception:
        return "unknown"


def main() -> None:
    """Emit a JSON health summary for the meta-harness to stdout."""
    rows = parse_registries(REPO_ROOT)
    s = summary(rows)
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_rows": s["total_rows"],
        "by_state": s["by_state"],
        "by_registry": s["by_registry"],
        "advisory_stale_count": len(s["advisory_stale_rows"]),
        "install_evidence_count": len(s["install_evidence_rows"]),
        "tool_versions": {
            "graphify": tool_version(["graphify", "--version"]),
            "gitnexus": tool_version(["gitnexus", "--version"]),
        },
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
