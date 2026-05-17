from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "harness"))

from lib import validate_examples_data


def test_failure_examples_fail() -> None:
    result = validate_examples_data()
    assert all(item["status"] == "pass" for item in result["invalid_examples"])
    assert all(item["matched_expected"] is True for item in result["invalid_examples"])
