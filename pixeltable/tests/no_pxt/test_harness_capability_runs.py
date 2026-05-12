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
