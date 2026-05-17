"""DDC ERP routes."""

from __future__ import annotations

import importlib.util
import logging
from pathlib import Path
from typing import Any

import httpx
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
DEFAULT_COST_SEARCH_REGION = "US"
DEFAULT_COST_SEARCH_TOP = 5
MAX_COST_SEARCH_TOP = 25
MAX_COST_SEARCH_DESCRIPTION_LENGTH = 500
MAX_COST_SEARCH_REGION_LENGTH = 16
MIN_REVIEW_SCORE = 0.25
MIN_RELIABLE_SCORE = 0.55


def _load_module(name: str, relative_path: str):
    path = _REPO_ROOT / relative_path
    if not path.exists():
        raise RuntimeError(f"required DDC adapter missing: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        raise RuntimeError(f"failed to load DDC adapter {path}: {exc!s}") from exc
    return module


_BOQ_ADAPTER = _load_module("ddc_erp_boq_adapter", "ddc/erp/boq-adapter.py")
_COST_EXPORT = _load_module("ddc_erp_cost_export", "ddc/erp/cost-export.py")
_COST_SEARCH = _load_module("ddc_cwicr_cost_search", "ddc/cwicr/cost-search.py")
_PHASE_ADAPTER = _load_module("ddc_erp_phase_adapter", "ddc/erp/phase-adapter.py")


def _as_http_error(exc: Exception, detail: str) -> HTTPException:
    if isinstance(exc, NotImplementedError):
        return HTTPException(status_code=501, detail=str(exc))
    return HTTPException(status_code=502, detail=f"{detail}: {exc!s}")


def _normalize_project_id(value: Any) -> str:
    if not isinstance(value, str):
        raise HTTPException(status_code=400, detail="project_id required")
    project_id = value.strip()
    if not project_id:
        raise HTTPException(status_code=400, detail="project_id required")
    return project_id


def _as_boq_read_http_error(exc: Exception, project_id: str) -> HTTPException:
    if isinstance(exc, NotImplementedError):
        return HTTPException(status_code=501, detail=str(exc))
    if isinstance(exc, httpx.HTTPStatusError):
        request_path = exc.request.url.path
        if exc.response.status_code == 404:
            return HTTPException(
                status_code=404,
                detail=f"upstream ERP returned 404 for {request_path} (project_id={project_id})",
            )
        return HTTPException(
            status_code=502,
            detail=f"boq fetch failed: upstream ERP returned {exc.response.status_code} for {request_path}",
        )
    return _as_http_error(exc, "boq fetch failed")


def _coerce_score(row: dict[str, Any]) -> float | None:
    value = row.get("score")
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    return None


def _normalize_description(value: Any) -> str:
    if not isinstance(value, str):
        raise HTTPException(status_code=400, detail="description required")
    description = value.strip()
    if not description:
        raise HTTPException(status_code=400, detail="description required")
    if len(description) > MAX_COST_SEARCH_DESCRIPTION_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"description must be <= {MAX_COST_SEARCH_DESCRIPTION_LENGTH} chars",
        )
    return description


def _normalize_region(value: Any) -> str:
    if value is None:
        return DEFAULT_COST_SEARCH_REGION
    if not isinstance(value, str):
        raise HTTPException(status_code=400, detail="region must be a string")
    region = value.strip().upper() or DEFAULT_COST_SEARCH_REGION
    if len(region) > MAX_COST_SEARCH_REGION_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"region must be 1..{MAX_COST_SEARCH_REGION_LENGTH} chars",
        )
    if not all(char.isalnum() or char in {"-", "_"} for char in region):
        raise HTTPException(
            status_code=400,
            detail="region must contain only letters, digits, hyphen, or underscore",
        )
    return region


def _normalize_top(value: Any) -> int:
    if value is None:
        return DEFAULT_COST_SEARCH_TOP
    if isinstance(value, bool):
        raise HTTPException(status_code=400, detail=f"top must be between 1 and {MAX_COST_SEARCH_TOP}")
    try:
        top = int(value)
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=400,
            detail=f"top must be between 1 and {MAX_COST_SEARCH_TOP}",
        ) from exc
    if top < 1 or top > MAX_COST_SEARCH_TOP:
        raise HTTPException(status_code=400, detail=f"top must be between 1 and {MAX_COST_SEARCH_TOP}")
    return top


def _normalize_optional_string(value: Any, *, field: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise HTTPException(status_code=502, detail=f"cost search returned non-string {field}")
    normalized = value.strip()
    return normalized or None


def _normalize_required_string(value: Any, *, field: str) -> str:
    normalized = _normalize_optional_string(value, field=field)
    if normalized is None:
        raise HTTPException(status_code=502, detail=f"cost search returned empty {field}")
    return normalized


def _normalize_optional_number(value: Any, *, field: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise HTTPException(status_code=502, detail=f"cost search returned boolean {field}")
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError as exc:
            raise HTTPException(status_code=502, detail=f"cost search returned non-numeric {field}") from exc
    raise HTTPException(status_code=502, detail=f"cost search returned invalid {field}")


def _normalize_cost_search_rows(rows: Any, region: str) -> list[dict[str, Any]]:
    if not isinstance(rows, list):
        raise HTTPException(status_code=502, detail="cost search returned invalid rows payload")
    normalized_rows: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            raise HTTPException(status_code=502, detail="cost search returned a non-object row")
        normalized_row = {
            "item_id": _normalize_required_string(row.get("item_id"), field="item_id"),
            "name": _normalize_required_string(row.get("name"), field="name"),
            "unit": _normalize_optional_string(row.get("unit"), field="unit"),
            "unit_cost": _normalize_optional_number(row.get("unit_cost"), field="unit_cost"),
            "unit_currency": _normalize_optional_string(row.get("unit_currency"), field="unit_currency") or "USD",
            "unit_cost_region": _normalize_optional_string(
                row.get("unit_cost_region"),
                field="unit_cost_region",
            )
            or region,
            "score": _coerce_score(row),
        }
        normalized_rows.append(normalized_row)
    return normalized_rows


def _classify_cost_search(rows: list[dict[str, Any]]) -> dict[str, Any]:
    top_row = rows[0] if rows else None
    top_score = _coerce_score(top_row) if top_row else None
    if top_score is None:
        return {
            "top_score": None,
            "signal": "none",
            "reliable": False,
            "verdict": "failed",
            "message": "No CWICR match was returned.",
        }
    if top_score >= MIN_RELIABLE_SCORE:
        return {
            "top_score": top_score,
            "signal": "high",
            "reliable": True,
            "verdict": "passed",
            "message": "Top CWICR match met the reliable threshold.",
        }
    if top_score >= MIN_REVIEW_SCORE:
        return {
            "top_score": top_score,
            "signal": "medium",
            "reliable": False,
            "verdict": "review_required",
            "message": "Top CWICR match is review-only and must not be treated as verified proof.",
        }
    return {
        "top_score": top_score,
        "signal": "low",
        "reliable": False,
        "verdict": "failed",
        "message": "Top CWICR match is too weak for verified cost evidence.",
    }


def _cost_search_trust_contract(verification_status: str) -> dict[str, Any]:
    return {
        "surface": "POST /v1/erp/cost-search",
        "evidence_kind": "cwicr_semantic_match",
        "verified_statuses": ["passed"],
        "review_statuses": ["review_required", "unverified"],
        "thresholds": {
            "review_required_gte": MIN_REVIEW_SCORE,
            "verified_gte": MIN_RELIABLE_SCORE,
        },
        "status": verification_status,
        "verified_only_when": [
            "request validation passed",
            "adapter returned normalized rows",
            f"top score is numeric and >= {MIN_RELIABLE_SCORE}",
        ],
    }


@router.post("/boq")
def post_boq(
    body: dict[str, Any] = Body(...),
    pxt: Any = Depends(get_pxt),
    store: IdempotencyStore = Depends(get_idem_store),
    idem_key: str = Depends(require_idempotency_key),
):
    """Sync a BOQ payload into the ERP adapter for one project."""
    project_id = (body.get("project_id") or "").strip()
    if not project_id:
        raise HTTPException(status_code=400, detail="project_id required")

    def do():
        """Execute the idempotent BOQ sync."""
        try:
            result = _BOQ_ADAPTER.sync_boq(project_id, pxt=pxt)
        except Exception as exc:
            raise _as_http_error(exc, "boq sync failed") from exc
        return {"ok": True, "project_id": project_id, "result": result}

    return with_idempotency(store, idem_key, do)


@router.get("/boq/{project_id}")
def get_boq(project_id: str):
    """Fetch the ERP BOQ snapshot for one project."""
    normalized_project_id = _normalize_project_id(project_id)
    try:
        result = _BOQ_ADAPTER.fetch_boq(normalized_project_id)
    except Exception as exc:
        raise _as_boq_read_http_error(exc, normalized_project_id) from exc
    return result


@router.get("/export/{project_id}")
def get_export(project_id: str, fmt: str = Query(default="xlsx", pattern="^(xlsx|csv)$")):
    """Stream a generated BOQ export for one project."""
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
    """Search CWICR cost rows and classify the returned proof strength."""
    description = _normalize_description(body.get("description"))
    region = _normalize_region(body.get("region"))
    top = _normalize_top(body.get("top"))
    try:
        rows = _normalize_cost_search_rows(_COST_SEARCH.search(description, region, top), region)
    except HTTPException:
        raise
    except Exception as exc:
        raise _as_http_error(exc, "cost search failed") from exc
    confidence = _classify_cost_search(rows)
    verification = {
        "status": confidence["verdict"],
        "message": confidence["message"],
    }
    return {
        "ok": confidence["reliable"],
        "description": description,
        "region": region,
        "top": top,
        "rows": rows,
        "confidence": confidence,
        "verification": verification,
        "trust_contract": _cost_search_trust_contract(verification["status"]),
    }


@router.post("/phases")
def post_phases(
    body: dict[str, Any] = Body(...),
    store: IdempotencyStore = Depends(get_idem_store),
    idem_key: str = Depends(require_idempotency_key),
):
    """Sync ERP phase data for one project."""
    project_id = (body.get("project_id") or "").strip()
    if not project_id:
        raise HTTPException(status_code=400, detail="project_id required")

    def do():
        """Execute the idempotent phase sync."""
        try:
            result = _PHASE_ADAPTER.sync_phases(project_id)
        except Exception as exc:
            raise _as_http_error(exc, "phase sync failed") from exc
        return {"ok": True, "project_id": project_id, "result": result}

    return with_idempotency(store, idem_key, do)
