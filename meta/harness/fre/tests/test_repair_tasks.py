"""Repair-task generation test for the FRE main contract slice."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "harness"))

from lib import propose_repairs_data


def test_repair_tasks() -> None:
    """A blocking failure on a lifecycle gate should produce a single, owned repair task."""

    repairs = propose_repairs_data(
        [
            {
                "gate_id": "verification",
                "status": "fail",
                "blocking": True,
                "reason": "Verification gate did not assemble required comparison evidence.",
                "evidence": [],
            }
        ]
    )
    assert len(repairs) == 1
    assert repairs[0]["blocking_gate_ids"] == ["verification"]
    assert repairs[0]["owner"] == "evaluation-agent"
