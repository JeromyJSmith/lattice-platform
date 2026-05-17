#!/usr/bin/env -S uv run --with pyproj python
"""Apply a survey CSV payload into the live Farber-Haines project_georef row."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))
sys.path.insert(0, str(_HERE.parent.parent))

from scripts._pxt_env import get_client  # noqa: E402
from georef.converters.survey_csv_to_georef import survey_csv_to_georef  # noqa: E402


PROJECT_ID = "farber-haines-2521"
TABLE_PATH = "lattice/bridge/project_georef"
DEFAULT_SOURCE_EPSG = "EPSG:2876"


def now() -> datetime:
    return datetime.now(timezone.utc)


def dump_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path")
    parser.add_argument("--source-epsg", default=DEFAULT_SOURCE_EPSG)
    return parser.parse_args()


def fetch_current_row(table: Any) -> dict[str, Any]:
    rows = list(table.where(table.project_id == PROJECT_ID).limit(1).collect())
    if not rows:
        raise SystemExit(f"no project_georef row found for {PROJECT_ID}")
    return rows[0]


def compute_hash(current_hash: str, payload: dict[str, Any]) -> str:
    return hashlib.sha256(
        dump_json({"prior_hash": current_hash, "survey_payload": payload}).encode("utf-8")
    ).hexdigest()


def merge_notes(current_notes: str, csv_path: str, source_epsg: str) -> str:
    extra = (
        f" Survey CSV applied from {csv_path} with source EPSG {source_epsg}. "
        "Survey/stake control now supersedes provisional parcel-corner-only control where overlapping."
    )
    return (current_notes or "").strip() + extra


def main() -> int:
    args = parse_args()
    csv_path = Path(args.csv_path).expanduser().resolve()
    if not csv_path.exists():
        raise SystemExit(f"survey CSV not found: {csv_path}")

    payload = survey_csv_to_georef(str(csv_path), PROJECT_ID, args.source_epsg)

    pxt = get_client()
    table = pxt.get_table(TABLE_PATH)
    current = fetch_current_row(table)
    timestamp = now()

    updated = dict(current)
    updated["id"] = uuid.uuid4().hex
    updated["config_file_hash"] = compute_hash(str(current.get("config_file_hash") or ""), payload)
    updated["config_version"] = "farber-haines-survey-csv-v1"
    updated["survey_easting"] = payload["survey_easting"]
    updated["survey_northing"] = payload["survey_northing"]
    updated["survey_elevation_units"] = payload["survey_elevation_units"]
    updated["benchmark_elevation_m"] = payload["benchmark_elevation_m"]
    updated["state_plane_zone"] = payload["state_plane_zone"]
    updated["control_points_json"] = payload["control_points_json"]
    updated["benchmark_id"] = payload["benchmark_id"]
    updated["surveyor_name"] = payload["surveyor_name"]
    updated["survey_date"] = payload["survey_date"]
    updated["survey_file_path"] = payload["survey_file_path"]
    updated["has_survey_csv"] = bool(payload["has_survey_csv"])
    updated["notes"] = merge_notes(str(current.get("notes") or ""), str(csv_path), args.source_epsg)
    updated["updated_at"] = timestamp

    current_created = current.get("created_at")
    updated["created_at"] = current_created if current_created is not None else timestamp

    table.delete(table.project_id == PROJECT_ID)
    table.insert([updated])
    print(json.dumps({
        "ok": True,
        "table": TABLE_PATH,
        "project_id": PROJECT_ID,
        "config_version": updated["config_version"],
        "survey_file_path": updated["survey_file_path"],
        "benchmark_id": updated["benchmark_id"],
        "control_point_count": len(json.loads(updated["control_points_json"]).get("control_points", [])),
    }, default=str, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
