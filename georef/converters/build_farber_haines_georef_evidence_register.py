#!/usr/bin/env python3
"""Build a Farber-Haines georef evidence register seed.

This is not the canonical georef config. It is the broader evidence register
that tracks every source we may use to validate or improve georeferencing:
survey, parcel, OSM, plan overlays, iTwin checks, and future splat assets.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path("/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge")
GROVE = Path("/Volumes/PixelTable/GROVE_HARNESS/juniper2026")
OUT_PATH = ROOT / "projects" / "farber-haines-2521" / "georef.evidence.register.json"

CONTROL_POINTS_PATH = GROVE / "georef" / "control_points_wgs84_provisional.json"
BINDING_PATH = GROVE / "georef" / "document_georef_binding.json"
CONFIG_SEED_PATH = ROOT / "projects" / "farber-haines-2521" / "georef.config.seed.json"
SOURCES_DIR = ROOT / "projects" / "farber-haines-2521" / "sources"
PARCEL_JSON_PATH = SOURCES_DIR / "boulder_county_parcel_146124100105.json"
PARCEL_GEOJSON_PATH = SOURCES_DIR / "boulder_county_parcel_146124100105.geojson"
COUNTY_CONTROL_JSON_PATH = SOURCES_DIR / "boulder_county_control_bank_near_site.json"
CITY_BENCHMARK_JSON_PATH = SOURCES_DIR / "boulder_city_benchmarks_near_site.json"
CONTROL_CANDIDATES_CSV_PATH = SOURCES_DIR / "farber_haines_control_candidates.csv"
AUTHORITATIVE_POINT_PAIR_PATH = SOURCES_DIR / "farber_haines_point_pairs_authoritative_template.json"
WORKING_COPY_VWX = ROOT / "projects" / "vectorworks project files" / "_Farber-Haines [2521]__ESTIMATION_WORKING_COPY__2026-05-16.vwx"
ORIGINAL_VWX = ROOT / "projects" / "vectorworks project files" / "_Farber-Haines [2521].vwx"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} did not contain a JSON object.")
    return data


def maybe_exists(path: Path) -> str:
    return str(path) if path.exists() else ""


def build_register() -> dict[str, Any]:
    control = load_json(CONTROL_POINTS_PATH)
    binding = load_json(BINDING_PATH)
    config_seed = load_json(CONFIG_SEED_PATH) if CONFIG_SEED_PATH.exists() else {}

    return {
        "project_id": "farber-haines-2521",
        "project_name": "Farber-Haines [2521]",
        "updated_at": now_iso(),
        "purpose": (
            "Track every georeference evidence source available for Farber-Haines, "
            "including control, parcel, OSM, overlay, iTwin, and splat references."
        ),
        "vectorworks": {
            "original_vwx": maybe_exists(ORIGINAL_VWX),
            "working_copy_vwx": maybe_exists(WORKING_COPY_VWX),
            "document_binding_status": binding.get("binding_status"),
            "document_allow_apply": binding.get("allow_apply"),
        },
        "core_location": {
            "target_lat_wgs84": binding.get("target_wgs84_lat"),
            "target_lon_wgs84": binding.get("target_wgs84_lon"),
            "epsg_code": binding.get("epsg_code"),
            "elevation_m": config_seed.get("origin", {}).get("elevation_m"),
            "true_north_degrees": config_seed.get("origin", {}).get("true_north_degrees"),
            "google_maps_url": config_seed.get("origin", {}).get("google_maps_url", ""),
        },
        "survey_control": {
            "status": "authoritative_candidates_present" if CONTROL_CANDIDATES_CSV_PATH.exists() else "provisional_seed_present",
            "control_points_path": str(CONTROL_POINTS_PATH),
            "control_point_count": len(control.get("control_points", [])),
            "control_points": control.get("control_points", []),
            "stake_coordinate_source": maybe_exists(CONTROL_CANDIDATES_CSV_PATH),
            "authoritative_point_pair_path": maybe_exists(AUTHORITATIVE_POINT_PAIR_PATH),
            "survey_file_path": "",
            "county_control_json_path": maybe_exists(COUNTY_CONTROL_JSON_PATH),
            "city_benchmark_json_path": maybe_exists(CITY_BENCHMARK_JSON_PATH),
            "notes": "Replace provisional parcel corners with matched VW survey stakes/corners when available; county and city control candidates may already be present.",
        },
        "parcel_boundary": {
            "shapefile_path": "",
            "geojson_path": maybe_exists(PARCEL_GEOJSON_PATH),
            "kml_path": "",
            "geopackage_path": "",
            "county_json_path": maybe_exists(PARCEL_JSON_PATH),
            "county_source_url": "https://maps.bouldercounty.org/arcgis/rest/services/PARCELS/PARCELS_OWNER/FeatureServer/0",
            "notes": "Use county parcel geometry for boundary sanity and fit confirmation.",
        },
        "osm": {
            "status": "candidate_reference",
            "osm_geojson_path": "",
            "osm_node_id": "",
            "osm_way_id": "",
            "osm_relation_id": "",
            "notes": "Useful for parcel sanity and surrounding context, not primary stake truth.",
        },
        "plan_image_overlays": {
            "full_landscape_plan_image": "",
            "planting_plan_image": "",
            "additional_plan_images": [],
            "overlay_target": "iTwin_or_threejs_reference_stack",
            "notes": "Use exported 2D plan images as turn-on/off alignment references over georeferenced context.",
        },
        "itwin_and_threejs": {
            "ifc_probe_path": "/tmp/farber_haines_ifc_probe/farber_haines_probe_20260516T231627Z.ifc",
            "itwin_overlay_status": "planned",
            "threejs_overlay_status": "planned",
            "notes": "Use 2D image overlays and georeferenced model checks to visually confirm orientation and placement.",
        },
        "gaussian_splat": {
            "status": "future_candidate",
            "site_images_path": "",
            "splat_output_path": "",
            "alignment_method": "control_points",
            "notes": "If a current-site splat is generated, align it against the same control-point authority used for the project georef.",
        },
        "config_seed": {
            "path": maybe_exists(CONFIG_SEED_PATH),
        },
    }


def main() -> int:
    register = build_register()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as handle:
        json.dump(register, handle, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
