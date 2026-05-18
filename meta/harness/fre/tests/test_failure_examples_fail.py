"""Failure-example tests for the FRE main contract slice."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "harness"))

from lib import validate_examples_data


def test_valid_examples_pass() -> None:
    """Valid fixtures should satisfy their canonical schemas."""

    payload = validate_examples_data()
    assert all(item["status"] == "pass" for item in payload["valid_examples"])


def test_invalid_examples_fail_for_expected_reasons() -> None:
    """Invalid fixtures should fail and match the expected registry."""

    payload = validate_examples_data()
    assert all(item["status"] == "pass" for item in payload["invalid_examples"])
    assert all(item["matched_expected"] is True for item in payload["invalid_examples"])
