"""Translation-map tests for the FRE main contract slice."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "harness"))

from lib import REQUIRED_MAPPING_ROWS
from lib import mapping_rows


def test_lattice_mapping_rows_match_contract() -> None:
    """The translation map should keep the required row statuses stable."""

    assert mapping_rows() == REQUIRED_MAPPING_ROWS
