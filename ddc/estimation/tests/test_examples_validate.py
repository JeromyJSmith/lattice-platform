"""Tests for bounded estimation fixture validation."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "harness"))

from lib import validate_examples_data


def test_valid_estimation_fixtures_pass() -> None:
    """Every valid estimation fixture passes its contract schema."""

    payload = validate_examples_data()
    assert all(item["status"] == "pass" for item in payload["valid_examples"])


def test_invalid_estimation_fixtures_fail_for_expected_reasons() -> None:
    """Every invalid estimation fixture fails with the expected reason set."""

    payload = validate_examples_data()
    assert all(item["status"] == "pass" for item in payload["invalid_examples"])
    assert all(item["matched_expected"] is True for item in payload["invalid_examples"])
