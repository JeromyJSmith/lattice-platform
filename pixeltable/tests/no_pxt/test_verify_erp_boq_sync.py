"""Pure-Python tests for the live BOQ sync verifier."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest


def _load_verifier():
    repo_root = Path(__file__).resolve().parents[3]
    script_path = repo_root / "scripts" / "verify-erp-boq-sync.py"
    spec = importlib.util.spec_from_file_location("verify_erp_boq_sync", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_verify_route_reports_precise_blocker():
    """Treat sync proof as failed until the route stops returning the BOQ blocker."""
    verifier = _load_verifier()

    with pytest.raises(RuntimeError, match="project IFC rows are not ready"):
        verifier._verify_route("proj-1", idempotency_key="ddc-boq-sync-proof-0001")


def test_probe_upstream_create_reports_404_blocker(monkeypatch):
    """Fail live proof honestly when the upstream BOQ create contract is missing."""
    verifier = _load_verifier()
    monkeypatch.setattr(verifier, "require_erp_runtime", lambda: SimpleNamespace(base_url="http://erp.test"))

    class _Response:
        status_code = 404

        def raise_for_status(self):
            """This branch should stay on the explicit 404 blocker path."""
            raise AssertionError("raise_for_status should not be called for 404 blocker path")

    monkeypatch.setattr(verifier.httpx, "post", lambda *args, **kwargs: _Response())

    with pytest.raises(RuntimeError, match="live ERP create contract is not ready"):
        verifier._probe_upstream_create("proj-404")


def test_main_reports_combined_blockers(monkeypatch, capsys):
    """Emit structured blocker output when either upstream or route proof is not ready."""
    verifier = _load_verifier()
    monkeypatch.setattr(
        verifier,
        "_parse_args",
        lambda: verifier.argparse.Namespace(
            project_id="proj-1",
            idempotency_key="ddc-boq-sync-proof-0001",
        ),
    )
    monkeypatch.setattr(
        verifier,
        "_probe_upstream_create",
        lambda project_id: (_ for _ in ()).throw(RuntimeError("upstream 404")),
    )
    monkeypatch.setattr(
        verifier,
        "_verify_route",
        lambda project_id, idempotency_key: (_ for _ in ()).throw(RuntimeError("route blocked")),
    )

    assert verifier.main() == 1
    stderr = capsys.readouterr().err
    payload = json.loads(stderr)
    assert payload["status"] == "blocked"
    assert payload["blockers"] == ["upstream 404", "route blocked"]
