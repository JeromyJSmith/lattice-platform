"""Tests for estimation contract schema validity."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "harness"))

from lib import check_all_schemas


def test_estimation_contract_schemas_are_valid() -> None:
    """All estimation schemas stay Draft 2020-12 valid."""

    payload = check_all_schemas()
    assert payload["all_valid"] is True
