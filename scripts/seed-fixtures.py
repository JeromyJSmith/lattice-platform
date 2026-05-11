#!/usr/bin/env python3
"""Run pixeltable/scripts/load_fixtures.py from the repo root.

Convenience wrapper so anyone can `python3 scripts/seed-fixtures.py` from
either the repo root or inside an editor's task runner.

This delegates — the canonical fixture loader is pixeltable/scripts/load_fixtures.py.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SIDECAR_DIR = REPO_ROOT / "pixeltable"


def main() -> int:
    if not (SIDECAR_DIR / "scripts" / "load_fixtures.py").exists():
        print("error: pixeltable/scripts/load_fixtures.py not found", file=sys.stderr)
        return 1
    env = os.environ.copy()
    env.setdefault("PIXELTABLE_HOME", "/Volumes/PixelTable/.pixeltable")
    return subprocess.call(
        ["uv", "run", "python", "scripts/load_fixtures.py"],
        cwd=SIDECAR_DIR,
        env=env,
    )


if __name__ == "__main__":
    raise SystemExit(main())
