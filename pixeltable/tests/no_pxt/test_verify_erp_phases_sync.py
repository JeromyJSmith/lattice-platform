"""Pure-Python tests for the live phases-sync verifier."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest


def _load_verifier():
    repo_root = Path(__file__).resolve().parents[3]
    script_path = repo_root / "scripts" / "verify-erp-phases-sync.py"
    spec = importlib.util.spec_from_file_location("verify_erp_phases_sync", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_verify_route_reports_precise_schedule_blocker():
    """Treat phase sync proof as failed until the route stops returning the schedule blocker."""
    verifier = _load_verifier()

    class _RowsTable:
        def __init__(self, rows):
            self._rows = rows

        def collect(self):
            """Return the synthetic table rows."""
            return list(self._rows)

    class _PhaseSyncPxt:
        def __init__(self):
            self._tables = {
                "lattice/bridge/ifc/ifc_elements": _RowsTable([{"source_element_id": "ifc-1"}]),
                "lattice/bridge/marpa_projects": _RowsTable([]),
            }

        def get_table(self, path: str):
            """Return one synthetic table handle."""
            if path not in self._tables:
                raise RuntimeError(f"table not found: {path}")
            return self._tables[path]

    verifier._resolve_phase_sync_pxt = lambda: _PhaseSyncPxt()

    with pytest.raises(RuntimeError, match="rows do not expose project_id"):
        verifier._verify_route("ddc-phases-proof-project", idempotency_key="ddc-phases-sync-proof-0001")


def test_probe_upstream_phase_endpoint_reports_404_blocker(monkeypatch):
    """Fail live proof honestly when the upstream phase endpoint is missing."""
    verifier = _load_verifier()
    monkeypatch.setattr(verifier, "require_erp_runtime", lambda: SimpleNamespace(base_url="http://erp.test"))

    class _Response:
        status_code = 404
        headers = {"content-type": "application/json"}

    monkeypatch.setattr(verifier.httpx, "get", lambda *args, **kwargs: _Response())

    with pytest.raises(RuntimeError, match="live ERP phase endpoint contract is not ready"):
        verifier._probe_upstream_phase_endpoint("proj-404")


def test_probe_upstream_phase_endpoint_accepts_live_404_405_mix(monkeypatch):
    """Treat the live Portless schedule probe mix as reachable bounded evidence, not an upstream blocker."""

    verifier = _load_verifier()
    monkeypatch.setattr(verifier, "require_erp_runtime", lambda: SimpleNamespace(base_url="https://erp.test"))

    responses = iter(
        [
            SimpleNamespace(status_code=404, headers={"content-type": "application/json"}),
            SimpleNamespace(status_code=405, headers={"content-type": "application/json"}),
        ]
    )
    monkeypatch.setattr(verifier.httpx, "get", lambda *args, **kwargs: next(responses))

    result = verifier._probe_upstream_phase_endpoint("proj-live")

    assert result["project_id"] == "proj-live"
    assert result["schedules_status_code"] == 404
    assert result["links_status_code"] == 405


def test_main_reports_combined_blockers(monkeypatch, capsys):
    """Emit structured blocker output when either upstream or route proof is not ready."""
    verifier = _load_verifier()
    monkeypatch.setattr(
        verifier,
        "_parse_args",
        lambda: verifier.argparse.Namespace(
            project_id="proj-1",
            idempotency_key="ddc-phases-sync-proof-0001",
        ),
    )
    monkeypatch.setattr(
        verifier,
        "_probe_local_phase_sync_seam",
        lambda project_id: {
            "project_id": project_id,
            "ready": False,
            "blockers": ["missing schedule_id/task_id"],
        },
    )
    monkeypatch.setattr(
        verifier,
        "_probe_upstream_phase_endpoint",
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
    assert payload["local_seam_probe"]["blockers"] == ["missing schedule_id/task_id"]
