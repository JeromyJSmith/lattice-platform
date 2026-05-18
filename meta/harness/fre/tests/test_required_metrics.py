"""Required-metrics test for the FRE main contract slice."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "harness"))

from lib import REQUIRED_METRICS
from lib import evaluate_data
from lib import read_json
from lib import schema_path
from lib import validate_instance


def test_required_metrics() -> None:
    """The fre-loop fixture and the evaluation scorecard should expose the required metric set."""

    payload = read_json(Path(__file__).resolve().parents[1] / "examples" / "fre-loop.valid.json")
    assert set(payload["metrics"]) == REQUIRED_METRICS

    result = evaluate_data()
    assert set(result["scorecard"]["required_metrics"]) == REQUIRED_METRICS

    schema_failures = validate_instance("fre-loop.schema.json", payload)
    assert schema_failures == []
    assert schema_path("fre-loop.schema.json").exists()
