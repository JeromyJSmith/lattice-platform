from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "harness"))

from lib import check_all_schemas


def test_schema_validity() -> None:
    result = check_all_schemas()
    assert result["all_valid"] is True
    assert len(result["schemas"]) == 4
    assert all(item["issues"] == [] for item in result["schemas"])
