from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "harness"))

from lib import evaluate_data
from lib import research_grounding_status


def test_research_grounding_gate_passes() -> None:
    status = research_grounding_status()
    assert status["status"] == "pass"
    payload = evaluate_data()
    gate = next(item for item in payload["gate_results"] if item["gate_id"] == "research_grounding")
    assert gate["status"] == "pass"
