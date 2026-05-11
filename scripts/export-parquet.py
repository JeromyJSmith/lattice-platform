#!/usr/bin/env python3
"""Export every `lattice/bridge/*` table to Parquet under public/data/.

Tracked in meta/FEATURE_BACKLOG.md § DATA LAYER (Pixeltable / sidecar) →
"Parquet export endpoint" and § DATA LAYER — DuckDB WASM → "Parquet pipeline".

Usage:
    python3 scripts/export-parquet.py [--out public/data]

Stub. Acceptance criteria + full sidecar endpoint design are on the
matching GitHub issues.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO_ROOT / "public" / "data"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    p.add_argument("--scope", default="lattice/bridge",
                   help="Pixeltable namespace prefix to export (default: lattice/bridge)")
    args = p.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    print(f"STUB: would export {args.scope}/* to {args.out}/", file=sys.stderr)
    print("  Implementation outline:", file=sys.stderr)
    print(f"  1. pxt.list_tables('{args.scope}', recursive=True)", file=sys.stderr)
    print("  2. For each table: pxt.get_table(path).to_pandas().to_parquet(out / f'{path.replace(\"/\", \"_\")}.parquet')",
          file=sys.stderr)
    print("  3. Write a manifest.json with table -> parquet path + row count + schema hash", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
