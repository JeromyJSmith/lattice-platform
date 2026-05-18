"""Pure-Python tests for the governed Juniper quantity-takeoff runtime."""

from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_runtime():
    repo_root = Path(__file__).resolve().parents[3]
    module_path = repo_root / "ddc" / "estimation" / "quantity_takeoff_runtime.py"
    spec = importlib.util.spec_from_file_location("quantity_takeoff_runtime", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_extract_quantities_filters_to_juniper_scope() -> None:
    """Return only the governed Juniper rows from the shared fixture table."""
    runtime = _load_runtime()
    result = runtime.extract_quantities(runtime.DEFAULT_PROJECT_ID, pxt=runtime.VerifierPxt())

    assert result["project_id"] == runtime.DEFAULT_PROJECT_ID
    assert result["row_count"] == 2
    assert result["total_quantity"] == 15.5
    assert [row["source_element_id"] for row in result["rows"]] == [
        "ifc-juniper-001",
        "ifc-juniper-002",
    ]


def test_run_quantity_takeoff_proof_captures_boq_linked_evidence(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Treat the governed quantity path as passed only when Juniper rows stay enriched and BOQ-linked."""
    runtime = _load_runtime()

    monkeypatch.setattr(
        runtime,
        "_run_boq_read",
        lambda client, project_id: {
            "project_id": project_id,
            "boq_count": 1,
            "erp_base": "https://erp.test",
        },
    )
    monkeypatch.setattr(
        runtime,
        "_run_boq_export",
        lambda client, project_id: {
            "project_id": project_id,
            "content_type": "text/csv",
            "content_length": 64,
            "filename": "boq-918-juniper.csv",
        },
    )
    monkeypatch.setattr(
        runtime,
        "_resolve_erp_project_id",
        lambda: ("e7d28c24-c7f9-4a8e-a219-da2d52b82a73", "test"),
    )

    original_sync = runtime.erp._BOQ_ADAPTER.sync_boq

    def _fake_sync(project_id: str, pxt=None):
        assert project_id == "e7d28c24-c7f9-4a8e-a219-da2d52b82a73"
        assert pxt is not None
        for row in pxt.table.rows:
            if row.get("project_id") == project_id:
                row["erp_item_id"] = f"erp-{row['source_element_id']}"
        return {"boq_id": "boq-1", "rows_updated": 2}

    monkeypatch.setattr(runtime.erp._BOQ_ADAPTER, "sync_boq", _fake_sync)
    try:
        result = runtime.run_quantity_takeoff_proof(tmp_path)
    finally:
        monkeypatch.setattr(runtime.erp._BOQ_ADAPTER, "sync_boq", original_sync)

    assert result["status"] == "passed"
    assert result["project_target"] == "MARPA — 918 Juniper Avenue"
    assert result["steps"]["quantity_extract"]["row_count"] == 2
    assert len(result["steps"]["cost_search_writeback"]) == 2
    assert result["steps"]["boq_sync"]["result"]["rows_updated"] == 2
    assert [row["erp_item_id"] for row in result["evidence"]["ifc_rows"]] == [
        "erp-ifc-juniper-001",
        "erp-ifc-juniper-002",
    ]
