"""Pure-Python tests for ERP route proof semantics."""

from __future__ import annotations

import httpx
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from service.idempotency import IdempotencyStore
from service.routes import erp


def _app(tmp_path: Path, *, pxt: object | None = None) -> FastAPI:
    app = FastAPI()
    app.state.idem = IdempotencyStore(tmp_path / ".idem.json")
    app.state.pxt = object() if pxt is None else pxt
    app.include_router(erp.router, prefix="/v1/erp")
    return app


def test_cost_search_requires_description(tmp_path: Path):
    """Reject cost-search requests that omit the description."""
    client = TestClient(_app(tmp_path))
    response = client.post("/v1/erp/cost-search", json={"region": "US", "top": 3})
    assert response.status_code == 400
    assert response.json()["detail"] == "description required"


def test_cost_search_returns_rows(tmp_path: Path, monkeypatch):
    """Mark high-confidence numeric scores as passed proof."""
    monkeypatch.setattr(
        erp._COST_SEARCH,
        "search",
        lambda description, region, top: [
            {"item_id": "cwicr-1", "name": description, "unit_cost_region": region, "score": top}
        ],
    )
    client = TestClient(_app(tmp_path))
    response = client.post(
        "/v1/erp/cost-search",
        json={"description": "planting bed", "region": "US", "top": 4},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["rows"][0]["item_id"] == "cwicr-1"
    assert body["confidence"]["signal"] == "high"
    assert body["verification"]["status"] == "passed"
    assert body["trust_contract"]["surface"] == "POST /v1/erp/cost-search"
    assert body["trust_contract"]["status"] == "passed"
    assert body["trust_contract"]["thresholds"]["verified_gte"] == erp.MIN_RELIABLE_SCORE


def test_cost_search_rejects_invalid_top_as_bad_request(tmp_path: Path):
    """Reject invalid top values at the route boundary instead of surfacing adapter errors."""
    client = TestClient(_app(tmp_path))
    response = client.post(
        "/v1/erp/cost-search",
        json={"description": "planting bed", "region": "US", "top": 0},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == f"top must be between 1 and {erp.MAX_COST_SEARCH_TOP}"


def test_cost_search_rejects_malformed_adapter_rows(tmp_path: Path, monkeypatch):
    """Fail closed when the adapter returns rows that do not satisfy the route contract."""
    monkeypatch.setattr(
        erp._COST_SEARCH,
        "search",
        lambda description, region, top: [{"item_id": "cwicr-1"}],
    )
    client = TestClient(_app(tmp_path))
    response = client.post(
        "/v1/erp/cost-search",
        json={"description": "planting bed", "region": "US", "top": 3},
    )
    assert response.status_code == 502
    assert response.json()["detail"] == "cost search returned empty name"


def test_cost_search_marks_review_only_matches(tmp_path: Path, monkeypatch):
    """Downgrade mid-range numeric scores to review-only proof."""
    monkeypatch.setattr(
        erp._COST_SEARCH,
        "search",
        lambda description, region, top: [
            {"item_id": "cwicr-1", "name": description, "unit_cost_region": region, "score": 0.42}
        ],
    )
    client = TestClient(_app(tmp_path))
    response = client.post(
        "/v1/erp/cost-search",
        json={"description": "planting bed", "region": "US", "top": 4},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is False
    assert body["confidence"]["signal"] == "medium"
    assert body["confidence"]["verdict"] == "review_required"
    assert body["verification"]["status"] == "review_required"


def test_cost_search_marks_weak_matches_failed(tmp_path: Path, monkeypatch):
    """Fail weak numeric scores instead of treating them as verified proof."""
    monkeypatch.setattr(
        erp._COST_SEARCH,
        "search",
        lambda description, region, top: [
            {"item_id": "cwicr-1", "name": description, "unit_cost_region": region, "score": 0.12}
        ],
    )
    client = TestClient(_app(tmp_path))
    response = client.post(
        "/v1/erp/cost-search",
        json={"description": "planting bed", "region": "US", "top": 4},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is False
    assert body["confidence"]["signal"] == "low"
    assert body["verification"]["status"] == "failed"


def test_cost_search_marks_no_rows_failed(tmp_path: Path, monkeypatch):
    """Fail cost-search requests that return no rows."""
    monkeypatch.setattr(erp._COST_SEARCH, "search", lambda description, region, top: [])
    client = TestClient(_app(tmp_path))
    response = client.post(
        "/v1/erp/cost-search",
        json={"description": "planting bed", "region": "US", "top": 4},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is False
    assert body["rows"] == []
    assert body["confidence"]["signal"] == "none"
    assert body["verification"]["status"] == "failed"


def test_cost_search_rejects_boolean_scores_as_numeric_proof(tmp_path: Path, monkeypatch):
    """Treat boolean scores as missing proof strength instead of numeric evidence."""
    monkeypatch.setattr(
        erp._COST_SEARCH,
        "search",
        lambda description, region, top: [
            {"item_id": "cwicr-1", "name": description, "unit_cost_region": region, "score": True}
        ],
    )
    client = TestClient(_app(tmp_path))
    response = client.post(
        "/v1/erp/cost-search",
        json={"description": "planting bed", "region": "US", "top": 4},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is False
    assert body["confidence"]["top_score"] is None
    assert body["confidence"]["signal"] == "none"
    assert body["verification"]["status"] == "failed"


def test_boq_sync_surfaces_precise_pixeltable_blocker(tmp_path: Path):
    """Expose the concrete BOQ sync blocker instead of a generic stub message."""
    client = TestClient(_app(tmp_path))
    response = client.post(
        "/v1/erp/boq",
        json={"project_id": "proj-1"},
        headers={"Idempotency-Key": "ddc-boq-sync-0001"},
    )
    assert response.status_code == 501
    assert (
        response.json()["detail"]
        == "boq sync blocked: Pixeltable handle is not ready; expected get_table() for project IFC row access and BOQ writeback."
    )


def test_boq_read_strips_project_id_before_adapter_call(tmp_path: Path, monkeypatch):
    """Normalize the project id before calling the BOQ read adapter."""
    seen: list[str] = []

    def _fetch(project_id: str):
        seen.append(project_id)
        return {
            "ok": True,
            "project_id": project_id,
            "erp_base": "http://localhost:8080",
            "boq": {"items": []},
        }

    monkeypatch.setattr(erp._BOQ_ADAPTER, "fetch_boq", _fetch)
    client = TestClient(_app(tmp_path))
    response = client.get("/v1/erp/boq/%20proj-1%20")
    assert response.status_code == 200
    assert response.json()["project_id"] == "proj-1"
    assert seen == ["proj-1"]


def test_boq_read_surfaces_upstream_404(tmp_path: Path, monkeypatch):
    """Preserve upstream BOQ 404s with a concrete blocker message."""
    request = httpx.Request("GET", "http://localhost:8080/api/boq/proj-404")
    response = httpx.Response(404, request=request, json={"detail": "Not Found"})

    def _fetch(project_id: str):
        raise httpx.HTTPStatusError("Not Found", request=request, response=response)

    monkeypatch.setattr(erp._BOQ_ADAPTER, "fetch_boq", _fetch)
    client = TestClient(_app(tmp_path))
    route_response = client.get("/v1/erp/boq/proj-404")
    assert route_response.status_code == 404
    assert route_response.json()["detail"] == "upstream ERP returned 404 for /api/boq/proj-404 (project_id=proj-404)"


def test_boq_read_surfaces_upstream_401(tmp_path: Path, monkeypatch):
    """Preserve upstream BOQ auth failures with a concrete blocker message."""
    request = httpx.Request("GET", "https://openconstructionerp.marpa.localhost:1355/api/v1/boq/boqs/")
    response = httpx.Response(401, request=request, json={"detail": "Not authenticated"})

    def _fetch(project_id: str):
        raise httpx.HTTPStatusError("Unauthorized", request=request, response=response)

    monkeypatch.setattr(erp._BOQ_ADAPTER, "fetch_boq", _fetch)
    client = TestClient(_app(tmp_path))
    route_response = client.get("/v1/erp/boq/proj-auth")
    assert route_response.status_code == 502
    assert (
        route_response.json()["detail"]
        == "upstream ERP returned 401 for /api/v1/boq/boqs/ (project_id=proj-auth); configure ERP authentication"
    )


def test_export_streams_generated_file(tmp_path: Path, monkeypatch):
    """Stream generated BOQ exports with the expected media type."""
    export_path = tmp_path / "boq-proj-1.csv"
    export_path.write_text("id,name\n1,Planting\n")
    monkeypatch.setattr(erp._COST_EXPORT, "export_boq", lambda project_id, fmt="xlsx": str(export_path))
    client = TestClient(_app(tmp_path))
    response = client.get("/v1/erp/export/proj-1?fmt=csv")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "Planting" in response.text


def test_export_normalizes_project_id_before_adapter_call(tmp_path: Path, monkeypatch):
    """Normalize the project id before exporting and stream the sanitized filename."""
    seen: list[tuple[str, str]] = []

    def _export(project_id: str, fmt: str = "xlsx") -> str:
        seen.append((project_id, fmt))
        export_path = tmp_path / "boq-proj-1.csv"
        export_path.write_text("id,name\n1,Planting\n")
        return str(export_path)

    monkeypatch.setattr(erp._COST_EXPORT, "export_boq", _export)
    client = TestClient(_app(tmp_path))
    response = client.get("/v1/erp/export/%20proj-1%20?fmt=csv")
    assert response.status_code == 200
    assert seen == [("proj-1", "csv")]
    assert 'filename="boq-proj-1.csv"' in response.headers["content-disposition"]


def test_export_surfaces_upstream_404(tmp_path: Path, monkeypatch):
    """Preserve upstream export 404s with a concrete blocker message."""
    request = httpx.Request("GET", "http://localhost:8080/api/boq/export?project_id=proj-404&format=csv")
    response = httpx.Response(404, request=request, json={"detail": "Not Found"})

    def _export(project_id: str, fmt: str = "xlsx") -> str:
        raise httpx.HTTPStatusError("Not Found", request=request, response=response)

    monkeypatch.setattr(erp._COST_EXPORT, "export_boq", _export)
    client = TestClient(_app(tmp_path))
    route_response = client.get("/v1/erp/export/proj-404?fmt=csv")
    assert route_response.status_code == 404
    assert (
        route_response.json()["detail"]
        == "upstream ERP returned 404 for /api/boq/export (project_id=proj-404, fmt=csv)"
    )


def test_export_surfaces_upstream_401(tmp_path: Path, monkeypatch):
    """Preserve upstream export auth failures with a concrete blocker message."""
    request = httpx.Request("GET", "https://openconstructionerp.marpa.localhost:1355/api/v1/boq/boqs/")
    response = httpx.Response(401, request=request, json={"detail": "Not authenticated"})

    def _export(project_id: str, fmt: str = "xlsx") -> str:
        raise httpx.HTTPStatusError("Unauthorized", request=request, response=response)

    monkeypatch.setattr(erp._COST_EXPORT, "export_boq", _export)
    client = TestClient(_app(tmp_path))
    route_response = client.get("/v1/erp/export/proj-auth?fmt=csv")
    assert route_response.status_code == 502
    assert (
        route_response.json()["detail"]
        == "upstream ERP returned 401 for /api/v1/boq/boqs/ (project_id=proj-auth, fmt=csv); configure ERP authentication"
    )


def test_phases_sync_requires_project_id(tmp_path: Path):
    """Reject phase-sync requests that omit the project id."""
    client = TestClient(_app(tmp_path))
    response = client.post(
        "/v1/erp/phases",
        json={},
        headers={"Idempotency-Key": "ddc-phases-sync-0001"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "project_id required"


def test_phases_sync_surfaces_schedule_granularity_blocker(tmp_path: Path):
    """Expose the concrete local schedule blocker instead of a generic stub message."""

    class _PhaseSyncPxt:
        def get_table(self, path: str):
            """Return the minimum table set needed to reach the schedule blocker."""
            if path in {"lattice/projects/proj-1/ifc_elements", "lattice/bridge/marpa_projects"}:
                return {"path": path}
            raise RuntimeError(f"table not found: {path}")

    client = TestClient(_app(tmp_path, pxt=_PhaseSyncPxt()))
    response = client.post(
        "/v1/erp/phases",
        json={"project_id": "proj-1"},
        headers={"Idempotency-Key": "ddc-phases-sync-0001"},
    )
    assert response.status_code == 501
    assert (
        response.json()["detail"]
        == "phase sync blocked: local schedule metadata is only project-level in "
        "lattice/bridge/marpa_projects (phase/start_date/end_date) and cannot express "
        "per-phase assignments for proj-1. The bounded live OpenConstructionERP schedule "
        "surface is /api/v2/schedules/{schedule_id}/import (CSV upload) plus "
        "/api/v2/schedules/tasks/{task_id}/progress (task progress JSON), so verifier "
        "data must include schedule_id/task_id rather than only project_id."
    )


def test_phases_sync_normalizes_project_id_before_adapter_call(tmp_path: Path, monkeypatch):
    """Normalize the project id before calling the phase adapter."""
    seen: list[tuple[str, object]] = []
    pxt = object()

    def _sync(project_id: str, *, pxt=None):
        seen.append((project_id, pxt))
        return {"updated": 0}

    monkeypatch.setattr(erp._PHASE_ADAPTER, "sync_phases", _sync)
    client = TestClient(_app(tmp_path, pxt=pxt))
    response = client.post(
        "/v1/erp/phases",
        json={"project_id": "  proj-1  "},
        headers={"Idempotency-Key": "ddc-phases-sync-0002"},
    )
    assert response.status_code == 200
    assert response.json()["project_id"] == "proj-1"
    assert seen == [("proj-1", pxt)]
