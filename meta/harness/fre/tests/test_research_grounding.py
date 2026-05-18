"""Research-grounding test for the FRE main contract slice."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "harness"))

from lib import evaluate_data
from lib import research_grounding_status


def test_research_grounding_gate_passes() -> None:
    """Research grounding should pass on its own and as a metric in the evaluation."""

    status = research_grounding_status()
    assert status["status"] == "pass"
    payload = evaluate_data()
    metric = next(item for item in payload["metric_results"] if item["metric_id"] == "research_grounding")
    assert metric["status"] == "pass"
