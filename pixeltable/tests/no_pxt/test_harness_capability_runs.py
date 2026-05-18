"""Pure-Python tests for registered Meta-Harness capability run contracts."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from service.routes import harness


def test_python_docstring_rule_exposes_run_contract() -> None:
    """The docstring verifier row is visible as a runnable pre-flight contract."""
    capability = {"id": "python-docstring-rule"}

    action = harness.run_action(capability)
    contract = harness.run_contract(capability)

    assert action is not None
    assert action["kind"] == "script_exit_code"
    assert action["job_id"] == "python-docstring-rule"
    assert contract is not None
    assert contract["command"] == ["uv", "run", "python", "scripts/check-python-docstrings.py"]


def test_cwicr_cost_search_exposes_run_contract() -> None:
    """The CWICR verifier row exposes an allowlisted runnable proof contract."""
    capability = {"id": "cwicr-qdrant-cost-search"}

    action = harness.run_action(capability)
    contract = harness.run_contract(capability)

    assert action is not None
    assert action["kind"] == "script_exit_code"
    assert action["job_id"] == "cwicr-qdrant-cost-search"
    assert contract is not None
    assert contract["request"]["timeout_seconds"] == 120
    assert contract["command"] == ["uv", "run", "--project", "pixeltable", "python", "scripts/verify-cwicr-cost-search.py"]


def test_cwicr_seed_exposes_run_contract() -> None:
    """The CWICR seed verifier row exposes an allowlisted runnable proof contract."""
    capability = {"id": "cwicr-seed"}

    action = harness.run_action(capability)
    contract = harness.run_contract(capability)

    assert action is not None
    assert action["kind"] == "script_exit_code"
    assert action["job_id"] == "cwicr-seed"
    assert contract is not None
    assert contract["request"]["timeout_seconds"] == 120
    assert contract["command"] == ["uv", "run", "python", "scripts/verify-cwicr-seed.py"]


def test_boq_export_exposes_run_contract() -> None:
    """The BOQ export verifier row exposes an allowlisted runnable proof contract."""
    capability = {"id": "boq-export"}

    action = harness.run_action(capability)
    contract = harness.run_contract(capability)

    assert action is not None
    assert action["kind"] == "script_exit_code"
    assert action["job_id"] == "boq-export"
    assert contract is not None
    assert contract["request"]["timeout_seconds"] == 120
    assert contract["command"] == ["uv", "run", "--project", "pixeltable", "python", "scripts/verify-erp-boq-export.py"]


def test_phases_sync_exposes_run_contract() -> None:
    """The phases-sync verifier row exposes an allowlisted runnable proof contract."""
    capability = {"id": "phases-sync"}

    action = harness.run_action(capability)
    contract = harness.run_contract(capability)

    assert action is not None
    assert action["kind"] == "script_exit_code"
    assert action["job_id"] == "phases-sync"
    assert contract is not None
    assert contract["request"]["timeout_seconds"] == 120
    assert contract["command"] == ["uv", "run", "--project", "pixeltable", "python", "scripts/verify-erp-phases-sync.py"]


def test_python_docstring_rule_run_writes_evidence(
    tmp_path: Path,
    monkeypatch: Any,
) -> None:
    """The script contract persists verifier output to the requested evidence artifact."""
    calls: list[dict[str, Any]] = []

    def fake_run(
        command: list[str],
        cwd: Path,
        capture_output: bool,
        text: bool,
        check: bool,
        timeout: int,
    ) -> SimpleNamespace:
        """Record the allowlisted command instead of executing a subprocess."""
        calls.append(
            {
                "command": command,
                "cwd": cwd,
                "capture_output": capture_output,
                "text": text,
                "check": check,
                "timeout": timeout,
            }
        )
        return SimpleNamespace(returncode=0, stdout="check-python-docstrings: OK\n", stderr="")

    monkeypatch.setattr(harness, "repo_root", lambda: tmp_path)
    monkeypatch.setattr(harness.subprocess, "run", fake_run)

    result = harness.run_capability(
        {
            "capability_id": "python-docstring-rule",
            "output": "meta/harness/docs/sessions/test-python-docstring-rule.json",
            "timeout_seconds": 12,
        }
    )

    evidence_path = tmp_path / "meta/harness/docs/sessions/test-python-docstring-rule.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))

    assert calls == [
        {
            "command": ["uv", "run", "python", "scripts/check-python-docstrings.py"],
            "cwd": tmp_path,
            "capture_output": True,
            "text": True,
            "check": False,
            "timeout": 12,
        }
    ]
    assert result["ok"] is True
    assert result["artifact"] == "meta/harness/docs/sessions/test-python-docstring-rule.json"
    assert result["verification"]["status"] == "passed"
    assert evidence["capability_id"] == "python-docstring-rule"
    assert evidence["verification"]["returncode"] == 0


def test_cwicr_cost_search_run_writes_evidence(
    tmp_path: Path,
    monkeypatch: Any,
) -> None:
    """The CWICR verifier contract persists its proof artifact with the action timeout."""
    calls: list[dict[str, Any]] = []

    def fake_run(
        command: list[str],
        cwd: Path,
        capture_output: bool,
        text: bool,
        check: bool,
        timeout: int,
    ) -> SimpleNamespace:
        """Record the CWICR verifier invocation instead of executing a subprocess."""
        calls.append(
            {
                "command": command,
                "cwd": cwd,
                "capture_output": capture_output,
                "text": text,
                "check": check,
                "timeout": timeout,
            }
        )
        return SimpleNamespace(returncode=0, stdout="cwicr verifier: OK\n", stderr="")

    monkeypatch.setattr(harness, "repo_root", lambda: tmp_path)
    monkeypatch.setattr(harness.subprocess, "run", fake_run)

    result = harness.run_capability(
        {
            "capability_id": "cwicr-qdrant-cost-search",
            "output": "meta/harness/docs/sessions/test-cwicr-qdrant-cost-search.json",
        }
    )

    evidence_path = tmp_path / "meta/harness/docs/sessions/test-cwicr-qdrant-cost-search.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))

    assert calls == [
        {
            "command": ["uv", "run", "--project", "pixeltable", "python", "scripts/verify-cwicr-cost-search.py"],
            "cwd": tmp_path,
            "capture_output": True,
            "text": True,
            "check": False,
            "timeout": 120,
        }
    ]
    assert result["ok"] is True
    assert result["artifact"] == "meta/harness/docs/sessions/test-cwicr-qdrant-cost-search.json"
    assert result["verification"]["status"] == "passed"
    assert evidence["capability_id"] == "cwicr-qdrant-cost-search"
    assert evidence["verification"]["returncode"] == 0


def test_cwicr_seed_run_writes_evidence(
    tmp_path: Path,
    monkeypatch: Any,
) -> None:
    """The CWICR seed verifier contract persists its proof artifact with the action timeout."""
    calls: list[dict[str, Any]] = []

    def fake_run(
        command: list[str],
        cwd: Path,
        capture_output: bool,
        text: bool,
        check: bool,
        timeout: int,
    ) -> SimpleNamespace:
        """Record the CWICR seed verifier invocation instead of executing a subprocess."""
        calls.append(
            {
                "command": command,
                "cwd": cwd,
                "capture_output": capture_output,
                "text": text,
                "check": check,
                "timeout": timeout,
            }
        )
        return SimpleNamespace(returncode=1, stdout="", stderr='{"status":"blocked"}\n')

    monkeypatch.setattr(harness, "repo_root", lambda: tmp_path)
    monkeypatch.setattr(harness.subprocess, "run", fake_run)

    result = harness.run_capability(
        {
            "capability_id": "cwicr-seed",
            "output": "meta/harness/docs/sessions/test-cwicr-seed.json",
        }
    )

    evidence_path = tmp_path / "meta/harness/docs/sessions/test-cwicr-seed.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))

    assert calls == [
        {
            "command": ["uv", "run", "python", "scripts/verify-cwicr-seed.py"],
            "cwd": tmp_path,
            "capture_output": True,
            "text": True,
            "check": False,
            "timeout": 120,
        }
    ]
    assert result["ok"] is False
    assert result["artifact"] == "meta/harness/docs/sessions/test-cwicr-seed.json"
    assert result["verification"]["status"] == "failed"
    assert evidence["capability_id"] == "cwicr-seed"
    assert evidence["verification"]["returncode"] == 1


def test_phases_sync_run_writes_evidence(
    tmp_path: Path,
    monkeypatch: Any,
) -> None:
    """The phases-sync verifier contract persists its proof artifact with the action timeout."""
    calls: list[dict[str, Any]] = []

    def fake_run(
        command: list[str],
        cwd: Path,
        capture_output: bool,
        text: bool,
        check: bool,
        timeout: int,
    ) -> SimpleNamespace:
        """Record the phases-sync verifier invocation instead of executing a subprocess."""
        calls.append(
            {
                "command": command,
                "cwd": cwd,
                "capture_output": capture_output,
                "text": text,
                "check": check,
                "timeout": timeout,
            }
        )
        return SimpleNamespace(returncode=1, stdout="", stderr='{"status":"blocked"}\n')

    monkeypatch.setattr(harness, "repo_root", lambda: tmp_path)
    monkeypatch.setattr(harness.subprocess, "run", fake_run)

    result = harness.run_capability(
        {
            "capability_id": "phases-sync",
            "output": "meta/harness/docs/sessions/test-phases-sync.json",
        }
    )

    evidence_path = tmp_path / "meta/harness/docs/sessions/test-phases-sync.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))

    assert calls == [
        {
            "command": ["uv", "run", "--project", "pixeltable", "python", "scripts/verify-erp-phases-sync.py"],
            "cwd": tmp_path,
            "capture_output": True,
            "text": True,
            "check": False,
            "timeout": 120,
        }
    ]
    assert result["ok"] is False
    assert result["artifact"] == "meta/harness/docs/sessions/test-phases-sync.json"
    assert result["verification"]["status"] == "failed"
    assert evidence["capability_id"] == "phases-sync"
    assert evidence["verification"]["returncode"] == 1


def test_boq_export_run_writes_evidence(
    tmp_path: Path,
    monkeypatch: Any,
) -> None:
    """The BOQ export verifier contract persists its proof artifact with the action timeout."""
    calls: list[dict[str, Any]] = []

    def fake_run(
        command: list[str],
        cwd: Path,
        capture_output: bool,
        text: bool,
        check: bool,
        timeout: int,
    ) -> SimpleNamespace:
        """Record the BOQ export verifier invocation instead of executing a subprocess."""
        calls.append(
            {
                "command": command,
                "cwd": cwd,
                "capture_output": capture_output,
                "text": text,
                "check": check,
                "timeout": timeout,
            }
        )
        return SimpleNamespace(returncode=1, stdout="", stderr="upstream ERP export contract not ready\n")

    monkeypatch.setattr(harness, "repo_root", lambda: tmp_path)
    monkeypatch.setattr(harness.subprocess, "run", fake_run)

    result = harness.run_capability(
        {
            "capability_id": "boq-export",
            "output": "meta/harness/docs/sessions/test-boq-export.json",
        }
    )

    evidence_path = tmp_path / "meta/harness/docs/sessions/test-boq-export.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))

    assert calls == [
        {
            "command": ["uv", "run", "--project", "pixeltable", "python", "scripts/verify-erp-boq-export.py"],
            "cwd": tmp_path,
            "capture_output": True,
            "text": True,
            "check": False,
            "timeout": 120,
        }
    ]
    assert result["ok"] is False
    assert result["artifact"] == "meta/harness/docs/sessions/test-boq-export.json"
    assert result["verification"]["status"] == "failed"
    assert evidence["capability_id"] == "boq-export"
    assert evidence["verification"]["returncode"] == 1


def test_diagnostic_status_uses_proof_verification_semantics(tmp_path: Path) -> None:
    """Keep review-only proof artifacts amber instead of green."""
    proof_path = tmp_path / "meta/harness/docs/sessions/cwicr-proof.json"
    proof_path.parent.mkdir(parents=True, exist_ok=True)
    proof_path.write_text(
        json.dumps(
            {
                "capability_id": "cwicr-qdrant-cost-search",
                "artifact": "meta/harness/docs/sessions/cwicr-proof.json",
                "verification": {
                    "status": "review_required",
                    "message": "Top CWICR match is review-only.",
                }
            }
        ),
        encoding="utf-8",
    )

    capability = {
        "id": "cwicr-qdrant-cost-search",
        "state": "ACTIVE",
        "wired_at": ["pixeltable/service/routes/erp.py"],
        "proof_evidence": {"latest": "meta/harness/docs/sessions/cwicr-proof.json"},
    }

    status = harness.diagnostic_status(tmp_path, capability)
    assert status["color"] == "amber"
    assert status["label"] == "review-required"
    assert status["proof_verification"]["review_required"] == [
        "meta/harness/docs/sessions/cwicr-proof.json"
    ]


def test_diagnostic_status_marks_failed_verification_red(tmp_path: Path) -> None:
    """Mark failed verifier artifacts red."""
    proof_path = tmp_path / "meta/harness/docs/sessions/cwicr-proof.json"
    proof_path.parent.mkdir(parents=True, exist_ok=True)
    proof_path.write_text(
        json.dumps(
            {
                "capability_id": "cwicr-qdrant-cost-search",
                "artifact": "meta/harness/docs/sessions/cwicr-proof.json",
                "verification": {
                    "status": "failed",
                    "message": "Top CWICR match is too weak.",
                    "returncode": 1,
                }
            }
        ),
        encoding="utf-8",
    )

    capability = {
        "id": "cwicr-qdrant-cost-search",
        "state": "ACTIVE",
        "wired_at": ["pixeltable/service/routes/erp.py"],
        "proof_evidence": {"latest": "meta/harness/docs/sessions/cwicr-proof.json"},
    }

    status = harness.diagnostic_status(tmp_path, capability)
    assert status["color"] == "red"
    assert status["label"] == "fail"
    assert status["proof_verification"]["failed"] == [
        "meta/harness/docs/sessions/cwicr-proof.json"
    ]


def test_diagnostic_status_marks_legacy_json_review_required(tmp_path: Path) -> None:
    """Downgrade legacy JSON artifacts that lack verifier metadata."""
    proof_path = tmp_path / "meta/harness/docs/sessions/cwicr-proof.json"
    proof_path.parent.mkdir(parents=True, exist_ok=True)
    proof_path.write_text(json.dumps({"benchmark_name": "legacy-proof"}), encoding="utf-8")

    capability = {
        "id": "cwicr-qdrant-cost-search",
        "state": "ACTIVE",
        "wired_at": ["pixeltable/service/routes/erp.py"],
        "proof_evidence": {"latest": "meta/harness/docs/sessions/cwicr-proof.json"},
    }

    status = harness.diagnostic_status(tmp_path, capability)
    assert status["color"] == "amber"
    assert status["label"] == "review-required"
    assert status["proof_verification"]["unverified_json"] == [
        "meta/harness/docs/sessions/cwicr-proof.json"
    ]


def test_diagnostic_status_marks_malformed_json_failed(tmp_path: Path) -> None:
    """Mark malformed JSON artifacts as failed proof."""
    proof_path = tmp_path / "meta/harness/docs/sessions/cwicr-proof.json"
    proof_path.parent.mkdir(parents=True, exist_ok=True)
    proof_path.write_text("{not-json", encoding="utf-8")

    capability = {
        "id": "cwicr-qdrant-cost-search",
        "state": "ACTIVE",
        "wired_at": ["pixeltable/service/routes/erp.py"],
        "proof_evidence": {"latest": "meta/harness/docs/sessions/cwicr-proof.json"},
    }

    status = harness.diagnostic_status(tmp_path, capability)
    assert status["color"] == "red"
    assert status["label"] == "fail"
    assert status["proof_verification"]["unreadable"] == [
        "meta/harness/docs/sessions/cwicr-proof.json"
    ]


def test_diagnostic_status_marks_non_json_proof_review_required(tmp_path: Path) -> None:
    """Downgrade non-JSON proof artifacts to review-required."""
    proof_path = tmp_path / "meta/harness/docs/sessions/cwicr-proof.md"
    proof_path.parent.mkdir(parents=True, exist_ok=True)
    proof_path.write_text("# proof\n", encoding="utf-8")

    capability = {
        "id": "cwicr-qdrant-cost-search",
        "state": "ACTIVE",
        "wired_at": ["pixeltable/service/routes/erp.py"],
        "proof_evidence": {"latest": "meta/harness/docs/sessions/cwicr-proof.md"},
    }

    status = harness.diagnostic_status(tmp_path, capability)
    assert status["color"] == "amber"
    assert status["label"] == "review-required"
    assert status["proof_verification"]["non_json"] == [
        "meta/harness/docs/sessions/cwicr-proof.md"
    ]


def test_diagnostic_status_marks_forged_minimal_json_review_required(tmp_path: Path) -> None:
    """Reject minimal self-attested passed JSON as verifier-backed proof."""
    proof_path = tmp_path / "meta/harness/docs/sessions/cwicr-proof.json"
    proof_path.parent.mkdir(parents=True, exist_ok=True)
    proof_path.write_text(
        json.dumps({"verification": {"status": "passed"}}),
        encoding="utf-8",
    )

    capability = {
        "id": "cwicr-qdrant-cost-search",
        "state": "ACTIVE",
        "wired_at": ["pixeltable/service/routes/erp.py"],
        "proof_evidence": {"latest": "meta/harness/docs/sessions/cwicr-proof.json"},
    }

    status = harness.diagnostic_status(tmp_path, capability)
    assert status["color"] == "amber"
    assert status["label"] == "review-required"
    assert status["proof_verification"]["unverified_json"] == [
        "meta/harness/docs/sessions/cwicr-proof.json"
    ]


def test_diagnostic_status_marks_artifact_mismatch_review_required(tmp_path: Path) -> None:
    """Downgrade proof artifacts whose embedded path does not match the registry path."""
    proof_path = tmp_path / "meta/harness/docs/sessions/cwicr-proof.json"
    proof_path.parent.mkdir(parents=True, exist_ok=True)
    proof_path.write_text(
        json.dumps(
            {
                "capability_id": "cwicr-qdrant-cost-search",
                "artifact": "meta/harness/docs/sessions/other-proof.json",
                "verification": {
                    "status": "passed",
                    "message": "Verifier returned zero.",
                    "returncode": 0,
                },
            }
        ),
        encoding="utf-8",
    )

    capability = {
        "id": "cwicr-qdrant-cost-search",
        "state": "ACTIVE",
        "wired_at": ["pixeltable/service/routes/erp.py"],
        "proof_evidence": {"latest": "meta/harness/docs/sessions/cwicr-proof.json"},
    }

    status = harness.diagnostic_status(tmp_path, capability)
    assert status["color"] == "amber"
    assert status["label"] == "review-required"
    assert status["proof_verification"]["artifact_mismatch"] == [
        "meta/harness/docs/sessions/cwicr-proof.json"
    ]


def test_diagnostic_status_marks_capability_mismatch_review_required(tmp_path: Path) -> None:
    """Downgrade proof artifacts bound to a different capability id."""
    proof_path = tmp_path / "meta/harness/docs/sessions/cwicr-proof.json"
    proof_path.parent.mkdir(parents=True, exist_ok=True)
    proof_path.write_text(
        json.dumps(
            {
                "capability_id": "different-capability",
                "artifact": "meta/harness/docs/sessions/cwicr-proof.json",
                "verification": {
                    "status": "passed",
                    "message": "Verifier returned zero.",
                    "returncode": 0,
                },
            }
        ),
        encoding="utf-8",
    )

    capability = {
        "id": "cwicr-qdrant-cost-search",
        "state": "ACTIVE",
        "wired_at": ["pixeltable/service/routes/erp.py"],
        "proof_evidence": {"latest": "meta/harness/docs/sessions/cwicr-proof.json"},
    }

    status = harness.diagnostic_status(tmp_path, capability)
    assert status["color"] == "amber"
    assert status["label"] == "review-required"
    assert status["proof_verification"]["capability_mismatch"] == [
        "meta/harness/docs/sessions/cwicr-proof.json"
    ]


def test_normalize_report_provenance_downgrades_uploaded_self_attested_live_proof() -> None:
    """Never trust uploaded reports that self-attest as live verified proof."""
    provenance, verification = harness.normalize_report_provenance(
        {
            "benchmark_name": "forged live proof",
            "models": [],
            "provenance": {
                "source": "sidecar_live_run",
                "trust": "live_verified",
                "label": "forged",
            },
            "verification": {
                "status": "passed",
                "message": "forged",
            },
        },
        ingest_source="uploaded",
    )

    assert provenance["source"] == "uploaded"
    assert provenance["trust"] == "uploaded_unverified"
    assert verification["status"] == "unverified"
