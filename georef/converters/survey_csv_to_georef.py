#!/usr/bin/env -S uv run --with pyproj python
"""Survey CSV -> project_georef survey/control payload.

Expected minimum columns after normalization:
- point id:        id | point_id | name | label
- easting:         easting | x
- northing:        northing | y

Optional columns:
- elevation_ft / elevation / z
- description / notes
- quality / point_type

The converter preserves projected coordinates, derives WGS84 lat/lon via
pyproj, and returns a payload suitable for merging into `project_georef`.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from pyproj import Transformer


def normalize_header(value: str) -> str:
    return "".join(ch.lower() for ch in (value or "").strip() if ch.isalnum())


def parse_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        return None
    cleaned = "".join(ch for ch in text if ch in "0123456789.-")
    if cleaned in {"", "-", ".", "-."}:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def first_present(row: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in row and row[key] not in (None, ""):
            return row[key]
    return None


def load_rows(csv_path: Path) -> list[dict[str, Any]]:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("CSV is missing a header row.")
        remap = {name: normalize_header(name) for name in reader.fieldnames}
        rows: list[dict[str, Any]] = []
        for raw in reader:
            rows.append({remap[k]: v for k, v in raw.items()})
    return rows


def convert_control_points(rows: list[dict[str, Any]], source_epsg: str) -> list[dict[str, Any]]:
    transformer = Transformer.from_crs(source_epsg, "EPSG:4326", always_xy=True)
    points: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        point_id = str(first_present(row, "id", "pointid", "name", "label") or f"point_{index}").strip()
        easting = parse_float(first_present(row, "easting", "x"))
        northing = parse_float(first_present(row, "northing", "y"))
        if easting is None or northing is None:
            continue
        lon, lat = transformer.transform(easting, northing)
        points.append(
            {
                "control_point_id": point_id,
                "description": str(first_present(row, "description", "notes") or "").strip(),
                "quality_class": str(first_present(row, "quality", "pointtype") or "survey_csv").strip(),
                "confidence": 1.0,
                "easting": easting,
                "northing": northing,
                "elevation_ft": parse_float(first_present(row, "elevationft", "elevation", "z")),
                "lat_wgs84": lat,
                "lon_wgs84": lon,
            }
        )
    if not points:
        raise ValueError("No usable survey control points found in CSV.")
    return points


def survey_csv_to_georef(csv_path: str, project_id: str, source_epsg: str) -> dict[str, Any]:
    path = Path(csv_path)
    rows = load_rows(path)
    control_points = convert_control_points(rows, source_epsg)

    first = control_points[0]
    benchmark_elevation_ft = next(
        (pt["elevation_ft"] for pt in control_points if pt.get("elevation_ft") is not None),
        None,
    )
    benchmark_elevation_m = (
        float(benchmark_elevation_ft) * 0.3048 if benchmark_elevation_ft is not None else None
    )

    return {
        "project_id": project_id,
        "source_epsg": source_epsg,
        "survey_easting": first["easting"],
        "survey_northing": first["northing"],
        "survey_elevation_units": "feet" if benchmark_elevation_ft is not None else "",
        "benchmark_elevation_m": benchmark_elevation_m,
        "state_plane_zone": source_epsg,
        "control_points_json": json.dumps(
            {
                "_origin": f"survey_csv_to_georef:{path}",
                "_status": "survey_control_points",
                "_notes": "Derived from survey CSV and reprojected to WGS84.",
                "source_epsg": source_epsg,
                "control_points": control_points,
            }
        ),
        "benchmark_id": first["control_point_id"],
        "surveyor_name": "",
        "survey_date": "",
        "survey_file_path": str(path),
        "has_survey_csv": True,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path")
    parser.add_argument("project_id")
    parser.add_argument("source_epsg")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = survey_csv_to_georef(args.csv_path, args.project_id, args.source_epsg)
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
