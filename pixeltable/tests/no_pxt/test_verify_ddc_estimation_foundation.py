"""Pure-Python tests for promoted DDC estimation verification semantics."""

from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_verifier():
    repo_root = Path(__file__).resolve().parents[3]
    script_path = repo_root / "scripts" / "verify-ddc-estimation-foundation.py"
    spec = importlib.util.spec_from_file_location("verify_ddc_estimation_foundation", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_quantity_report_passes_when_governed_runtime_and_dependencies_are_green(monkeypatch) -> None:
    """Promote quantity-takeoff only when the governed runtime and helper states are all green."""
    verifier = _load_verifier()
    monkeypatch.setattr(verifier, "_verify_alignment", lambda: [])
    monkeypatch.setattr(
        verifier,
        "_yaml_capability",
        lambda path, capability_id: {
            "status": "green",
            "state": "ACTIVE",
        },
    )
    monkeypatch.setattr(
        verifier,
        "run_quantity_takeoff_proof",
        lambda root, idempotency_key="ddc-quantity-takeoff-proof-0001": {
            "status": "passed",
            "project_id": "918-juniper",
            "supported_by": verifier.QUANTITY_SUPPORTED_BY,
        },
    )

    exit_code, report = verifier._quantity_report()

    assert exit_code == 0
    assert report["status"] == "passed"
    assert report["dependency_status"]["ifc-cost-enrichment"] == "green"
    assert report["dependency_status"]["boq-sync"] == "green"


def test_contract_report_passes_when_helper_proofs_and_quantity_runtime_pass(monkeypatch) -> None:
    """Promote the estimation contract only when the full supported helper set and quantity proof are green."""
    verifier = _load_verifier()
    monkeypatch.setattr(verifier, "_verify_alignment", lambda: [])

    def _yaml_capability(path, capability_id):
        if path == verifier.REGISTRY_PATH:
            return {
                "state": "ACTIVE",
                "supported_by": verifier.CONTRACT_SUPPORTED_IDS,
                "blocking_capabilities": [],
                "project_target": verifier.PROJECT_TARGET,
                "proof_lineage": [verifier.ROSE_LINEAGE, verifier.FARBER_LINEAGE],
            }
        if capability_id == "ddc-estimation-contract":
            return {
                "status": "green",
                "supported_by": verifier.CONTRACT_SUPPORTED_IDS,
                "blocked_by": [],
                "project_target": verifier.PROJECT_TARGET,
            }
        return {"status": "green"}

    monkeypatch.setattr(verifier, "_yaml_capability", _yaml_capability)
    monkeypatch.setattr(verifier, "_proof_status", lambda path: "passed")
    monkeypatch.setattr(
        verifier,
        "run_quantity_takeoff_proof",
        lambda root, idempotency_key="ddc-estimation-contract-proof-0001": {
            "status": "passed",
            "project_id": "918-juniper",
            "supported_by": verifier.QUANTITY_SUPPORTED_BY,
        },
    )

    exit_code, report = verifier._contract_report()

    assert exit_code == 0
    assert report["status"] == "passed"
    assert report["supported_by"] == verifier.CONTRACT_SUPPORTED_IDS
    assert report["blocked_by"] == []
