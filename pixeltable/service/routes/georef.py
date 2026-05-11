"""Georef routes — the per-project coordinate authority.

Every endpoint here reads from or writes to `lattice/bridge/project_georef`.
Survey beats IFC beats GPS beats Google Maps beats OSM (configurable per
project via the `source_priority` JSON array).

All endpoints are stubs returning 501 until the matching ingest helpers
in `georef/converters/` are implemented. The handler shape and contract
are stable — only the bodies are pending.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Body, Depends, File, Form, HTTPException, UploadFile

from service.deps import (
    get_idem_store,
    get_pxt,
    require_idempotency_key,
    require_local_socket_or_token,
)
from service.routes._idempotent import with_idempotency

router = APIRouter(dependencies=[Depends(require_local_socket_or_token)])
log = logging.getLogger("vwbridge.georef")

GEOREF_TABLE = "lattice/bridge/project_georef"


def _upsert_stub(table_path: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Placeholder until the proper upsert is wired through service/upsert.py.

    Returns the payload so endpoints can echo back what they would have written.
    """
    log.info("STUB upsert %s payload_keys=%s", table_path, sorted(payload.keys()))
    return {"would_upsert": table_path, "payload_keys": sorted(payload.keys())}


# ----- ingest endpoints (one per source format) ---------------------------

@router.post("/ingest/config")
def ingest_config(
    body: dict[str, Any] = Body(...),
    pxt=Depends(get_pxt),
    store=Depends(get_idem_store),
    idem_key: str = Depends(require_idempotency_key),
):
    """Ingest a full `georef.config.json` payload for one project."""
    project_id = body.get("project", {}).get("project_id") or body.get("project_id")
    if not project_id:
        raise HTTPException(400, "project_id required (top-level or in body.project)")

    def do() -> dict:
        # TODO: validate against georef/schema/georef.config.schema.json,
        # then map JSON -> project_georef columns and upsert.
        return {"ok": True, "result": _upsert_stub(GEOREF_TABLE, body)}

    return with_idempotency(store, idem_key, do)


@router.post("/ingest/kml")
async def ingest_kml(
    project_id: str = Form(...),
    file: UploadFile = File(...),
    pxt=Depends(get_pxt),
    idem_key: str = Depends(require_idempotency_key),
):
    """KML / KMZ → boundary_wkt_wgs84 + boundary_geojson + area_m2."""
    raise HTTPException(501, "ingest/kml stub — see georef/converters/kml_to_georef.py")


@router.post("/ingest/shapefile")
async def ingest_shapefile(
    project_id: str = Form(...),
    file: UploadFile = File(...),
    pxt=Depends(get_pxt),
    idem_key: str = Depends(require_idempotency_key),
):
    """Zipped Shapefile (.shp + .prj + .shx + .dbf) → boundary fields + epsg_code."""
    raise HTTPException(501, "ingest/shapefile stub")


@router.post("/ingest/geotiff")
async def ingest_geotiff(
    project_id: str = Form(...),
    asset_kind: str = Form(...),  # 'dem' or 'orthophoto'
    file: UploadFile = File(...),
    pxt=Depends(get_pxt),
    idem_key: str = Depends(require_idempotency_key),
):
    """GeoTIFF DEM or orthophoto → dem_* or orthophoto_* fields."""
    if asset_kind not in {"dem", "orthophoto"}:
        raise HTTPException(400, "asset_kind must be 'dem' or 'orthophoto'")
    raise HTTPException(501, "ingest/geotiff stub")


@router.post("/ingest/survey-csv")
async def ingest_survey_csv(
    project_id: str = Form(...),
    source_epsg: str = Form(...),  # e.g. "EPSG:2243"
    file: UploadFile = File(...),
    pxt=Depends(get_pxt),
    idem_key: str = Depends(require_idempotency_key),
):
    """Survey control-points CSV → survey_* + control_points_json fields."""
    raise HTTPException(501, "ingest/survey-csv stub")


@router.post("/ingest/ifc")
def ingest_ifc(
    body: dict[str, Any] = Body(...),
    pxt=Depends(get_pxt),
    idem_key: str = Depends(require_idempotency_key),
):
    """IFC file path + project_id → IfcSite RefLat/RefLon/RefElevation extraction."""
    if "project_id" not in body or "ifc_path" not in body:
        raise HTTPException(400, "project_id and ifc_path required")
    raise HTTPException(501, "ingest/ifc stub — see georef/converters/ifc_to_georef.py")


@router.post("/ingest/osm")
def ingest_osm(
    body: dict[str, Any] = Body(...),
    pxt=Depends(get_pxt),
    idem_key: str = Depends(require_idempotency_key),
):
    """Overpass API fetch within boundary_geojson → osm_* fields."""
    if "project_id" not in body or "boundary_geojson" not in body:
        raise HTTPException(400, "project_id and boundary_geojson required")
    raise HTTPException(501, "ingest/osm stub")


# ----- compute + query endpoints ------------------------------------------

@router.post("/compute-transforms/{project_id}")
def compute_transforms(project_id: str, pxt=Depends(get_pxt)):
    """Populate transform_vw_to_wgs84 / wgs84_to_ecef / project_to_utm /
    ifc_to_wgs84 via pyproj. Idempotent (safe to re-run any time)."""
    raise HTTPException(501, "compute-transforms stub — use pyproj.Transformer")


@router.get("/{project_id}")
def get_georef(project_id: str, pxt=Depends(get_pxt)):
    """Return the full project_georef row for a project."""
    t = pxt.get_table(GEOREF_TABLE)
    rows = t.where(t.project_id == project_id).collect()
    rows_list = list(rows)
    if not rows_list:
        raise HTTPException(404, f"no project_georef row for project_id={project_id!r}")
    return {"project_id": project_id, "row": dict(rows_list[0])}


@router.get("/{project_id}/transforms")
def get_transforms(project_id: str, pxt=Depends(get_pxt)):
    """Just the four transform matrices."""
    t = pxt.get_table(GEOREF_TABLE)
    rows = list(t.where(t.project_id == project_id).select(
        t.transform_vw_to_wgs84, t.transform_wgs84_to_ecef,
        t.transform_project_to_utm, t.transform_ifc_to_wgs84,
    ).collect())
    if not rows:
        raise HTTPException(404, f"no project_georef row for project_id={project_id!r}")
    r = rows[0]
    return {
        "project_id": project_id,
        "vw_to_wgs84":    _parse_or_none(r.get("transform_vw_to_wgs84")),
        "wgs84_to_ecef":  _parse_or_none(r.get("transform_wgs84_to_ecef")),
        "project_to_utm": _parse_or_none(r.get("transform_project_to_utm")),
        "ifc_to_wgs84":   _parse_or_none(r.get("transform_ifc_to_wgs84")),
    }


@router.get("/{project_id}/boundary.geojson")
def get_boundary_geojson(project_id: str, pxt=Depends(get_pxt)):
    """Return the site boundary as a GeoJSON Feature (Cesium- / deck.gl-ready)."""
    t = pxt.get_table(GEOREF_TABLE)
    rows = list(t.where(t.project_id == project_id).select(
        t.boundary_geojson, t.boundary_wkt_wgs84, t.area_m2,
    ).collect())
    if not rows:
        raise HTTPException(404, f"no project_georef row for project_id={project_id!r}")
    r = rows[0]
    geojson = _parse_or_none(r.get("boundary_geojson"))
    if geojson is None and not r.get("boundary_wkt_wgs84"):
        raise HTTPException(404, "no boundary geometry recorded for this project yet")
    return {
        "type": "Feature",
        "properties": {"project_id": project_id, "area_m2": r.get("area_m2")},
        "geometry": geojson,
    }


def _parse_or_none(s: Any) -> Any:
    if s is None or s == "":
        return None
    if isinstance(s, (dict, list)):
        return s
    try:
        return json.loads(s)
    except (TypeError, json.JSONDecodeError):
        return None
