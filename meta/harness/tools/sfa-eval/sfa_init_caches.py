#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "duckdb>=1.0",
# ]
# ///
"""sfa_init_caches.py — bootstrap a DuckDB cache for SFA evaluation.

LATTICE-adapted port of:
    /Volumes/PixelTable/GROVE_HARNESS/juniper2026/harness/init_caches.py

Status: PRE-CAPABILITY evaluation. This SFA lives under
`meta/harness/tools/sfa-eval/` until its capability is confirmed and it earns
placement in the right section harness. See
`analysis/capabilities/grove-harness-capability-registry.yaml` for the
DEFERRED row that this port aims to promote to ACTIVE.

What it does
------------
Creates one DuckDB file (`meta/harness/state/cache/sfa-eval.duckdb`) and
seeds two small tables so the companion `sfa_duckdb_local_v1.py` agent has
something to query:

    plants          — sample landscape architecture row set
    migrations      — every Pixeltable migration on this branch

Idempotent: CREATE TABLE IF NOT EXISTS + INSERT OR REPLACE patterns.

Marker contract
---------------
Writes `meta/harness/state/_init_caches.done.json` with:

    {"ok": true, "timestamp": "...", "duckdb_path": "...",
     "tables": ["plants", "migrations"], "row_counts": {...}}

This is the L1→L2 handoff per SPEC_SFA_PATTERN.md §3.

Usage
-----
    uv run meta/harness/tools/sfa-eval/sfa_init_caches.py
    uv run meta/harness/tools/sfa-eval/sfa_init_caches.py --verify
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import duckdb

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent.parent.parent.parent  # …/<repo>/
STATE_DIR = _REPO / "meta" / "harness" / "state"
CACHE_DIR = STATE_DIR / "cache"
CACHE_DB = CACHE_DIR / "sfa-eval.duckdb"
MARKER = STATE_DIR / "_init_caches.done.json"

MIGRATIONS_DIR = _REPO / "pixeltable" / "migrations"

PLANTS_SEED = [
    # (id,  latin_name,                 common_name,         mature_height_ft, mature_spread_ft, native_to)
    (1, "Quercus virginiana",           "Southern Live Oak",         60,  80, "Southeastern US"),
    (2, "Magnolia grandiflora",         "Southern Magnolia",         80,  40, "Southeastern US"),
    (3, "Lagerstroemia indica",         "Crepe Myrtle",              25,  20, "China"),
    (4, "Acer rubrum",                  "Red Maple",                 60,  40, "Eastern US"),
    (5, "Lavandula angustifolia",       "English Lavender",           2,   3, "Mediterranean"),
    (6, "Hosta plantaginea",            "Fragrant Hosta",             2,   3, "China"),
    (7, "Buxus sempervirens",           "Common Boxwood",            10,  10, "Mediterranean"),
    (8, "Hydrangea macrophylla",        "Bigleaf Hydrangea",          6,   6, "Japan"),
]


def _migration_rows() -> list[tuple[str, str, str]]:
    """List every migration file on this branch.

    Returns [(migration_id, filename, size_bytes_as_str)].
    """
    rows: list[tuple[str, str, str]] = []
    if not MIGRATIONS_DIR.is_dir():
        return rows
    for path in sorted(MIGRATIONS_DIR.glob("0*.py")):
        if path.name.startswith("_"):
            continue
        migration_id = path.stem.split("_", 1)[0]
        rows.append((migration_id, path.name, str(path.stat().st_size)))
    return rows


def init_cache(verbose: bool = True) -> dict:
    """Create the cache DB and seed both tables.

    Returns a dict suitable for the marker JSON.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(CACHE_DB))
    try:
        con.execute("""
            CREATE TABLE IF NOT EXISTS plants (
                id              INTEGER PRIMARY KEY,
                latin_name      VARCHAR NOT NULL,
                common_name     VARCHAR NOT NULL,
                mature_height_ft INTEGER,
                mature_spread_ft INTEGER,
                native_to       VARCHAR
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS migrations (
                migration_id    VARCHAR PRIMARY KEY,
                filename        VARCHAR NOT NULL,
                size_bytes      VARCHAR NOT NULL,
                indexed_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Clear + reseed so this remains idempotent
        con.execute("DELETE FROM plants")
        con.executemany(
            "INSERT INTO plants VALUES (?, ?, ?, ?, ?, ?)",
            PLANTS_SEED,
        )

        mrows = _migration_rows()
        con.execute("DELETE FROM migrations")
        if mrows:
            con.executemany(
                "INSERT INTO migrations(migration_id, filename, size_bytes) VALUES (?, ?, ?)",
                mrows,
            )

        plant_count = con.execute("SELECT COUNT(*) FROM plants").fetchone()[0]
        migration_count = con.execute("SELECT COUNT(*) FROM migrations").fetchone()[0]
    finally:
        con.close()

    result = {
        "ok": True,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "duckdb_path": str(CACHE_DB),
        "tables": ["plants", "migrations"],
        "row_counts": {"plants": plant_count, "migrations": migration_count},
    }

    if verbose:
        print(f"[init_caches] created {CACHE_DB}")
        print(f"[init_caches] plants={plant_count}  migrations={migration_count}")
    return result


def write_marker(payload: dict) -> Path:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    MARKER.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return MARKER


def verify_marker() -> int:
    """Check that the marker exists and matches the canonical shape."""
    if not MARKER.exists():
        print(f"verify: missing marker {MARKER}", file=sys.stderr)
        return 1
    data = json.loads(MARKER.read_text(encoding="utf-8"))
    required = {"ok", "timestamp", "duckdb_path", "tables", "row_counts"}
    missing = required - set(data.keys())
    if missing:
        print(f"verify: marker missing keys: {sorted(missing)}", file=sys.stderr)
        return 1
    if not data["ok"]:
        print("verify: marker has ok=false", file=sys.stderr)
        return 1
    if not Path(data["duckdb_path"]).exists():
        print(f"verify: duckdb file gone: {data['duckdb_path']}", file=sys.stderr)
        return 1
    print(f"verify: OK  tables={data['tables']}  row_counts={data['row_counts']}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--verify", action="store_true", help="Verify the marker only; don't (re)initialize")
    args = parser.parse_args()
    if args.verify:
        return verify_marker()
    payload = init_cache()
    path = write_marker(payload)
    print(f"[init_caches] marker → {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
