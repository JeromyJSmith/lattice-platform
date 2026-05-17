from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "harness"))

from lib import propose_repairs_data


def test_repair_tasks() -> None:
    repairs = propose_repairs_data(
        [
            {
                "gate_id": "real_fixture_pressure_test",
                "status": "fail",
                "blocking": True,
                "reason": "Real fixtures have not been evaluated.",
                "evidence": [],
            }
        ]
    )
    assert len(repairs) == 1
    assert repairs[0]["blocking_gate_ids"] == ["real_fixture_pressure_test"]
    assert repairs[0]["owner"] == "evaluation-agent"
