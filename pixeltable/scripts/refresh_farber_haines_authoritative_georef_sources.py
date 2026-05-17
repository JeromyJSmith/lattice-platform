#!/usr/bin/env -S uv run python
"""Fetch authoritative Farber-Haines parcel and control-source artifacts."""

from __future__ import annotations

import csv
import json
import math
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path("/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge")
PROJECT_DIR = ROOT / "projects" / "farber-haines-2521"
SOURCES_DIR = PROJECT_DIR / "sources"
SEED_PATH = PROJECT_DIR / "georef.config.seed.json"

PARCEL_NO = "146124100105"
ACCOUNT_NO = "R0005342"
SITE_RADIUS_FT = 2000

COUNTY_PARCEL_LAYER = "https://maps.bouldercounty.org/arcgis/rest/services/PARCELS/PARCELS_OWNER/FeatureServer/0/query"
COUNTY_CONTROL_LAYER = "https://services3.arcgis.com/0jWpHMuhmHsukKE3/arcgis/rest/services/Control_Bank_Points/FeatureServer/0/query"
CITY_BENCHMARK_LAYER = "https://gis.bouldercolorado.gov/ags_svr1/rest/services/plan/Benchmarks/MapServer/0/query"

COUNTY_PARCEL_JSON_PATH = SOURCES_DIR / "boulder_county_parcel_146124100105.json"
COUNTY_PARCEL_GEOJSON_PATH = SOURCES_DIR / "boulder_county_parcel_146124100105.geojson"
COUNTY_CONTROL_JSON_PATH = SOURCES_DIR / "boulder_county_control_bank_near_site.json"
CITY_BENCHMARK_JSON_PATH = SOURCES_DIR / "boulder_city_benchmarks_near_site.json"
CONTROL_CANDIDATES_CSV_PATH = SOURCES_DIR / "farber_haines_control_candidates.csv"
SOURCE_SUMMARY_PATH = SOURCES_DIR / "farber_haines_authoritative_georef_sources_summary.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def fetch_json(base_url: str, params: dict[str, Any]) -> dict[str, Any]:
    query = urllib.parse.urlencode(params)
    request = urllib.request.Request(
        f"{base_url}?{query}",
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json,text/plain,*/*",
        },
    )
    with urllib.request.urlopen(request) as response:
        return json.load(response)


def fetch_text(base_url: str, params: dict[str, Any]) -> str:
    query = urllib.parse.urlencode(params)
    request = urllib.request.Request(
        f"{base_url}?{query}",
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json,text/plain,*/*",
        },
    )
    with urllib.request.urlopen(request) as response:
        return response.read().decode("utf-8")


def parcel_query_params(fmt: str, out_sr: int | None = None) -> dict[str, Any]:
    params: dict[str, Any] = {
        "where": f"AccountNo='{ACCOUNT_NO}'",
        "outFields": "*",
        "returnGeometry": "true",
        "f": fmt,
    }
    if out_sr is not None:
        params["outSR"] = out_sr
    return params


def load_seed() -> dict[str, Any]:
    return json.loads(SEED_PATH.read_text(encoding="utf-8"))


def save_seed(seed: dict[str, Any]) -> None:
    SEED_PATH.write_text(json.dumps(seed, indent=2), encoding="utf-8")


def extract_project_ring(parcel_json: dict[str, Any]) -> list[list[float]]:
    features = parcel_json.get("features") or []
    if not features:
        raise ValueError("Parcel query returned no features.")
    rings = (((features[0].get("geometry") or {}).get("rings")) or [])
    if not rings:
        raise ValueError("Parcel geometry contained no rings.")
    return rings[0]


def extract_geojson_ring(parcel_geojson: dict[str, Any]) -> list[list[float]]:
    features = parcel_geojson.get("features") or []
    if not features:
        raise ValueError("Parcel geojson query returned no features.")
    coords = ((((features[0].get("geometry") or {}).get("coordinates")) or [[]])[0]) or []
    if not coords:
        raise ValueError("Parcel geojson contained no coordinates.")
    return coords


def bbox_from_ring(ring: list[list[float]]) -> list[float]:
    xs = [pt[0] for pt in ring]
    ys = [pt[1] for pt in ring]
    return [min(xs), min(ys), max(xs), max(ys)]


def center_from_bbox(bbox: list[float]) -> tuple[float, float]:
    return ((bbox[0] + bbox[2]) / 2.0, (bbox[1] + bbox[3]) / 2.0)


def to_wkt(ring: list[list[float]]) -> str:
    coords = ", ".join(f"{x} {y}" for x, y in ring)
    return f"POLYGON(({coords}))"


def distance_ft(x: float, y: float, cx: float, cy: float) -> float:
    return math.hypot(x - cx, y - cy)


def fetch_nearby_features(layer_url: str, cx: float, cy: float) -> dict[str, Any]:
    return fetch_json(
        layer_url,
        {
            "where": "1=1",
            "geometry": f"{cx},{cy}",
            "geometryType": "esriGeometryPoint",
            "inSR": 2876,
            "spatialRel": "esriSpatialRelIntersects",
            "distance": SITE_RADIUS_FT,
            "units": "esriSRUnit_Foot",
            "outFields": "*",
            "returnGeometry": "true",
            "f": "json",
        },
    )


def candidate_rows(
    county_control: dict[str, Any],
    city_benchmarks: dict[str, Any],
    cx: float,
    cy: float,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for feature in county_control.get("features") or []:
        attrs = feature.get("attributes") or {}
        geom = feature.get("geometry") or {}
        x = float(geom.get("x"))
        y = float(geom.get("y"))
        rows.append({
            "source": "county_control_bank",
            "id": attrs.get("POINTID") or attrs.get("CPID") or "",
            "kind": attrs.get("CornerTP") or attrs.get("CornerCategory") or "",
            "status": attrs.get("Status") or "",
            "reliability": attrs.get("ReliabilityClass") or "",
            "description": attrs.get("CollectionNote") or attrs.get("Mon_Record") or "",
            "x_2876_ft": x,
            "y_2876_ft": y,
            "z_ft": attrs.get("ZCOORD"),
            "distance_ft": round(distance_ft(x, y, cx, cy), 3),
            "source_url": attrs.get("Url") or "",
        })
    for feature in city_benchmarks.get("features") or []:
        attrs = feature.get("attributes") or {}
        geom = feature.get("geometry") or {}
        x = float(geom.get("x"))
        y = float(geom.get("y"))
        rows.append({
            "source": "city_benchmark",
            "id": attrs.get("BMID") or "",
            "kind": "Bench Mark",
            "status": "FOUND" if attrs.get("FOUND") else "NOT_FOUND",
            "reliability": "city_benchmark",
            "description": attrs.get("DESCRIPTION2") or attrs.get("DESCRIPTION") or "",
            "x_2876_ft": x,
            "y_2876_ft": y,
            "z_ft": attrs.get("NGVD88DATUM") or attrs.get("ELEVATION"),
            "distance_ft": round(distance_ft(x, y, cx, cy), 3),
            "source_url": "",
        })
    rows.sort(key=lambda row: row["distance_ft"])
    return rows


def write_candidates_csv(rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "source",
        "id",
        "kind",
        "status",
        "reliability",
        "description",
        "x_2876_ft",
        "y_2876_ft",
        "z_ft",
        "distance_ft",
        "source_url",
    ]
    with CONTROL_CANDIDATES_CSV_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def refresh_seed(parcel_json: dict[str, Any], parcel_geojson: dict[str, Any]) -> None:
    seed = load_seed()
    geojson_feature = (parcel_geojson.get("features") or [])[0]
    project_ring = extract_project_ring(parcel_json)
    wgs84_ring = extract_geojson_ring(parcel_geojson)
    seed["project"]["address"] = "918 Juniper Ave, Boulder, CO 80304, USA"
    seed["site_boundary"]["geojson"] = geojson_feature
    seed["site_boundary"]["wkt_wgs84"] = to_wkt(wgs84_ring)
    seed["site_boundary"]["wkt_project"] = to_wkt(project_ring)
    seed["site_boundary"]["bounding_box"] = bbox_from_ring(wgs84_ring)
    seed["metadata"]["updated_at"] = now_iso()
    seed["metadata"]["notes"] = (
        "Seed updated from Boulder County parcel geometry for AccountNo R0005342 / "
        "ParcelNo 146124100105. Document binding remains unresolved until matched "
        "VW survey/corner/stake points are solved."
    )
    save_seed(seed)


def main() -> int:
    SOURCES_DIR.mkdir(parents=True, exist_ok=True)

    parcel_json = fetch_json(COUNTY_PARCEL_LAYER, parcel_query_params("json"))
    parcel_geojson = json.loads(fetch_text(COUNTY_PARCEL_LAYER, parcel_query_params("geojson", out_sr=4326)))

    COUNTY_PARCEL_JSON_PATH.write_text(json.dumps(parcel_json, indent=2), encoding="utf-8")
    COUNTY_PARCEL_GEOJSON_PATH.write_text(json.dumps(parcel_geojson, indent=2), encoding="utf-8")

    project_ring = extract_project_ring(parcel_json)
    project_bbox = bbox_from_ring(project_ring)
    cx, cy = center_from_bbox(project_bbox)

    county_control = fetch_nearby_features(COUNTY_CONTROL_LAYER, cx, cy)
    city_benchmarks = fetch_nearby_features(CITY_BENCHMARK_LAYER, cx, cy)
    COUNTY_CONTROL_JSON_PATH.write_text(json.dumps(county_control, indent=2), encoding="utf-8")
    CITY_BENCHMARK_JSON_PATH.write_text(json.dumps(city_benchmarks, indent=2), encoding="utf-8")

    rows = candidate_rows(county_control, city_benchmarks, cx, cy)
    write_candidates_csv(rows)
    refresh_seed(parcel_json, parcel_geojson)

    summary = {
        "project_id": "farber-haines-2521",
        "updated_at": now_iso(),
        "parcel_account_no": ACCOUNT_NO,
        "parcel_no": PARCEL_NO,
        "parcel_center_2876_ft": {"x": cx, "y": cy},
        "parcel_json_path": str(COUNTY_PARCEL_JSON_PATH),
        "parcel_geojson_path": str(COUNTY_PARCEL_GEOJSON_PATH),
        "county_control_json_path": str(COUNTY_CONTROL_JSON_PATH),
        "city_benchmark_json_path": str(CITY_BENCHMARK_JSON_PATH),
        "control_candidates_csv_path": str(CONTROL_CANDIDATES_CSV_PATH),
        "county_control_count": len(county_control.get("features") or []),
        "city_benchmark_count": len(city_benchmarks.get("features") or []),
        "nearest_candidates": rows[:10],
    }
    SOURCE_SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
