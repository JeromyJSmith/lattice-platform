"""Pure-Python tests for the bounded IFC cost-enrichment verifier."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


def _load_verifier():
    repo_root = Path(__file__).resolve().parents[3]
    script_path = repo_root / "scripts" / "verify-ifc-cost-enrichment.py"
    spec = importlib.util.spec_from_file_location("verify_ifc_cost_enrichment", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_verify_route_passes_for_juniper_writeback() -> None:
    """Treat the bounded Juniper writeback proof as passed only when the target row mutates."""
    verifier = _load_verifier()

    result = verifier._verify_route()

    assert result["route"] == "/v1/erp/cost-search"
    assert result["project_id"] == "918-juniper"
    assert result["writeback"]["status"] == "passed"
    assert result["writeback"]["rows_updated"] == 1


def test_main_reports_structured_blockers(monkeypatch, capsys) -> None:
    """Emit machine-readable blocker output when the writeback proof cannot pass."""
    verifier = _load_verifier()
    monkeypatch.setattr(
        verifier,
        "_verify_route",
        lambda: (_ for _ in ()).throw(RuntimeError("Juniper IFC rows missing")),
    )

    assert verifier.main() == 1
    payload = json.loads(capsys.readouterr().err)
    assert payload["status"] == "blocked"
    assert payload["blockers"] == ["Juniper IFC rows missing"]
