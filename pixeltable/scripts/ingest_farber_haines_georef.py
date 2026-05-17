#!/usr/bin/env -S uv run python
"""Ingest the current Farber-Haines georef seed into project_georef."""

from __future__ import annotations

import hashlib
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))

from scripts._pxt_env import get_client  # noqa: E402

PROJECT_ID = "farber-haines-2521"
TABLE_PATH = "lattice/bridge/project_georef"
BINDING_PATH = Path("/Volumes/PixelTable/GROVE_HARNESS/juniper2026/georef/document_georef_binding.json")
CONTROL_POINTS_PATH = Path("/Volumes/PixelTable/GROVE_HARNESS/juniper2026/georef/control_points_wgs84_provisional.json")
CRS_WKT_PATH = Path("/Volumes/PixelTable/GROVE_HARNESS/juniper2026/georef/crs/epsg_2876.wkt")
CONFIG_SEED_PATH = Path("/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/projects/farber-haines-2521/georef.config.seed.json")


def now() -> datetime:
    return datetime.now(timezone.utc)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_boundary(points: list[dict]) -> tuple[str, str, str]:
    ring = [[pt["lon_wgs84"], pt["lat_wgs84"]] for pt in points]
    if ring and ring[0] != ring[-1]:
        ring.append(ring[0])
    coord_text = ", ".join(f"{lon} {lat}" for lon, lat in ring)
    wkt = f"POLYGON(({coord_text}))" if coord_text else ""
    geojson = json.dumps({"type": "Polygon", "coordinates": [ring]}) if ring else ""
    bbox = json.dumps({
        "min_lon": min(pt["lon_wgs84"] for pt in points),
        "max_lon": max(pt["lon_wgs84"] for pt in points),
        "min_lat": min(pt["lat_wgs84"] for pt in points),
        "max_lat": max(pt["lat_wgs84"] for pt in points),
    })
    return wkt, geojson, bbox


def build_row() -> dict[str, object]:
    binding = load_json(BINDING_PATH)
    control_points_doc = load_json(CONTROL_POINTS_PATH)
    config_seed = load_json(CONFIG_SEED_PATH) if CONFIG_SEED_PATH.exists() else {}
    control_points = list((config_seed.get("survey") or {}).get("control_points") or control_points_doc.get("control_points") or [])
    if not control_points:
        raise SystemExit(f"no control_points in {CONTROL_POINTS_PATH}")

    wkt_crs = CRS_WKT_PATH.read_text(encoding="utf-8").strip() if CRS_WKT_PATH.exists() else ""
    site_boundary = config_seed.get("site_boundary") or {}
    origin = config_seed.get("origin") or {}
    survey = config_seed.get("survey") or {}
    metadata = config_seed.get("metadata") or {}
    source_priority = metadata.get("source_priority") or ["survey", "ifc", "osm"]
    boundary_wkt, boundary_geojson, bbox_json = build_boundary(control_points)
    if site_boundary.get("wkt_wgs84"):
        boundary_wkt = str(site_boundary.get("wkt_wgs84") or "")
    if site_boundary.get("geojson"):
        boundary_geojson = json.dumps(site_boundary.get("geojson"))
    if site_boundary.get("bounding_box"):
        bbox = site_boundary.get("bounding_box") or []
        if len(bbox) == 4:
            bbox_json = json.dumps({
                "min_lon": bbox[0],
                "min_lat": bbox[1],
                "max_lon": bbox[2],
                "max_lat": bbox[3],
            })
    longitude = float(origin.get("longitude")) if origin.get("longitude") is not None else sum(pt["lon_wgs84"] for pt in control_points) / len(control_points)
    latitude = float(origin.get("latitude")) if origin.get("latitude") is not None else sum(pt["lat_wgs84"] for pt in control_points) / len(control_points)
    config_hash = hashlib.sha256(
        json.dumps(
            {"binding": binding, "control_points": control_points_doc, "config_seed": config_seed},
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()
    timestamp = now()

    notes = (
        "Farber-Haines provisional georef seed from GROVE parcel corners. "
        "Document binding remains unresolved; blind apply is disallowed until "
        "a control-point solve is completed."
    )

    return {
        "id": uuid.uuid4().hex,
        "project_id": PROJECT_ID,
        "config_file_hash": config_hash,
        "config_version": metadata.get("config_version") or "farber-haines-provisional-v1",
        "source_priority": json.dumps(source_priority),
        "longitude": longitude,
        "latitude": latitude,
        "elevation_m": origin.get("elevation_m"),
        "true_north_degrees": origin.get("true_north_degrees"),
        "epsg_code": str(binding.get("epsg_code") or control_points_doc.get("horizontal_crs") or ""),
        "proj_string": "",
        "wkt_crs": wkt_crs,
        "vertical_datum": str((config_seed.get("coordinate_system") or {}).get("vertical_datum") or ""),
        "units": str((config_seed.get("coordinate_system") or {}).get("units") or "US survey foot"),
        "boundary_wkt_wgs84": boundary_wkt,
        "boundary_wkt_project": str(site_boundary.get("wkt_project") or ""),
        "boundary_geojson": boundary_geojson,
        "bounding_box_json": bbox_json,
        "area_m2": site_boundary.get("area_m2"),
        "survey_easting": survey.get("easting"),
        "survey_northing": survey.get("northing"),
        "survey_elevation_units": None,
        "benchmark_elevation_m": survey.get("benchmark_elevation_m"),
        "state_plane_zone": survey.get("state_plane_zone") or "Colorado Central",
        "control_points_json": json.dumps({"control_points": control_points}),
        "benchmark_id": survey.get("benchmark_id") or "",
        "surveyor_name": "",
        "survey_date": survey.get("survey_date") or "",
        "survey_file_path": survey.get("survey_file_path") or "",
        "ifc_ref_latitude": None,
        "ifc_ref_longitude": None,
        "ifc_ref_elevation": None,
        "ifc_placement_matrix": "",
        "vw_origin_x": None,
        "vw_origin_y": None,
        "vw_scale": None,
        "vw_rotation_deg": None,
        "vw_units": "",
        "osm_node_id": "",
        "osm_way_id": "",
        "osm_relation_id": "",
        "osm_geojson_file": "",
        "osm_last_fetched": "",
        "dem_file_path": "",
        "dem_source": "",
        "dem_resolution_m": None,
        "min_elevation_m": None,
        "max_elevation_m": None,
        "orthophoto_file_path": "",
        "orthophoto_source": "",
        "orthophoto_resolution_cm": None,
        "orthophoto_date": "",
        "transform_vw_to_wgs84": "",
        "transform_wgs84_to_ecef": "",
        "transform_project_to_utm": "",
        "transform_ifc_to_wgs84": "",
        "has_kml": False,
        "has_shapefile": False,
        "has_geopackage": False,
        "has_geotiff_dem": False,
        "has_orthophoto": False,
        "has_survey_csv": False,
        "has_ifc_georef": False,
        "has_osm": False,
        "created_at": timestamp,
        "updated_at": timestamp,
        "notes": str(metadata.get("notes") or notes),
    }


def main() -> int:
    pxt = get_client()
    table = pxt.get_table(TABLE_PATH)
    row = build_row()
    try:
        table.delete(table.project_id == PROJECT_ID)
    except Exception:
        pass
    table.insert([row])
    print(json.dumps({
        "ok": True,
        "table": TABLE_PATH,
        "project_id": PROJECT_ID,
        "config_file_hash": row["config_file_hash"],
        "boundary_seed_points": 4,
    }, default=str, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
