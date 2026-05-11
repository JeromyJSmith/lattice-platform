"""End-to-end MARPA: run_marpa(tokens) -> upsert_marpa_parse_run."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

pxt = pytest.importorskip("pixeltable")

from migrations import load_all  # noqa: E402


@pytest.fixture()
def applied(ephemeral_pxt_home: Path):
    from scripts._pxt_env import get_client

    client = get_client()
    for _mig_id, module in load_all():
        module.apply(client, dry_run=False)
    return client


def test_marpa_run_then_upsert_writes_row(applied, fixtures_dir: Path):
    from service.marpa_runner import run_marpa
    from service.upsert import upsert_marpa_parse_run

    payload = json.loads((fixtures_dir / "marpa-parse-run-mini.json").read_text())
    tokens = payload["input_tokens"]
    res = run_marpa(tokens)

    enriched = {
        **payload,
        "parse_status":       res.parse_status,
        "ambiguity_score":    res.ambiguity_score,
        "partial_parse_json": res.record,
        "error_message":      res.error_message,
        "runner_kind":        res.runner_kind,
    }
    out = upsert_marpa_parse_run(applied, enriched)
    assert out["parse_run_id"]

    t = applied.get_table("lattice/bridge/marpa/marpa_parse_runs")
    rows = list(t.collect())
    matches = [r for r in rows if r["parse_run_id"] == out["parse_run_id"]]
    assert len(matches) == 1
    assert matches[0]["parse_status"] in {"success", "partial", "fail"}
    assert matches[0]["runner_kind"] == "python.fallback"
