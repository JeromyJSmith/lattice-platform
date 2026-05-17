from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "harness"))

from lib import build_determinism_check


def test_determinism_check_passes() -> None:
    payload = build_determinism_check()
    assert payload["status"] == "pass"
    assert payload["comparisons"]["first"] == payload["comparisons"]["second"]
