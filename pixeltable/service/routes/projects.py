"""Project-scoped ingest routes: POST /v1/projects/{project_id}/ingest/ifc.

Each project has its own Pixeltable namespace: lattice/projects/{project_id}/
Tables are created on demand (idempotent).  No migration required — the schema
is the same for every project; only the namespace differs.

Endpoints
---------
POST /v1/projects/{project_id}/ingest/ifc
    Accept a multipart IFC file upload and ingest all elements into the
    project-scoped namespace.  Returns element counts + parse stats.

GET /v1/projects/{project_id}/elements
    List IFC elements for a project (lightweight — returns id, ifc_class,
    name, tag, is_marpa_seed only; no geometry blobs).

GET /v1/projects/{project_id}/status
    Registry check + element count for a named project.
"""

from __future__ import annotations

import hashlib
import logging
import tempfile
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile

from service.deps import (
    get_pxt,
    get_settings,
    require_local_socket_or_token,
)

router = APIRouter(dependencies=[Depends(require_local_socket_or_token)])
log = logging.getLogger("vwbridge.projects")

# ---------------------------------------------------------------------------
# Pixeltable schema helpers
# ---------------------------------------------------------------------------

_IFC_ELEMENT_COLUMNS: dict[str, Any] = {}  # populated lazily after pxt import


def _ensure_project_tables(pxt, project_id: str) -> None:
    """Ensure lattice/projects/{project_id}/ namespace and ifc_elements table exist.

    Idempotent — safe to call on every request.
    """
    import pixeltable as pxt_mod  # local import; sidecar env has pixeltable

    ns_root = "lattice/projects"
    ns_proj = f"{ns_root}/{project_id}"

    # Create ancestor dirs (pxt raises if already exists — catch)
    for ns in [ns_root, ns_proj]:
        try:
            pxt_mod.create_dir(ns)
        except Exception:
            pass  # already exists

    tbl_path = f"{ns_proj}/ifc_elements"
    try:
        pxt_mod.get_table(tbl_path)
        return  # already exists
    except Exception:
        pass

    pxt_mod.create_table(tbl_path, {
        "id":                    pxt_mod.String,
        "project_id":            pxt_mod.String,
        "ingest_hash":           pxt_mod.String,
        "source_element_id":     pxt_mod.String,
        "ifc_class":             pxt_mod.String,
        "ifc_predefined_type":   pxt_mod.String,
        "ifc_schema":            pxt_mod.String,
        "name":                  pxt_mod.String,
        "long_name":             pxt_mod.String,
        "object_type":           pxt_mod.String,
        "tag":                   pxt_mod.String,
        "description":           pxt_mod.String,
        "spatial_container_guid":  pxt_mod.String,
        "spatial_container_class": pxt_mod.String,
        "bbox_min":              pxt_mod.Json,
        "bbox_max":              pxt_mod.Json,
        "centroid":              pxt_mod.Json,
        "elevation_m":           pxt_mod.Float,
        "is_marpa_seed":         pxt_mod.Bool,
        "property_sets":         pxt_mod.Json,
        "raw_attributes":        pxt_mod.Json,
        "parsed_at":             pxt_mod.String,
        "source_filename":       pxt_mod.String,
        "source_byte_size":      pxt_mod.Int,
    })
    log.info("created %s", tbl_path)


# ---------------------------------------------------------------------------
# Internal ingest worker
# ---------------------------------------------------------------------------

def _ingest_ifc_file(pxt, project_id: str, ifc_path: Path, filename: str) -> dict[str, Any]:
    """Parse IFC and upsert into project-scoped Pixeltable table.

    Returns a dict with element counts and parse stats.
    """
    from service.ifc_parser import parse_ifc
    import pixeltable as pxt_mod
    from datetime import datetime, timezone

    byte_size = ifc_path.stat().st_size
    ingest_hash = hashlib.sha256(ifc_path.read_bytes()).hexdigest()[:16]
    parsed_at = datetime.now(timezone.utc).isoformat()

    log.info("parsing IFC project=%s file=%s size=%d", project_id, filename, byte_size)
    result = parse_ifc(ifc_path)
    elements = result.get("elements", [])
    schema = result.get("schema", "")

    _ensure_project_tables(pxt, project_id)

    tbl_path = f"lattice/projects/{project_id}/ifc_elements"
    tbl = pxt_mod.get_table(tbl_path)

    # Delete previous rows for this ingest_hash (idempotent re-run)
    try:
        tbl.delete(tbl.ingest_hash == ingest_hash)
    except Exception:
        pass

    from service.ids import uuidv7

    rows = []
    for elt in elements:
        rows.append({
            "id":                    uuidv7(),
            "project_id":            project_id,
            "ingest_hash":           ingest_hash,
            "source_element_id":     elt.get("source_element_id", ""),
            "ifc_class":             elt.get("ifc_class", ""),
            "ifc_predefined_type":   elt.get("ifc_predefined_type", "") or "",
            "ifc_schema":            schema,
            "name":                  elt.get("name", "") or "",
            "long_name":             elt.get("long_name", "") or "",
            "object_type":           elt.get("object_type", "") or "",
            "tag":                   elt.get("tag", "") or "",
            "description":           elt.get("description", "") or "",
            "spatial_container_guid":  elt.get("spatial_container_guid", "") or "",
            "spatial_container_class": elt.get("spatial_container_class", "") or "",
            "bbox_min":              elt.get("bbox_min"),
            "bbox_max":              elt.get("bbox_max"),
            "centroid":              elt.get("centroid"),
            "elevation_m":           float(elt.get("elevation_m") or 0.0),
            "is_marpa_seed":         bool(elt.get("marpa_seed", False)),
            "property_sets":         elt.get("property_sets", []),
            "raw_attributes":        elt.get("raw_attributes", {}),
            "parsed_at":             parsed_at,
            "source_filename":       filename,
            "source_byte_size":      byte_size,
        })

    if rows:
        tbl.insert(rows)

    return {
        "project_id":   project_id,
        "ingest_hash":  ingest_hash,
        "ifc_schema":   schema,
        "filename":     filename,
        "byte_size":    byte_size,
        "element_count": len(rows),
        "table":        tbl_path,
        "parsed_at":    parsed_at,
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/{project_id}/ingest/ifc")
async def post_ingest_ifc(
    project_id: str,
    file: UploadFile = File(...),
    pxt=Depends(get_pxt),
    settings=Depends(get_settings),
):
    """Ingest an IFC file into the project-scoped Pixeltable namespace.

    Multipart upload — `file` field must be an IFC file.  The project must
    exist in `projects/registry.yaml`; returns 404 if unknown.

    Element parsing uses `service.ifc_parser.parse_ifc` (landscape IFC
    classes, full property set extraction, MARPA seed classification).

    Returns JSON with element counts, parse stats, and Pixeltable table path.
    """
    if not project_id.replace("-", "").replace("_", "").isalnum():
        raise HTTPException(status_code=400, detail="project_id must be alphanumeric with - or _")

    # Validate the IFC content-type loosely (VW exports plain .ifc)
    content_type = file.content_type or ""
    filename = file.filename or "upload.ifc"
    if not filename.lower().endswith(".ifc") and "ifc" not in content_type.lower():
        raise HTTPException(
            status_code=400,
            detail=f"Expected an IFC file; got filename={filename!r} content_type={content_type!r}",
        )

    # Check file size against settings
    max_bytes = getattr(settings, "IFC_MAX_BYTES", 200 * 1024 * 1024)  # 200 MB default
    data = await file.read()
    if len(data) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"IFC file too large: {len(data)} bytes > IFC_MAX_BYTES={max_bytes}",
        )

    # Write to tmp, parse, ingest
    with tempfile.NamedTemporaryFile(suffix=".ifc", delete=False) as tmp:
        tmp.write(data)
        tmp_path = Path(tmp.name)

    try:
        result = _ingest_ifc_file(pxt, project_id, tmp_path, filename)
    except Exception as exc:
        log.exception("IFC ingest failed project=%s", project_id)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        try:
            tmp_path.unlink()
        except Exception:
            pass

    return {"ok": True, "result": result}


@router.get("/{project_id}/elements")
def get_project_elements(
    project_id: str,
    pxt=Depends(get_pxt),
    ifc_class: str | None = Query(default=None, description="Filter by ifc_class"),
    limit: int = Query(default=200, ge=1, le=5000),
):
    """Return a lightweight element list for a project (id, ifc_class, name, tag, is_marpa_seed).

    Excludes geometry blobs (bbox, centroid, property_sets) for fast reads.
    Use query param `ifc_class` to filter by class (e.g. IfcGeographicElement).
    """
    import pixeltable as pxt_mod

    tbl_path = f"lattice/projects/{project_id}/ifc_elements"
    try:
        tbl = pxt_mod.get_table(tbl_path)
    except Exception:
        raise HTTPException(
            status_code=404,
            detail=f"No ifc_elements table for project '{project_id}'. Run ingest first.",
        )

    query = tbl.select(
        tbl.id,
        tbl.source_element_id,
        tbl.ifc_class,
        tbl.ifc_schema,
        tbl.name,
        tbl.tag,
        tbl.is_marpa_seed,
        tbl.parsed_at,
        tbl.source_filename,
    )
    if ifc_class:
        query = query.where(tbl.ifc_class == ifc_class)
    query = query.limit(limit)

    rows = query.collect().to_pydict()
    # Convert to list-of-dicts
    keys = list(rows.keys())
    n = len(rows[keys[0]]) if keys else 0
    records = [{k: rows[k][i] for k in keys} for i in range(n)]

    return {"ok": True, "project_id": project_id, "count": len(records), "elements": records}


@router.get("/{project_id}/status")
def get_project_status(
    project_id: str,
    pxt=Depends(get_pxt),
):
    """Return project registry info + element count (if table exists)."""
    import pixeltable as pxt_mod
    from pathlib import Path as _Path
    import yaml as _yaml

    # Load registry
    registry_path = _Path(__file__).resolve().parents[3] / "projects" / "registry.yaml"
    registry: dict[str, Any] = {"projects": []}
    if registry_path.exists():
        registry = _yaml.safe_load(registry_path.read_text()) or {"projects": []}

    proj = next(
        (p for p in registry.get("projects", []) if p.get("id") == project_id),
        None,
    )
    if not proj:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not in registry")

    # Count elements if table exists
    element_count: int | None = None
    tbl_path = f"lattice/projects/{project_id}/ifc_elements"
    try:
        tbl = pxt_mod.get_table(tbl_path)
        df = tbl.select(tbl.id).collect()
        element_count = len(df)
    except Exception:
        element_count = None

    return {
        "ok": True,
        "project": proj,
        "element_count": element_count,
        "ifc_elements_table": tbl_path,
        "ingested": element_count is not None and element_count > 0,
    }
