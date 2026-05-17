#!/usr/bin/env python3
"""Build a fit-ready authoritative world-point package for Farber-Haines.

This generates a point-pair JSON already shaped for `fit_vw_point_pairs.py`,
with authoritative/project-side coordinates prefilled and `vw_x` / `vw_y`
left blank until matching Vectorworks drawing points are captured.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path("/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge")
PROJECT_DIR = ROOT / "projects" / "farber-haines-2521"
SOURCES_DIR = PROJECT_DIR / "sources"

PARCEL_JSON_PATH = SOURCES_DIR / "boulder_county_parcel_146124100105.json"
PARCEL_GEOJSON_PATH = SOURCES_DIR / "boulder_county_parcel_146124100105.geojson"
CONTROL_CANDIDATES_CSV_PATH = SOURCES_DIR / "farber_haines_control_candidates.csv"
OUT_PATH = SOURCES_DIR / "farber_haines_point_pairs_authoritative_template.json"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object.")
    return data


def load_candidates(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def parcel_points(parcel_json: dict[str, Any], parcel_geojson: dict[str, Any]) -> list[dict[str, Any]]:
    json_features = parcel_json.get("features") or []
    geojson_features = parcel_geojson.get("features") or []
    if not json_features or not geojson_features:
        return []
    project_ring = ((((json_features[0].get("geometry") or {}).get("rings")) or [[]])[0]) or []
    wgs84_ring = ((((geojson_features[0].get("geometry") or {}).get("coordinates")) or [[]])[0]) or []
    if len(project_ring) >= 5:
        project_ring = project_ring[:-1]
    if len(wgs84_ring) >= 5:
        wgs84_ring = wgs84_ring[:-1]

    labels = ["corner_1", "corner_2", "corner_3", "corner_4"]
    rows: list[dict[str, Any]] = []
    for idx, (project_xy, wgs84_xy) in enumerate(zip(project_ring, wgs84_ring)):
        if idx >= len(labels):
            break
        rows.append({
            "point_id": f"parcel_{labels[idx]}",
            "description": f"County parcel polygon vertex {idx + 1}",
            "vw_x": None,
            "vw_y": None,
            "project_x": project_xy[0],
            "project_y": project_xy[1],
            "lat_wgs84": wgs84_xy[1],
            "lon_wgs84": wgs84_xy[0],
            "source_note": "Authoritative parcel corner from Boulder County parcel geometry.",
            "world_source": "county_parcel",
            "selection_priority": 1,
        })
    return rows


def choose_controls(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    def rank(row: dict[str, str]) -> tuple[int, float]:
        source = (row.get("source") or "").strip()
        status = (row.get("status") or "").strip()
        reliability = (row.get("reliability") or "").strip()
        kind = (row.get("kind") or "").strip()
        distance = float(row.get("distance_ft") or 999999)
        if source == "city_benchmark" and status == "FOUND":
            return (0, distance)
        if source == "county_control_bank" and reliability == "A":
            return (1, distance)
        if source == "county_control_bank" and kind == "Bench Mark":
            return (2, distance)
        return (9, distance)

    rows = sorted(rows, key=rank)
    chosen: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        source = (row.get("source") or "").strip()
        point_id = (row.get("id") or "").strip()
        kind = (row.get("kind") or "").strip()
        status = (row.get("status") or "").strip()
        reliability = (row.get("reliability") or "").strip()
        if not point_id or point_id in seen:
            continue
        include = False
        priority = 5
        note = ""
        if source == "city_benchmark" and status == "FOUND":
            include = True
            priority = 2
            note = "City benchmark candidate from live benchmark service."
        elif source == "county_control_bank" and reliability == "A":
            include = True
            priority = 3
            note = "County control candidate with reliability A."
        elif source == "county_control_bank" and kind == "Bench Mark" and len(chosen) < 8:
            include = True
            priority = 4
            note = "County benchmark/control candidate near parcel."
        if not include:
            continue
        seen.add(point_id)
        chosen.append({
            "point_id": point_id,
            "description": (row.get("description") or point_id).strip(),
            "vw_x": None,
            "vw_y": None,
            "project_x": float(row["x_2876_ft"]),
            "project_y": float(row["y_2876_ft"]),
            "lat_wgs84": None,
            "lon_wgs84": None,
            "source_note": note,
            "world_source": source,
            "kind": kind,
            "status": status,
            "reliability": reliability,
            "distance_ft": float(row["distance_ft"]),
            "selection_priority": priority,
        })
    return chosen[:10]


def build_package() -> dict[str, Any]:
    parcel_json = load_json(PARCEL_JSON_PATH)
    parcel_geojson = load_json(PARCEL_GEOJSON_PATH)
    candidates = load_candidates(CONTROL_CANDIDATES_CSV_PATH)
    points = parcel_points(parcel_json, parcel_geojson) + choose_controls(candidates)
    return {
        "_purpose": (
            "Authoritative world-side point-pair package for Farber-Haines. "
            "Fill `vw_x` and `vw_y` with matched Vectorworks drawing coordinates, "
            "then run fit_vw_point_pairs.py."
        ),
        "project_id": "farber-haines-2521",
        "target_crs": {
            "epsg_code": 2231,
            "name": "NAD83 / Colorado North (US survey foot)",
        },
        "sources": {
            "parcel_json": str(PARCEL_JSON_PATH),
            "parcel_geojson": str(PARCEL_GEOJSON_PATH),
            "control_candidates_csv": str(CONTROL_CANDIDATES_CSV_PATH),
        },
        "instructions": [
            "Match captured VW parcel corners, stakes, or benchmark-related loci to these world-side points.",
            "Prefer parcel corners first, then city/county found benchmark/control points.",
            "Leave unmatched rows with null `vw_x` and `vw_y`; fit_vw_point_pairs.py will skip them.",
            "Use at least 3 matched rows, but prefer 4+ with parcel corners plus one or more controls.",
        ],
        "points": points,
    }


def main() -> int:
    package = build_package()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(package, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
