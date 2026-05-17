from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "harness"))

from lib import cli_run_context
from lib import current_run_dir
from lib import document_contract_status
from lib import extract_bottom_matter
from lib import extract_front_matter
from lib import write_document_contract_summary


def test_extract_front_matter_from_skill_doc() -> None:
    skill_path = Path(__file__).resolve().parents[1] / "skills" / "fre-research-ratchet" / "SKILL.md"
    payload = extract_front_matter(skill_path.read_text(encoding="utf-8"))
    assert payload is not None
    assert payload["name"] == "fre-research-ratchet"
    assert "description" in payload


def test_extract_bottom_matter_from_checklist_section() -> None:
    payload = extract_bottom_matter(
        "# Example\n\n## Bottom Matter\n- [x] Contract parsed\n- [ ] Pending review\n"
    )
    assert payload is not None
    assert payload["total"] == 2
    assert payload["completed"] == 1


def test_document_contract_status_reports_front_matter() -> None:
    payload = document_contract_status()
    assert payload["status"] == "pass"
    assert payload["front_matter_count"] >= 1
    assert payload["parse_errors"] == []


def test_cli_run_context_allocates_fresh_run() -> None:
    original = os.environ.get("FRE_RUN_ID")
    try:
        os.environ.pop("FRE_RUN_ID", None)
        with cli_run_context():
            run_id = os.environ["FRE_RUN_ID"]
            assert run_id.startswith("RUN-")
            write_document_contract_summary()
            assert (current_run_dir() / "document-contract.json").exists()
            temp_run_dir = current_run_dir()
        assert "FRE_RUN_ID" not in os.environ
        shutil.rmtree(temp_run_dir, ignore_errors=True)
    finally:
        if original is not None:
            os.environ["FRE_RUN_ID"] = original
