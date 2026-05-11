"""service.marpa_runner without any external deps (uses Python fallback)."""

from __future__ import annotations

from service import marpa_runner


def test_python_fallback_planting():
    res = marpa_runner.run_marpa(
        ["planting", "Acer", "rubrum", "15-gal", "3"]
    )
    assert res.parse_status == "success"
    assert res.runner_kind == "python.fallback"
    assert res.record is not None
    assert res.record["kind"] == "planting"
    assert res.record["botanical_name"] == "Acer rubrum"
    assert res.record["quantity"] == 3


def test_python_fallback_unknown_rule():
    res = marpa_runner.run_marpa(["lighting", "wattage", "led"])
    assert res.parse_status == "fail"
    assert res.runner_kind == "python.fallback"
    assert "unknown rule head" in res.error_message


def test_grammar_version_fallback_default():
    res = marpa_runner.run_marpa(["irrigation", "Z2", "5", "0.5GPH", "drip"])
    assert res.parse_status == "success"
    assert res.runner_kind == "python.fallback"
