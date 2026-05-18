"""Forbidden-terminology test for the FRE main contract slice."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "harness"))

from lib import forbidden_term_violations


def test_no_green_terminology() -> None:
    """FRE-managed surfaces should not carry green-state terminology like definition_of_green."""

    assert forbidden_term_violations() == []
