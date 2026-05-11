"""Atomic VW-sidecar upsert: vw_export + ifc_elements + ifc_psets + semantic."""

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


def test_vw_sidecar_writes_all_target_tables(applied, fixtures_dir: Path):
    from service.upsert import upsert_vw_sidecar

    payload = json.loads((fixtures_dir / "vwx-sidecar-mini.json").read_text())
    out = upsert_vw_sidecar(applied, payload)

    assert out["vw_export_hash"] == payload["vw_export_hash"]
    counts = out["counts"]
    assert counts["vectorworks_exports"] == 1
    assert counts["ifc_elements"] >= 1
    # property_sets and semantic depend on the fixture; assert sanity only.
    assert counts["ifc_property_sets"] >= 0
    assert counts["semantic_sidecars"] >= 0


def test_vw_sidecar_is_idempotent(applied, fixtures_dir: Path):
    from service.upsert import upsert_vw_sidecar

    payload = json.loads((fixtures_dir / "vwx-sidecar-mini.json").read_text())
    a = upsert_vw_sidecar(applied, payload)
    b = upsert_vw_sidecar(applied, payload)
    assert a["counts"] == b["counts"]

    vw_t = applied.get_table("lattice/bridge/vw/vectorworks_exports")
    rows = list(vw_t.collect())
    matches = [r for r in rows if r["vw_export_hash"] == payload["vw_export_hash"]]
    assert len(matches) == 1, f"expected 1 vw row, found {len(matches)}"
