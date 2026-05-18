"""Document-contract tests for the FRE main contract slice."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "harness"))

from lib import document_contract_status
from lib import extract_bottom_matter
from lib import extract_front_matter
from lib import comparison_contract_status
from lib import read_text
from lib import validate_part_inventory


def test_extract_front_matter_from_goal_doc() -> None:
    """GOAL front matter should parse into the governed metadata shape."""

    goal_path = Path(__file__).resolve().parents[1] / "GOAL.md"
    payload = extract_front_matter(read_text(goal_path))
    assert payload is not None
    assert payload["id"] == "GOAL-FRE-MAIN-SLICE-0001"
    assert payload["doctype"] == "goal"


def test_extract_bottom_matter_from_goal_doc() -> None:
    """GOAL bottom matter should expose all lifecycle gates by gate_id."""

    goal_path = Path(__file__).resolve().parents[1] / "GOAL.md"
    payload = extract_bottom_matter(read_text(goal_path))
    assert payload is not None
    assert len(payload["gate_progress"]) == 7
    assert {item["gate_id"] for item in payload["gate_progress"]} == {
        "harvest",
        "registry",
        "manifest",
        "verification",
        "state",
        "health",
        "promotion",
    }


def test_document_contract_status_reports_clean_slice() -> None:
    """The bounded contract documents and inventory should validate together."""

    payload = document_contract_status()
    assert payload["status"] == "pass"
    assert payload["parse_errors"] == []
    assert payload["missing_front_matter"] == []
    assert payload["missing_bottom_matter"] == []
    assert payload["missing_part_paths"] == []


def test_part_inventory_paths_exist() -> None:
    """The source provenance inventory should resolve to real files."""

    payload = validate_part_inventory()
    assert payload["status"] == "pass"
    assert payload["missing_paths"] == []


def test_comparison_contract_status_reports_clean_slice() -> None:
    """Comparison-bearing surfaces should declare InfraNodus hooks explicitly."""

    payload = comparison_contract_status()
    assert payload["status"] == "pass"
    assert payload["errors"] == []
