"""Tests for estimation source and traceability truth."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "harness"))

from lib import source_packet_status
from lib import traceability_contract_status


def test_source_packet_preserves_juniper_and_lineage_truth() -> None:
    """The source packet preserves Juniper target and pilot lineage truth."""

    payload = source_packet_status()
    assert payload["status"] == "pass"
    assert payload["errors"] == []


def test_traceability_contract_is_present_for_valid_fixtures() -> None:
    """Valid fixtures keep workbook, formula, and source traceability intact."""

    payload = traceability_contract_status()
    assert payload["status"] == "pass"
    assert payload["errors"] == []
