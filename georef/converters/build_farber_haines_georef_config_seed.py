#!/usr/bin/env python3
"""Build a Farber-Haines georef config seed from current known artifacts.

This creates a canonical `georef.config.json`-shaped seed document using:
- provisional WGS84 parcel corners
- current document georef binding artifact
- latest georef dry-run state
- EPSG 2876 CRS WKT

It is intentionally conservative: it records current truth and provisional
boundary/control data, but does not claim the georef is solved.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path("/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge")
GROVE = Path("/Volumes/PixelTable/GROVE_HARNESS/juniper2026")
OUT_PATH = ROOT / "projects" / "farber-haines-2521" / "georef.config.seed.json"

CONTROL_POINTS_PATH = GROVE / "georef" / "control_points_wgs84_provisional.json"
BINDING_PATH = GROVE / "georef" / "document_georef_binding.json"
DRYRUN_PATH = GROVE / "data" / "vw_extract" / "_apply_georef_last_results.json"
WKT_PATH = GROVE / "georef" / "crs" / "epsg_2876.wkt"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} did not contain a JSON object.")
    return data


def polygon_geojson(points: list[dict[str, Any]]) -> dict[str, Any]:
    ring = []
    for point in points:
        ring.append([point["lon_wgs84"], point["lat_wgs84"]])
    if ring and ring[0] != ring[-1]:
        ring.append(ring[0])
    return {
        "type": "Feature",
        "properties": {
            "project_id": "farber-haines-2521",
            "status": "provisional_boundary_from_control_points",
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [ring],
        },
    }


def bbox(points: list[dict[str, Any]]) -> list[float]:
    lons = [float(point["lon_wgs84"]) for point in points]
    lats = [float(point["lat_wgs84"]) for point in points]
    return [min(lons), min(lats), max(lons), max(lats)]


def google_maps_url(lat: float, lon: float) -> str:
    return f"https://www.google.com/maps/@{lat},{lon},20z"


def build_seed() -> dict[str, Any]:
    control = load_json(CONTROL_POINTS_PATH)
    binding = load_json(BINDING_PATH)
    dryrun = load_json(DRYRUN_PATH)
    wkt = WKT_PATH.read_text(encoding="utf-8").strip()

    points = control.get("control_points") or []
    if not isinstance(points, list) or not points:
        raise ValueError("No control points found.")

    target_lat = float(binding.get("target_wgs84_lat") or dryrun["target"]["wgs84_lat"])
    target_lon = float(binding.get("target_wgs84_lon") or dryrun["target"]["wgs84_lon"])
    before = dryrun.get("before_state") or {}

    seed = {
        "$schema": "../../georef/schema/georef.config.schema.json",
        "project": {
            "project_id": "farber-haines-2521",
            "name": "Farber-Haines [2521]",
            "address": "Juniper Avenue project site, Boulder County, Colorado, USA",
            "client_name": "Farber-Haines",
        },
        "coordinate_system": {
            "epsg_code": "EPSG:2231",
            "proj_string": "",
            "wkt_crs": wkt,
            "vertical_datum": "NAVD88",
            "units": "us_survey_feet",
        },
        "origin": {
            "longitude": target_lon,
            "latitude": target_lat,
            "elevation_m": float(dryrun["target"]["elevation_m"]),
            "true_north_degrees": float(dryrun["target"]["angle_to_north_deg"]),
            "google_maps_url": google_maps_url(target_lat, target_lon),
            "what3words": "",
            "plus_code": "",
        },
        "ifc_georef": {
            "ref_latitude": None,
            "ref_longitude": None,
            "ref_elevation": None,
            "placement_matrix": None,
        },
        "vw_internal": {
            "origin_x": float(before.get("user_origin_x") or 0.0),
            "origin_y": float(before.get("user_origin_y") or 0.0),
            "scale": 1.0,
            "rotation_deg": float(before.get("angle_to_north") or 0.0),
            "units": "document_units_review_required",
        },
        "survey": {
            "easting": None,
            "northing": None,
            "elevation_units": "feet",
            "benchmark_elevation_m": float(dryrun["target"]["elevation_m"]),
            "state_plane_zone": "Colorado North FIPS 0501",
            "control_points": points,
            "benchmark_id": binding.get("control_point_id", ""),
            "surveyor_name": "",
            "survey_date": "",
            "survey_file_path": "",
        },
        "site_boundary": {
            "geojson": polygon_geojson(points),
            "wkt_wgs84": "",
            "wkt_project": "",
            "bounding_box": bbox(points),
            "kml_file": "",
            "shapefile": "",
            "geopackage": "",
            "area_m2": None,
        },
        "osm": {
            "node_id": "",
            "way_id": "",
            "relation_id": "",
            "geojson_file": "",
            "last_fetched": "",
        },
        "elevation": {
            "dem_file_path": "",
            "dem_source": "USGS_3DEP",
            "dem_resolution_m": 1.0,
            "min_elevation_m": None,
            "max_elevation_m": None,
        },
        "aerial_imagery": {
            "orthophoto_file_path": "",
            "orthophoto_source": "",
            "orthophoto_resolution_cm": None,
            "orthophoto_date": "",
            "streetview_lat": None,
            "streetview_lon": None,
            "streetview_heading": None,
        },
        "transforms": {
            "vw_to_wgs84": None,
            "wgs84_to_ecef": None,
            "project_to_utm": None,
            "ifc_to_wgs84": None,
        },
        "metadata": {
            "source_priority": ["survey", "ifc", "gps", "google_maps", "osm"],
            "config_version": "1",
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "notes": (
                "Seed generated from provisional parcel-corner control points, "
                "current unresolved binding artifact, and latest dry-run state. "
                "Not a solved georef."
            ),
        },
    }
    return seed


def main() -> int:
    seed = build_seed()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as handle:
        json.dump(seed, handle, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
