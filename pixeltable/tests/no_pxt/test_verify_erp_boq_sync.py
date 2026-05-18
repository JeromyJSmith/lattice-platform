"""Pure-Python tests for the live BOQ sync verifier."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from service.routes import erp


def _load_verifier():
    repo_root = Path(__file__).resolve().parents[3]
    script_path = repo_root / "scripts" / "verify-erp-boq-sync.py"
    spec = importlib.util.spec_from_file_location("verify_erp_boq_sync", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_verify_route_accepts_sync_result(monkeypatch):
    """Treat sync proof as proven only when the route returns the expected success envelope."""
    verifier = _load_verifier()
    monkeypatch.setattr(
        erp._BOQ_ADAPTER,
        "sync_boq",
        lambda project_id, pxt=None: {"project_id": project_id, "rows_updated": 1},
    )

    result = verifier._verify_route("proj-1", idempotency_key="ddc-boq-sync-proof-0001")
    assert result["route"] == "/v1/erp/boq"
    assert result["status_code"] == 200


def test_probe_upstream_create_reports_401_blocker(monkeypatch):
    """Fail live proof honestly when the Portless ERP requires authentication."""
    verifier = _load_verifier()
    monkeypatch.setattr(verifier, "require_erp_runtime", lambda: SimpleNamespace(base_url="http://erp.test"))

    class _Response:
        status_code = 401
        text = '{"detail":"Not authenticated"}'
        reason_phrase = "Unauthorized"

        def json(self):
            """Return the shaped auth payload used by the verifier."""
            return {"detail": "Not authenticated"}

        def raise_for_status(self):
            """This branch should stay on the explicit 401 blocker path."""
            raise AssertionError("raise_for_status should not be called for 401 blocker path")

    monkeypatch.setattr(verifier.httpx, "post", lambda *args, **kwargs: _Response())

    with pytest.raises(RuntimeError, match="401 Not authenticated"):
        verifier._probe_upstream_create("proj-auth")


def test_resolve_project_id_falls_back_to_passed_read_proof(monkeypatch, tmp_path: Path):
    """Reuse the latest passed BOQ proof project id before attempting ERP project bootstrap."""
    verifier = _load_verifier()
    proof_path = tmp_path / "meta" / "harness" / "docs" / "sessions" / "2026-05-18-boq-read-proof.json"
    proof_path.parent.mkdir(parents=True, exist_ok=True)
    proof_path.write_text(
        json.dumps(
            {
                "stdout": json.dumps(
                    {
                        "status": "passed",
                        "project_id": "e7d28c24-c7f9-4a8e-a219-da2d52b82a73",
                    }
                )
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(verifier, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(
        verifier,
        "ensure_erp_verifier_project_id",
        lambda **kwargs: (_ for _ in ()).throw(AssertionError("should not call ERP bootstrap")),
    )

    project_id, source = verifier._resolve_project_id(None)

    assert project_id == "e7d28c24-c7f9-4a8e-a219-da2d52b82a73"
    assert source == "proof:meta/harness/docs/sessions/2026-05-18-boq-read-proof.json"


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


def test_main_reports_project_bootstrap_blocker(monkeypatch, capsys):
    """Fail with structured JSON when verifier project bootstrap cannot resolve a project id."""
    verifier = _load_verifier()
    monkeypatch.setattr(
        verifier,
        "_parse_args",
        lambda: verifier.argparse.Namespace(project_id="", idempotency_key="ddc-boq-sync-proof-0001"),
    )
    monkeypatch.setattr(verifier, "_resolve_project_id", lambda project_id: (_ for _ in ()).throw(RuntimeError("401")))

    assert verifier.main() == 1
    stderr = capsys.readouterr().err
    payload = json.loads(stderr)
    assert payload["status"] == "blocked"
    assert payload["blockers"] == ["BOQ verifier project bootstrap failed: 401"]
