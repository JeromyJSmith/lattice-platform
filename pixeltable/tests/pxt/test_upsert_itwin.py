"""iTwin sync_jobs and changed_elements upsert."""

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


def test_sync_job_round_trip(applied, fixtures_dir: Path):
    from service.upsert import upsert_itwin_sync_job

    payload = json.loads((fixtures_dir / "itwin-sync-job-mini.json").read_text())
    out = upsert_itwin_sync_job(applied, payload)
    assert out["sync_run_id"] == payload["sync_run_id"]

    t = applied.get_table("lattice/bridge/itwin/itwin_sync_jobs")
    rows = list(t.collect())
    matches = [r for r in rows if r["sync_run_id"] == payload["sync_run_id"]]
    assert len(matches) == 1


def test_changed_elements_inserts_each_row(applied, fixtures_dir: Path):
    from service.upsert import upsert_itwin_changed_elements

    payload = json.loads((fixtures_dir / "itwin-changed-elements-mini.json").read_text())
    out = upsert_itwin_changed_elements(applied, payload)
    expected = len(payload.get("changed_elements", []))
    assert out["inserted"] == expected
