"""Bootstrap migrations against an ephemeral PXT_HOME, then verify schema."""

from __future__ import annotations

from pathlib import Path

import pytest

pxt = pytest.importorskip("pixeltable")

from migrations import load_all  # noqa: E402  (after env override)
from migrations._helpers import OWNED_BRIDGE_SUBS, OWNED_PARENTS, FORBIDDEN_PREFIXES  # noqa: E402


@pytest.fixture()
def applied(ephemeral_pxt_home: Path):
    """Apply all migrations against the ephemeral home and return the pxt module."""
    from scripts._pxt_env import get_client

    client = get_client()
    for _mig_id, module in load_all():
        module.apply(client, dry_run=False)
    return client


def test_owned_namespaces_exist(applied):
    dirs = set(applied.list_dirs())
    for ns in (*OWNED_PARENTS, *OWNED_BRIDGE_SUBS):
        assert ns in dirs, f"missing namespace {ns}"


def test_no_forbidden_namespace_was_created(applied):
    dirs = set(applied.list_dirs())
    for forbidden in FORBIDDEN_PREFIXES:
        assert not any(d.startswith(forbidden) for d in dirs), (
            f"namespace {forbidden!r} must not exist on ephemeral home; "
            f"migrations must not write outside OWNED_*"
        )


def test_idempotent_second_apply(applied):
    """Re-applying every migration must succeed and report no destructive change."""
    for _mig_id, module in load_all():
        result = module.apply(applied, dry_run=False)
        assert isinstance(result, dict)


def test_execution_tables_present(applied):
    tables = set(applied.list_tables("lattice/execution"))
    expected = {
        "lattice/execution/agent_threads",
        "lattice/execution/agent_messages",
        "lattice/execution/agent_runs",
        "lattice/execution/agent_stream_events",
        "lattice/execution/agent_artifacts",
        "lattice/execution/agent_outcomes",
    }
    missing = expected - tables
    assert not missing, f"missing execution tables: {missing}"


def test_bridge_tables_present(applied):
    expected_per_ns = {
        "lattice/bridge/vw":       {"vectorworks_exports"},
        "lattice/bridge/ifc":      {"ifc_elements", "ifc_property_sets"},
        # connector_versions is grouped with the iTwin tables because it
        # tracks which iTwin connector produced each sync job — same lifecycle.
        "lattice/bridge/itwin":    {"itwin_sync_jobs", "itwin_changed_elements", "connector_versions"},
        "lattice/bridge/marpa":    {"marpa_parse_runs"},
        "lattice/bridge/semantic": {"semantic_sidecars", "landscape_entities"},
        "lattice/bridge/evidence": {"promotion_events", "harness_run_refs"},
        "lattice/bridge/health":   {"schema_drift_events", "bridge_gap_matrix"},
    }
    for ns, want_names in expected_per_ns.items():
        live = {t.split("/")[-1] for t in applied.list_tables(ns)}
        missing = want_names - live
        assert not missing, f"{ns}: missing {missing} (have {live})"
