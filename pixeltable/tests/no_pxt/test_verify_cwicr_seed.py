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
        {
            "snapshot_dimensions": [3072],
            "selected_snapshot_asset": {
                "name": verifier.SNAPSHOT_ASSET_NAME,
                "vector_size": 3072,
            },
        },
        {
            "collection": "cwicr",
            "points_count": 5,
            "vector_size": 64,
        },
    )

    assert ok is False
    assert blockers == [
        "collection 'cwicr' has 5 points; expected 49600",
        "collection 'cwicr' uses vector size 64; expected 3072",
    ]


def test_fetch_release_metadata_selects_requested_snapshot_asset(monkeypatch) -> None:
    """Bind the verifier to the bounded published snapshot that seed-qdrant restores."""
    verifier = _load_verifier()
    monkeypatch.setattr(
        verifier,
        "_fetch_json",
        lambda *_args, **_kwargs: {
            "tag_name": "v0.1.0",
            "name": "OpenConstructionEstimate-DDC-CWICR_QDRANT_CSV",
            "assets": [
                {
                    "name": verifier.SNAPSHOT_ASSET_NAME,
                    "size": 958134272,
                    "browser_download_url": "https://example.invalid/hi.snapshot",
                },
                {
                    "name": "ENG_TORONTO_workitems_costs_resources_EMBEDDINGS_3072_DDC_CWICR.snapshot",
                    "size": 1046672896,
                    "browser_download_url": "https://example.invalid/en.snapshot",
                },
            ],
        },
    )

    release = verifier._fetch_release_metadata()

    assert release["snapshot_asset_count"] == 2
    assert release["snapshot_dimensions"] == [3072]
    assert release["selected_snapshot_asset"] == {
        "name": verifier.SNAPSHOT_ASSET_NAME,
        "size": 958134272,
        "browser_download_url": "https://example.invalid/hi.snapshot",
        "vector_size": 3072,
    }


def test_main_reports_structured_blockers(monkeypatch, capsys) -> None:
    """Emit machine-readable blocker output when release and collection contracts diverge."""
    verifier = _load_verifier()
    monkeypatch.setattr(
        verifier,
        "_parse_args",
        lambda: verifier.argparse.Namespace(collection="cwicr", restore_if_needed=False),
    )
    monkeypatch.setattr(
        verifier,
        "_fetch_release_metadata",
        lambda: {
            "tag_name": "v0.1.0",
            "snapshot_dimensions": [3072],
            "snapshot_asset_count": 7,
            "selected_snapshot_asset": {
                "name": verifier.SNAPSHOT_ASSET_NAME,
                "vector_size": 3072,
            },
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
        lambda collection, **_kwargs: {
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
        "collection 'cwicr' has 5 points; expected 49600",
        "collection 'cwicr' uses vector size 64; expected 3072",
    ]
    assert payload["expected"]["snapshot_asset_name"] == verifier.SNAPSHOT_ASSET_NAME


def test_main_passes_when_collection_matches_release_contract(monkeypatch, capsys) -> None:
    """Treat the seed as proven only when vector size and point count match the live release contract."""
    verifier = _load_verifier()
    monkeypatch.setattr(
        verifier,
        "_parse_args",
        lambda: verifier.argparse.Namespace(collection="cwicr", restore_if_needed=False),
    )
    monkeypatch.setattr(
        verifier,
        "_fetch_release_metadata",
        lambda: {
            "tag_name": "v0.1.0",
            "snapshot_dimensions": [3072],
            "snapshot_asset_count": 7,
            "selected_snapshot_asset": {
                "name": verifier.SNAPSHOT_ASSET_NAME,
                "vector_size": 3072,
            },
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
        lambda collection, **_kwargs: {
            "collection": collection,
            "points_count": 49600,
            "vector_size": 3072,
        },
    )

    assert verifier.main() == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "passed"
    assert payload["collection_state"]["points_count"] == 49600
    assert payload["collection_state"]["vector_size"] == 3072


def test_main_restores_snapshot_when_collection_is_stubbed(monkeypatch, capsys) -> None:
    """Attempt the bounded restore path before declaring the seed blocked."""
    verifier = _load_verifier()
    probe_results = iter(
        [
            {
                "collection": "cwicr",
                "points_count": 5,
                "vector_size": 64,
            },
            {
                "collection": "cwicr",
                "points_count": 49600,
                "vector_size": 3072,
            },
        ]
    )
    monkeypatch.setattr(
        verifier,
        "_parse_args",
        lambda: verifier.argparse.Namespace(collection="cwicr", restore_if_needed=True),
    )
    monkeypatch.setattr(
        verifier,
        "_fetch_release_metadata",
        lambda: {
            "tag_name": "v0.1.0",
            "snapshot_dimensions": [3072],
            "snapshot_asset_count": 7,
            "selected_snapshot_asset": {
                "name": verifier.SNAPSHOT_ASSET_NAME,
                "vector_size": 3072,
                "browser_download_url": "https://example.invalid/hi.snapshot",
            },
        },
    )
    monkeypatch.setattr(
        verifier,
        "_probe_health",
        lambda: {"health_endpoint": "/healthz"},
    )
    monkeypatch.setattr(verifier, "_probe_collection", lambda *_args, **_kwargs: next(probe_results))
    monkeypatch.setattr(verifier, "_delete_collection", lambda collection: collection == "cwicr")
    monkeypatch.setattr(
        verifier,
        "_recover_snapshot",
        lambda *_args, **_kwargs: {"result": True, "status": "ok"},
    )

    assert verifier.main() == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "passed"
    assert payload["restore"] == {
        "attempted": True,
        "snapshot_asset_name": verifier.SNAPSHOT_ASSET_NAME,
        "deleted_existing_collection": True,
        "recover_response": {"result": True, "status": "ok"},
    }
