"""Pure-Python tests for the live BOQ read verifier."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace

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


def test_fetch_upstream_json_reports_401_blocker(monkeypatch):
    """Fail live proof honestly when the Portless ERP requires authentication."""
    verifier = _load_verifier()
    monkeypatch.setattr(verifier, "require_erp_runtime", lambda: SimpleNamespace(base_url="http://erp.test"))

    class _Response:
        status_code = 401

        def json(self):
            """Return the shaped auth payload used by the verifier."""
            return {"detail": "Not authenticated"}

        text = '{"detail":"Not authenticated"}'
        reason_phrase = "Unauthorized"

    monkeypatch.setattr(verifier.httpx, "get", lambda *args, **kwargs: _Response())

    with pytest.raises(RuntimeError, match="401 Not authenticated"):
        verifier._fetch_upstream_json("proj-auth")
