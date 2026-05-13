#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pixeltable>=0.6.0"]
# ///
"""bridge-to-proposals.py — read bridge evidence from Pixeltable and write proposal briefs.

Closes InfraNodus Gap 2: "Bridge Integration → Proposal Cycle".

Reads recent activity from:
  - lattice/bridge/ifc_elements    → section vw-itwin
  - lattice/bridge/point_clouds    → section georef
  - lattice/bridge/cloud_comparisons → section georef
  - lattice/execution/briefs       → last-run watermark
  - lattice/execution/tool_calls   → section schema / api

Writes JSON brief files to meta/harness/state/bridge-briefs/ for each section
that has new evidence since the last proposal run. run-autoresearch.sh can
consume these as evidence-triggered proposals.

Degrades gracefully when Pixeltable is unavailable (prints warning, exits 0).

Usage:
  uv run meta/harness/bootstrap/bridge-to-proposals.py          # live run
  uv run meta/harness/bootstrap/bridge-to-proposals.py --dry    # print without writing
  uv run meta/harness/bootstrap/bridge-to-proposals.py --since 2026-05-01
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Set PIXELTABLE_HOME before any pixeltable import.
os.environ.setdefault("PIXELTABLE_HOME", "/Volumes/PixelTable/.pixeltable")

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
BRIEFS_DIR = REPO_ROOT / "meta" / "harness" / "state" / "bridge-briefs"

DRY = "--dry" in sys.argv

# --since <date> support
SINCE_DT: datetime | None = None
for _i, _arg in enumerate(sys.argv):
    if _arg == "--since" and _i + 1 < len(sys.argv):
        try:
            SINCE_DT = datetime.fromisoformat(sys.argv[_i + 1]).replace(tzinfo=timezone.utc)
        except ValueError:
            print(
                f"[bridge-to-proposals] WARNING: invalid --since value '{sys.argv[_i + 1]}' — ignoring",
                file=sys.stderr,
            )
        break


def _now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat()


def _parse_ts(value: Any) -> datetime | None:
    """Parse a Pixeltable timestamp value into a timezone-aware datetime, or None."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value)
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except ValueError:
            return None
    return None


def _ts_col_or_none(row: dict[str, Any], *candidates: str) -> datetime | None:
    """Return the first parseable timestamp from a result row, or None."""
    for col in candidates:
        dt = _parse_ts(row.get(col))
        if dt is not None:
            return dt
    return None


def get_last_proposal_time(pxt: Any) -> datetime | None:
    """Return the timestamp of the most recent brief in lattice/execution/briefs."""
    try:
        t = pxt.get_table("lattice/execution/briefs")
        rows = t.select(t.created_at).order_by(t.created_at, asc=False).limit(1).collect()
        if rows and len(rows) > 0:
            return _parse_ts(rows[0].get("created_at"))
    except Exception:
        pass
    return None


def collect_ifc_evidence(pxt: Any, since: datetime | None) -> dict[str, Any] | None:
    """Return evidence summary for IFC element ingests, or None when table is unavailable."""
    try:
        t = pxt.get_table("lattice/bridge/ifc_elements")
        rows = t.collect()
        if not rows:
            return None

        records = list(rows)
        if since is not None:
            records = [
                r for r in records
                if (_ts := _ts_col_or_none(r, "ingested_at", "created_at", "updated_at")) is not None
                and _ts > since
            ]

        if not records:
            return None

        timestamps = [
            _ts for r in records
            if (_ts := _ts_col_or_none(r, "ingested_at", "created_at", "updated_at")) is not None
        ]
        last_ts = max(timestamps).isoformat() if timestamps else _now_iso()

        return {
            "section": "vw-itwin",
            "trigger": "ifc_ingest",
            "evidence_count": len(records),
            "last_evidence_at": last_ts,
            "proposal_hint": (
                f"{len(records)} new IFC element(s) ingested since last proposal. "
                "Consider promoting ifc-ingest capability rows and reviewing BIS class coverage."
            ),
            "generated_at": _now_iso(),
        }
    except Exception as exc:
        print(f"[bridge-to-proposals] lattice/bridge/ifc_elements unavailable: {exc} — skipping")
        return None


def collect_point_cloud_evidence(pxt: Any, since: datetime | None) -> dict[str, Any] | None:
    """Return evidence summary for point cloud ingests, or None when table is unavailable."""
    try:
        t = pxt.get_table("lattice/bridge/point_clouds")
        rows = t.collect()
        if not rows:
            return None

        records = list(rows)
        if since is not None:
            records = [
                r for r in records
                if (_ts := _ts_col_or_none(r, "ingested_at", "created_at", "processed_at")) is not None
                and _ts > since
            ]

        if not records:
            return None

        timestamps = [
            _ts for r in records
            if (_ts := _ts_col_or_none(r, "ingested_at", "created_at", "processed_at")) is not None
        ]
        last_ts = max(timestamps).isoformat() if timestamps else _now_iso()

        return {
            "section": "georef",
            "trigger": "point_cloud_ingest",
            "evidence_count": len(records),
            "last_evidence_at": last_ts,
            "proposal_hint": (
                f"{len(records)} new point cloud file(s) processed since last proposal. "
                "Consider georef pipeline improvements: reprojection coverage, tile generation, "
                "or PDAL classification accuracy."
            ),
            "generated_at": _now_iso(),
        }
    except Exception as exc:
        print(f"[bridge-to-proposals] lattice/bridge/point_clouds unavailable: {exc} — skipping")
        return None


def collect_comparison_evidence(pxt: Any, since: datetime | None) -> dict[str, Any] | None:
    """Return evidence summary for cloud comparison runs, or None when table is unavailable."""
    try:
        t = pxt.get_table("lattice/bridge/cloud_comparisons")
        rows = t.collect()
        if not rows:
            return None

        records = list(rows)
        if since is not None:
            records = [
                r for r in records
                if (_ts := _ts_col_or_none(r, "run_at", "created_at", "completed_at")) is not None
                and _ts > since
            ]

        if not records:
            return None

        timestamps = [
            _ts for r in records
            if (_ts := _ts_col_or_none(r, "run_at", "created_at", "completed_at")) is not None
        ]
        last_ts = max(timestamps).isoformat() if timestamps else _now_iso()

        return {
            "section": "georef",
            "trigger": "cloud_comparison",
            "evidence_count": len(records),
            "last_evidence_at": last_ts,
            "proposal_hint": (
                f"{len(records)} deviation/comparison run(s) completed since last proposal. "
                "Consider promoting georef accuracy results or expanding C2C distance thresholds."
            ),
            "generated_at": _now_iso(),
        }
    except Exception as exc:
        print(f"[bridge-to-proposals] lattice/bridge/cloud_comparisons unavailable: {exc} — skipping")
        return None


def collect_tool_call_evidence(pxt: Any, since: datetime | None) -> list[dict[str, Any]]:
    """Return evidence summaries from tool call records, split by inferred section."""
    results: list[dict[str, Any]] = []
    try:
        t = pxt.get_table("lattice/execution/tool_calls")
        rows = t.collect()
        if not rows:
            return results

        records = list(rows)
        if since is not None:
            records = [
                r for r in records
                if (_ts := _ts_col_or_none(r, "called_at", "created_at", "timestamp")) is not None
                and _ts > since
            ]

        if not records:
            return results

        # Partition by tool name patterns
        schema_calls = [
            r for r in records
            if "migration" in str(r.get("tool_name", "")).lower()
            or "schema" in str(r.get("tool_name", "")).lower()
        ]
        api_calls = [
            r for r in records
            if "endpoint" in str(r.get("tool_name", "")).lower()
            or "route" in str(r.get("tool_name", "")).lower()
            or "router" in str(r.get("tool_name", "")).lower()
        ]

        now = _now_iso()

        if schema_calls:
            timestamps = [
                _ts for r in schema_calls
                if (_ts := _ts_col_or_none(r, "called_at", "created_at", "timestamp")) is not None
            ]
            last_ts = max(timestamps).isoformat() if timestamps else now
            results.append({
                "section": "schema",
                "trigger": "tool_call_schema",
                "evidence_count": len(schema_calls),
                "last_evidence_at": last_ts,
                "proposal_hint": (
                    f"{len(schema_calls)} schema-related tool call(s) recorded since last proposal. "
                    "Consider reviewing migration trail or promoting new table capability rows."
                ),
                "generated_at": now,
            })

        if api_calls:
            timestamps = [
                _ts for r in api_calls
                if (_ts := _ts_col_or_none(r, "called_at", "created_at", "timestamp")) is not None
            ]
            last_ts = max(timestamps).isoformat() if timestamps else now
            results.append({
                "section": "api",
                "trigger": "tool_call_api",
                "evidence_count": len(api_calls),
                "last_evidence_at": last_ts,
                "proposal_hint": (
                    f"{len(api_calls)} API/routing tool call(s) recorded since last proposal. "
                    "Consider reviewing endpoint coverage or promoting new router capability rows."
                ),
                "generated_at": now,
            })

    except Exception as exc:
        print(f"[bridge-to-proposals] lattice/execution/tool_calls unavailable: {exc} — skipping")

    return results


def merge_georef_briefs(briefs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Merge multiple georef-section briefs into a single combined brief."""
    georef = [b for b in briefs if b.get("section") == "georef"]
    other = [b for b in briefs if b.get("section") != "georef"]

    if len(georef) <= 1:
        return briefs

    total_count = sum(b["evidence_count"] for b in georef)
    triggers = [b["trigger"] for b in georef]
    hints = " ".join(b["proposal_hint"] for b in georef)
    timestamps = [b["last_evidence_at"] for b in georef]
    last_ts = max(timestamps)

    merged: dict[str, Any] = {
        "section": "georef",
        "trigger": "+".join(triggers),
        "evidence_count": total_count,
        "last_evidence_at": last_ts,
        "proposal_hint": hints,
        "generated_at": _now_iso(),
    }
    return other + [merged]


def write_brief(brief: dict[str, Any], output_dir: Path, dry: bool) -> Path:
    """Write a brief JSON file to output_dir; returns the target path."""
    section = brief["section"]
    trigger = brief["trigger"].replace("+", "_")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    filename = f"{section}-{trigger}-{stamp}.json"
    out_path = output_dir / filename

    if dry:
        print(f"[bridge-to-proposals] [dry] would write {out_path}")
        print(json.dumps(brief, indent=2))
    else:
        output_dir.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(brief, indent=2))
        print(f"[bridge-to-proposals] wrote {out_path}")

    return out_path


def main() -> None:
    """Read bridge evidence from Pixeltable and write proposal brief JSON files."""
    try:
        import pixeltable as pxt  # type: ignore[import]
    except Exception as exc:
        print(f"[bridge-to-proposals] Pixeltable unavailable: {exc} — skipping")
        sys.exit(0)

    # Determine the since watermark: CLI override > last proposal run > None
    since: datetime | None = SINCE_DT
    if since is None:
        since = get_last_proposal_time(pxt)
        if since is not None:
            print(f"[bridge-to-proposals] watermark from last proposal run: {since.isoformat()}")
        else:
            print("[bridge-to-proposals] no watermark — scanning all available evidence")

    # Collect evidence from each bridge table
    briefs: list[dict[str, Any]] = []

    ifc_brief = collect_ifc_evidence(pxt, since)
    if ifc_brief:
        briefs.append(ifc_brief)

    pc_brief = collect_point_cloud_evidence(pxt, since)
    if pc_brief:
        briefs.append(pc_brief)

    cmp_brief = collect_comparison_evidence(pxt, since)
    if cmp_brief:
        briefs.append(cmp_brief)

    tool_briefs = collect_tool_call_evidence(pxt, since)
    briefs.extend(tool_briefs)

    # Merge multiple georef briefs into one
    briefs = merge_georef_briefs(briefs)

    if not briefs:
        print("[bridge-to-proposals] no new evidence found — no briefs written")
        return

    print(f"[bridge-to-proposals] {len(briefs)} brief(s) to write:")
    for b in briefs:
        print(f"  section={b['section']} trigger={b['trigger']} evidence_count={b['evidence_count']}")

    written: list[Path] = []
    for brief in briefs:
        path = write_brief(brief, BRIEFS_DIR, dry=DRY)
        written.append(path)

    if DRY:
        print(f"[bridge-to-proposals] dry-run complete — {len(written)} brief(s) would be written")
    else:
        print(f"[bridge-to-proposals] done — {len(written)} brief(s) written to {BRIEFS_DIR}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[bridge-to-proposals] Pixeltable unavailable: {exc} — skipping")
        sys.exit(0)
