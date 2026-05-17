from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from service.idempotency import IdempotencyStore
from service.routes import erp


def _app(tmp_path: Path) -> FastAPI:
    app = FastAPI()
    app.state.idem = IdempotencyStore(tmp_path / ".idem.json")
    app.state.pxt = object()
    app.include_router(erp.router, prefix="/v1/erp")
    return app


def test_cost_search_requires_description(tmp_path: Path):
    client = TestClient(_app(tmp_path))
    response = client.post("/v1/erp/cost-search", json={"region": "US", "top": 3})
    assert response.status_code == 400
    assert response.json()["detail"] == "description required"


def test_cost_search_returns_rows(tmp_path: Path, monkeypatch):
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


def test_cost_search_marks_review_only_matches(tmp_path: Path, monkeypatch):
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


def test_boq_sync_returns_stub_501(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(
        erp._BOQ_ADAPTER,
        "sync_boq",
        lambda project_id, pxt=None: (_ for _ in ()).throw(NotImplementedError("boq sync pending")),
    )
    client = TestClient(_app(tmp_path))
    response = client.post(
        "/v1/erp/boq",
        json={"project_id": "proj-1"},
        headers={"Idempotency-Key": "ddc-boq-sync-0001"},
    )
    assert response.status_code == 501
    assert response.json()["detail"] == "boq sync pending"


def test_export_streams_generated_file(tmp_path: Path, monkeypatch):
    export_path = tmp_path / "boq-proj-1.csv"
    export_path.write_text("id,name\n1,Planting\n")
    monkeypatch.setattr(erp._COST_EXPORT, "export_boq", lambda project_id, fmt="xlsx": str(export_path))
    client = TestClient(_app(tmp_path))
    response = client.get("/v1/erp/export/proj-1?fmt=csv")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "Planting" in response.text
