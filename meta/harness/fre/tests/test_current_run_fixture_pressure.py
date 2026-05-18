"""Fixture-pressure test for the FRE main contract slice."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "harness"))

from lib import current_run_dir
from lib import evaluate_data
from lib import write_real_fixture_evaluation_artifacts


def test_current_run_fixture_pressure_uses_current_run_artifacts() -> None:
    """Setting FRE_RUN_ID should produce a real-fixture record that the evaluator reports as pass."""

    original = os.environ.get("FRE_RUN_ID")
    os.environ["FRE_RUN_ID"] = "RUN-2026-05-18-0001"
    try:
        write_real_fixture_evaluation_artifacts()
        payload = evaluate_data()
        metric = next(item for item in payload["metric_results"] if item["metric_id"] == "real_fixture_pressure_test")
        assert metric["status"] == "pass"
        assert f"runs/{os.environ['FRE_RUN_ID']}/real-fixture-evaluation.json" in metric["evidence"]
        assert (current_run_dir() / "real-fixture-evaluation.json").exists()
    finally:
        shutil.rmtree(current_run_dir(), ignore_errors=True)
        if original is None:
            os.environ.pop("FRE_RUN_ID", None)
        else:
            os.environ["FRE_RUN_ID"] = original
