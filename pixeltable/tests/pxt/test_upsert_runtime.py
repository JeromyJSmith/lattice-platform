"""Round-trip TS RuntimeEvents through service.upsert into lattice/execution."""

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


def _read_jsonl(path: Path):
    out = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def test_runtime_events_round_trip(applied, fixtures_dir: Path):
    from service.upsert import upsert_runtime_events

    events = _read_jsonl(fixtures_dir / "runtime-run-mini.jsonl")
    assert events, "fixture runtime-run-mini.jsonl is empty"
    summary = upsert_runtime_events(applied, events)
    counts = summary["counts"]

    assert counts.get("agent_threads", 0) >= 1
    assert counts.get("agent_runs", 0) >= 1


def test_runtime_events_are_idempotent(applied, fixtures_dir: Path):
    from service.upsert import upsert_runtime_events

    events = _read_jsonl(fixtures_dir / "runtime-run-mini.jsonl")
    a = upsert_runtime_events(applied, events)
    b = upsert_runtime_events(applied, events)
    # Idempotency at the upsert layer = same per-table counts.
    assert a["counts"] == b["counts"]

    runs = applied.get_table("lattice/execution/agent_runs")
    df = runs.collect()
    rows = list(df) if hasattr(df, "__iter__") else df
    seen_run_ids = {r["run_id"] for r in rows} if rows else set()
    if seen_run_ids:
        # Each run_id must appear exactly once after second upsert.
        for rid in seen_run_ids:
            count = sum(1 for r in rows if r["run_id"] == rid)
            assert count == 1, f"run_id {rid!r} duplicated: {count} rows"
