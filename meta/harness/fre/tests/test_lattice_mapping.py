from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "harness"))

from lib import REQUIRED_MAPPING_ROWS
from lib import mapping_rows


def test_lattice_mapping() -> None:
    assert mapping_rows() == REQUIRED_MAPPING_ROWS
