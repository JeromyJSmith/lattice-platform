"""Verify the live Pixeltable matches the contract snapshot.

This is the schema-drift gate. It produces (or compares against) a YAML
snapshot at `pixeltable/.schema-snapshot.yaml` capturing:
  - All owned namespaces (lattice/execution/*, lattice/bridge/*)
  - All tables in those namespaces
  - For each table: column name -> string type repr

Exit codes:
    0 = match
    2 = drift (snapshot != live)
    3 = ownership violation (foreign tables under owned namespace)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))

from migrations._helpers import OWNED_BRIDGE_SUBS, OWNED_PARENTS  # noqa: E402
from scripts._pxt_env import get_client  # noqa: E402

SNAPSHOT_PATH = _HERE.parent / ".schema-snapshot.yaml"

OWNED_NAMESPACES: tuple[str, ...] = (
    "lattice/execution",
    *OWNED_BRIDGE_SUBS,
)

# Per-namespace expected tables come from migrations 0002 and 0004-0010.
EXPECTED: dict[str, list[str]] = {
    "lattice/execution": [
        "agent_threads", "agent_messages", "agent_runs",
        "agent_stream_events", "agent_artifacts", "agent_outcomes",
    ],
    "lattice/bridge/vw":       ["vectorworks_exports"],
    "lattice/bridge/ifc":      ["ifc_elements", "ifc_property_sets"],
    "lattice/bridge/itwin":    ["itwin_sync_jobs", "itwin_changed_elements", "connector_versions"],
    "lattice/bridge/marpa":    ["marpa_parse_runs"],
    "lattice/bridge/semantic": ["semantic_sidecars", "landscape_entities"],
    "lattice/bridge/evidence": ["promotion_events", "harness_run_refs"],
    "lattice/bridge/health":   ["schema_drift_events", "bridge_gap_matrix"],
}


def _columns(t) -> dict[str, str]:
    """Return {column_name: canonical-type-repr} for a Pixeltable table.

    Pixeltable 0.6.0 exposes the authoritative schema via the (private)
    `_get_schema()` method which returns `dict[str, ColumnType]`. The
    `ColumnType.__repr__` is the canonical, version-stable type string
    (e.g. `"String | None"`, `"Int"`, `"Json | None"`), which is exactly
    what the snapshot needs to detect a rename, retype, or drop.

    Public surfaces (`columns`, `describe`) only return names or print to
    stdout, so we don't fall back to them — empty would make CI greenlight
    schema corruption silently.
    """
    raw = None
    getter = getattr(t, "_get_schema", None)
    if callable(getter):
        try:
            raw = getter()
        except Exception:
            raw = None
    if not isinstance(raw, dict):
        return {}
    return {str(k): repr(v) for k, v in raw.items()}


def collect(pxt) -> dict:
    snap: dict = {"namespaces": {}}
    live_dirs = set(pxt.list_dirs())

    for ns in OWNED_NAMESPACES:
        node: dict = {"present": ns in live_dirs, "tables": {}}
        if not node["present"]:
            snap["namespaces"][ns] = node
            continue
        try:
            live_tables = sorted(pxt.list_tables(ns))
        except Exception as exc:
            node["error"] = str(exc)
            snap["namespaces"][ns] = node
            continue
        for full in live_tables:
            name = full.split("/")[-1]
            try:
                t = pxt.get_table(full)
                node["tables"][name] = {"columns": _columns(t)}
            except Exception as exc:
                node["tables"][name] = {"error": str(exc)}
        snap["namespaces"][ns] = node
    return snap


def expected_set() -> set[str]:
    out: set[str] = set()
    for ns, tbls in EXPECTED.items():
        for t in tbls:
            out.add(f"{ns}/{t}")
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write snapshot instead of comparing")
    parser.add_argument("--print", action="store_true", help="print live snapshot")
    args = parser.parse_args()

    pxt = get_client()
    live = collect(pxt)

    # Ownership check: every table under owned namespaces must be in EXPECTED.
    foreign: list[str] = []
    for ns, node in live["namespaces"].items():
        for tbl in (node.get("tables") or {}):
            full = f"{ns}/{tbl}"
            if full not in expected_set():
                foreign.append(full)
    if foreign:
        print("ERROR: foreign tables in owned namespaces:")
        for f in foreign:
            print(f"  - {f}")
        return 3

    # Existence check
    missing: list[str] = []
    for full in sorted(expected_set()):
        ns = "/".join(full.split("/")[:-1])
        name = full.split("/")[-1]
        if name not in (live["namespaces"].get(ns, {}).get("tables") or {}):
            missing.append(full)

    if args.print:
        print(yaml.safe_dump(live, sort_keys=True))

    if args.write:
        SNAPSHOT_PATH.write_text(yaml.safe_dump(live, sort_keys=True))
        print(f"wrote {SNAPSHOT_PATH}")
        return 0

    if missing:
        print("DRIFT: missing tables:")
        for m in missing:
            print(f"  - {m}")
        return 2

    if SNAPSHOT_PATH.exists():
        snap = yaml.safe_load(SNAPSHOT_PATH.read_text())
        if snap != live:
            print(f"DRIFT: live schema does not match {SNAPSHOT_PATH.name}")
            # Emit a unified diff hint for CI logs.
            print("--- snapshot")
            print(yaml.safe_dump(snap, sort_keys=True))
            print("+++ live")
            print(yaml.safe_dump(live, sort_keys=True))
            return 2
        print("OK: live schema matches snapshot")
    else:
        print(f"OK: {len(expected_set())} expected tables present "
              "(no snapshot baseline yet; run with --write to create one)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
