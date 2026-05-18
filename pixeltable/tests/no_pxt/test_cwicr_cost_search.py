"""Pure-Python tests for the bounded CWICR cost-search runtime."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


def _load_cost_search():
    repo_root = Path(__file__).resolve().parents[3]
    script_path = repo_root / "ddc" / "cwicr" / "cost-search.py"
    spec = importlib.util.spec_from_file_location("cwicr_cost_search", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_search_falls_back_to_lexical_lookup_without_openai_runtime(monkeypatch) -> None:
    """Use the no-key lexical path when the restored collection lacks a matching local embed runtime."""
    cost_search = _load_cost_search()
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(
        cost_search,
        "_fetch_collection_contract",
        lambda: {"collection": "cwicr", "vector_size": 3072, "status": "green"},
    )
    monkeypatch.setattr(
        cost_search,
        "_search_lexical",
        lambda client, description, region, top: [
            {
                "item_id": "TOLI_KATO_KAKATO_KANE",
                "name": description,
                "unit": "ea",
                "unit_cost": 23733.64,
                "unit_currency": "EUR",
                "unit_cost_region": region,
                "score": 1.0,
                "retrieval_mode": "lexical",
            }
        ],
    )

    rows = cost_search.search("TOLI_KATO_KAKATO_KANE", "US", 3)

    assert rows[0]["item_id"] == "TOLI_KATO_KAKATO_KANE"
    assert rows[0]["retrieval_mode"] == "lexical"


def test_normalize_hit_maps_live_cwicr_payload() -> None:
    """Map the restored snapshot payload shape into the ERP route contract."""
    cost_search = _load_cost_search()

    class _Hit:
        id = "point-1"
        score = 0.81
        payload = {
            "metadata": {
                "doc_id": "doc-1",
                "names": "reinforced slab",
                "unit": "m2",
            },
            "payload_full": {
                "rate_code": "RATE-1",
                "rate_name": "reinforced slab",
                "rate_unit": "m2",
                "cost_summary": {
                    "total_cost_position": 47.5,
                },
            },
        }

    row = cost_search._normalize_hit(_Hit(), "US", retrieval_mode="vector")

    assert row == {
        "item_id": "RATE-1",
        "name": "reinforced slab",
        "unit": "m2",
        "unit_cost": 47.5,
        "unit_currency": cost_search.DEFAULT_UNIT_CURRENCY,
        "unit_cost_region": "US",
        "score": 0.81,
        "retrieval_mode": "vector",
    }
