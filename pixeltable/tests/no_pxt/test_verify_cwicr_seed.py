"""Pure-Python tests for the live CWICR seed verifier."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


def _load_verifier():
    repo_root = Path(__file__).resolve().parents[3]
    script_path = repo_root / "scripts" / "verify-cwicr-seed.py"
    spec = importlib.util.spec_from_file_location("verify_cwicr_seed", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_evaluate_seed_contract_reports_count_and_vector_blockers() -> None:
    """Fail live proof honestly when the target collection is just a demo stub."""
    verifier = _load_verifier()

    ok, blockers = verifier._evaluate_seed_contract(
        {"snapshot_dimensions": [3072]},
        {
            "collection": "cwicr",
            "points_count": 5,
            "vector_size": 64,
        },
    )

    assert ok is False
    assert blockers == [
        "collection 'cwicr' has 5 points; expected 55719",
        "collection 'cwicr' uses vector size 64; expected 3072",
    ]


def test_main_reports_structured_blockers(monkeypatch, capsys) -> None:
    """Emit machine-readable blocker output when release and collection contracts diverge."""
    verifier = _load_verifier()
    monkeypatch.setattr(
        verifier,
        "_parse_args",
        lambda: verifier.argparse.Namespace(collection="cwicr"),
    )
    monkeypatch.setattr(
        verifier,
        "_fetch_release_metadata",
        lambda: {
            "tag_name": "v0.1.0",
            "snapshot_dimensions": [3072],
            "snapshot_asset_count": 7,
        },
    )
    monkeypatch.setattr(
        verifier,
        "_probe_health",
        lambda: {"health_endpoint": "/healthz"},
    )
    monkeypatch.setattr(
        verifier,
        "_probe_collection",
        lambda collection: {
            "collection": collection,
            "points_count": 5,
            "vector_size": 64,
        },
    )

    assert verifier.main() == 1
    payload = json.loads(capsys.readouterr().err)
    assert payload["status"] == "blocked"
    assert payload["collection"] == "cwicr"
    assert payload["blockers"] == [
        "collection 'cwicr' has 5 points; expected 55719",
        "collection 'cwicr' uses vector size 64; expected 3072",
    ]


def test_main_passes_when_collection_matches_release_contract(monkeypatch, capsys) -> None:
    """Treat the seed as proven only when vector size and point count match the live release contract."""
    verifier = _load_verifier()
    monkeypatch.setattr(
        verifier,
        "_parse_args",
        lambda: verifier.argparse.Namespace(collection="cwicr"),
    )
    monkeypatch.setattr(
        verifier,
        "_fetch_release_metadata",
        lambda: {
            "tag_name": "v0.1.0",
            "snapshot_dimensions": [3072],
            "snapshot_asset_count": 7,
        },
    )
    monkeypatch.setattr(
        verifier,
        "_probe_health",
        lambda: {"health_endpoint": "/healthz"},
    )
    monkeypatch.setattr(
        verifier,
        "_probe_collection",
        lambda collection: {
            "collection": collection,
            "points_count": 55719,
            "vector_size": 3072,
        },
    )

    assert verifier.main() == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "passed"
    assert payload["collection_state"]["points_count"] == 55719
    assert payload["collection_state"]["vector_size"] == 3072
