"""Run all numbered migrations in order. Idempotent.

Usage:
    uv run scripts/bootstrap.py             # apply
    uv run scripts/bootstrap.py --dry-run   # report what would change

Honors $PXT_HOME_OVERRIDE for ephemeral test runs.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, cast

# Ensure `migrations` and `scripts` are importable when invoked from any cwd.
_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))

from migrations import load_all  # noqa: E402
from scripts._pxt_env import get_client, resolve_home  # noqa: E402

MigrationModule = Any

# Heavy migrations (e.g. HuggingFace model downloads) that the CI fast lane
# can opt out of via env. The set is keyed on the 4-digit prefix produced
# by `migrations.discover()` (NOT the file stem). Keep entries 4 chars wide.
HEAVY_PREFIXES: tuple[str, ...] = ("0011",)


def _should_skip(mig_id: str, skip_embeddings: bool, only: list[str] | None) -> bool:
    if only and mig_id not in only:
        return True
    if skip_embeddings and any(mig_id.startswith(p) for p in HEAVY_PREFIXES):
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true", help="emit machine-readable summary")
    parser.add_argument(
        "--skip-embeddings",
        action="store_true",
        default=os.environ.get("BRIDGE_SKIP_EMBEDDINGS") == "1",
        help="skip 0011_add_embedding_indices (HF model download); honors $BRIDGE_SKIP_EMBEDDINGS",
    )
    parser.add_argument(
        "--only",
        action="append",
        default=None,
        help="run only the migration ids in this list (repeatable)",
    )
    args = parser.parse_args()

    home = resolve_home()
    pxt = get_client()
    print(f"PIXELTABLE_HOME  = {home}")
    print(f"pixeltable       = {getattr(pxt, '__version__', '?')}")
    print(f"mode             = {'DRY-RUN' if args.dry_run else 'APPLY'}")
    print(f"skip-embeddings  = {args.skip_embeddings}")

    migrations_summary: list[dict[str, Any]] = []
    summary: dict[str, Any] = {
        "home": str(home),
        "skip_embeddings": args.skip_embeddings,
        "migrations": migrations_summary,
    }
    skipped: list[str] = []
    for mig_id, module in load_all():
        module = cast(MigrationModule, module)
        if _should_skip(mig_id, args.skip_embeddings, args.only):
            print(f"SKIP {mig_id} (filtered)")
            skipped.append(mig_id)
            migrations_summary.append({"id": mig_id, "result": {"skipped": True}})
            continue
        result = module.apply(pxt, dry_run=args.dry_run)
        migrations_summary.append({"id": mig_id, "result": result})
    summary["skipped"] = skipped

    if args.json:
        print(json.dumps(summary, default=str, indent=2))
    else:
        print(f"\nDONE. (skipped {len(skipped)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
