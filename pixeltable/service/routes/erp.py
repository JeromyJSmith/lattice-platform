"""DDC ERP routes."""

from __future__ import annotations

import importlib.util
import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from fastapi.responses import FileResponse

from service.deps import (
    get_idem_store,
    get_pxt,
    require_idempotency_key,
    require_local_socket_or_token,
)
from service.idempotency import IdempotencyStore
from service.routes._idempotent import with_idempotency

router = APIRouter(dependencies=[Depends(require_local_socket_or_token)])
log = logging.getLogger("vwbridge.erp")

_REPO_ROOT = Path(__file__).resolve().parents[3]


def _load_module(name: str, relative_path: str):
    path = _REPO_ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_BOQ_ADAPTER = _load_module("ddc_erp_boq_adapter", "ddc/erp/boq-adapter.py")
_COST_EXPORT = _load_module("ddc_erp_cost_export", "ddc/erp/cost-export.py")
_COST_SEARCH = _load_module("ddc_cwicr_cost_search", "ddc/cwicr/cost-search.py")
_PHASE_ADAPTER = _load_module("ddc_erp_phase_adapter", "ddc/erp/phase-adapter.py")


def _as_http_error(exc: Exception, detail: str) -> HTTPException:
    if isinstance(exc, NotImplementedError):
        return HTTPException(status_code=501, detail=str(exc))
    return HTTPException(status_code=502, detail=f"{detail}: {exc!s}")


@router.post("/boq")
def post_boq(
    body: dict[str, Any] = Body(...),
    pxt: Any = Depends(get_pxt),
    store: IdempotencyStore = Depends(get_idem_store),
    idem_key: str = Depends(require_idempotency_key),
):
    project_id = (body.get("project_id") or "").strip()
    if not project_id:
        raise HTTPException(status_code=400, detail="project_id required")

    def do():
        try:
            result = _BOQ_ADAPTER.sync_boq(project_id, pxt=pxt)
        except Exception as exc:
            raise _as_http_error(exc, "boq sync failed") from exc
        return {"ok": True, "project_id": project_id, "result": result}

    return with_idempotency(store, idem_key, do)


@router.get("/boq/{project_id}")
def get_boq(project_id: str):
    if not project_id.strip():
        raise HTTPException(status_code=400, detail="project_id required")
    try:
        result = _BOQ_ADAPTER.fetch_boq(project_id)
    except Exception as exc:
        raise _as_http_error(exc, "boq fetch failed") from exc
    return result


@router.get("/export/{project_id}")
def get_export(project_id: str, fmt: str = Query(default="xlsx", pattern="^(xlsx|csv)$")):
    if not project_id.strip():
        raise HTTPException(status_code=400, detail="project_id required")
    try:
        output_path = Path(_COST_EXPORT.export_boq(project_id, fmt))
    except Exception as exc:
        raise _as_http_error(exc, "boq export failed") from exc
    if not output_path.exists():
        raise HTTPException(status_code=500, detail=f"export missing at {output_path}")
    media_type = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        if fmt == "xlsx"
        else "text/csv"
    )
    return FileResponse(output_path, media_type=media_type, filename=output_path.name)


@router.post("/cost-search")
def post_cost_search(body: dict[str, Any] = Body(...)):
    description = (body.get("description") or "").strip()
    if not description:
        raise HTTPException(status_code=400, detail="description required")
    region = (body.get("region") or "US").strip() or "US"
    top = int(body.get("top") or 5)
    try:
        rows = _COST_SEARCH.search(description, region, top)
    except Exception as exc:
        raise _as_http_error(exc, "cost search failed") from exc
    return {"ok": True, "description": description, "region": region, "top": top, "rows": rows}


@router.post("/phases")
def post_phases(
    body: dict[str, Any] = Body(...),
    store: IdempotencyStore = Depends(get_idem_store),
    idem_key: str = Depends(require_idempotency_key),
):
    project_id = (body.get("project_id") or "").strip()
    if not project_id:
        raise HTTPException(status_code=400, detail="project_id required")

    def do():
        try:
            result = _PHASE_ADAPTER.sync_phases(project_id)
        except Exception as exc:
            raise _as_http_error(exc, "phase sync failed") from exc
        return {"ok": True, "project_id": project_id, "result": result}

    return with_idempotency(store, idem_key, do)
