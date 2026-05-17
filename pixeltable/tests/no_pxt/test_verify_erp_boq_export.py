"""Pure-Python tests for the live BOQ export verifier."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from service.routes import erp


def _load_verifier():
    repo_root = Path(__file__).resolve().parents[3]
    script_path = repo_root / "scripts" / "verify-erp-boq-export.py"
    spec = importlib.util.spec_from_file_location("verify_erp_boq_export", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_verify_route_accepts_csv_export(tmp_path: Path, monkeypatch):
    """Treat the export route as proven only when it streams the expected CSV artifact."""
    verifier = _load_verifier()
    upstream_bytes = b"id,name\n1,Planting\n"

    class _Response:
        status_code = 200
        content = upstream_bytes

        def raise_for_status(self):
            return None

    monkeypatch.setattr(verifier.httpx, "get", lambda *args, **kwargs: _Response())

    def _export(project_id: str, fmt: str = "xlsx") -> str:
        export_path = tmp_path / "boq-proj-1.csv"
        export_path.write_bytes(upstream_bytes)
        return str(export_path)

    monkeypatch.setattr(erp._COST_EXPORT, "export_boq", _export)

    result = verifier._verify_route("proj-1", expected_bytes=upstream_bytes)
    assert result["route"] == "/v1/erp/export/proj-1?fmt=csv"
    assert result["content_type"] == "text/csv"
    assert result["filename"] == "boq-proj-1.csv"


def test_fetch_upstream_export_reports_404_blocker(monkeypatch):
    """Fail live proof honestly when the ERP export contract or verifier data is missing."""
    verifier = _load_verifier()

    class _Response:
        status_code = 404
        content = b"Not Found"

        def raise_for_status(self):
            raise AssertionError("raise_for_status should not be called for 404 blocker path")

    monkeypatch.setattr(verifier.httpx, "get", lambda *args, **kwargs: _Response())

    with pytest.raises(RuntimeError, match="live dependency or verifier project data is not ready"):
        verifier._fetch_upstream_export("proj-404")
