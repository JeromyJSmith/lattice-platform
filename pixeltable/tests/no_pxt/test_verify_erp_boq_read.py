"""Pure-Python tests for the live BOQ read verifier."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from service.routes import erp


def _load_verifier():
    repo_root = Path(__file__).resolve().parents[3]
    script_path = repo_root / "scripts" / "verify-erp-boq-read.py"
    spec = importlib.util.spec_from_file_location("verify_erp_boq_read", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_verify_route_accepts_boq_document(monkeypatch):
    """Treat the BOQ route as proven only when it returns the expected envelope."""
    verifier = _load_verifier()
    monkeypatch.setattr(
        erp._BOQ_ADAPTER,
        "fetch_boq",
        lambda project_id: {
            "ok": True,
            "project_id": project_id,
            "erp_base": verifier.ERP_BASE,
            "boq": {"items": []},
        },
    )

    result = verifier._verify_route("proj-1")
    assert result["route"] == "/v1/erp/boq/proj-1"
    assert result["payload_kind"] == "object"
    assert result["erp_base"] == verifier.ERP_BASE


def test_fetch_upstream_json_reports_404_blocker(monkeypatch):
    """Fail live proof honestly when the ERP BOQ contract or verifier data is missing."""
    verifier = _load_verifier()

    class _Response:
        status_code = 404

        def raise_for_status(self):
            """Should never run for the explicit 404 blocker path."""
            raise AssertionError("raise_for_status should not be called for 404 blocker path")

        def json(self):
            """Return the shaped 404 payload used by the verifier."""
            return {"detail": "Not Found"}

    monkeypatch.setattr(verifier.httpx, "get", lambda *args, **kwargs: _Response())

    with pytest.raises(RuntimeError, match="live dependency or verifier project data is not ready"):
        verifier._fetch_upstream_json("proj-404")
