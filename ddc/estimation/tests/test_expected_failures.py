"""Tests for the estimation expected-failures registry."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "harness"))

from lib import validate_expected_failures_data


def test_expected_failures_registry_matches_invalid_fixtures() -> None:
    """The expected-failures registry stays aligned with invalid fixtures."""

    payload = validate_expected_failures_data()
    assert payload["all_expected_failures_match"] is True
