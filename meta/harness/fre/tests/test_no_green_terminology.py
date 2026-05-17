from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "harness"))

from lib import forbidden_term_violations


def test_no_green_terminology() -> None:
    assert forbidden_term_violations() == []
