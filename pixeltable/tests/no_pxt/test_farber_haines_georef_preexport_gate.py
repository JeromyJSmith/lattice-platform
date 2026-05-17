from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
GATE_PATH = ROOT / "georef/converters/farber_haines_georef_preexport_gate.py"
GATE_SPEC = importlib.util.spec_from_file_location("farber_haines_georef_preexport_gate", GATE_PATH)
assert GATE_SPEC is not None and GATE_SPEC.loader is not None
GATE_MODULE = importlib.util.module_from_spec(GATE_SPEC)
GATE_SPEC.loader.exec_module(GATE_MODULE)
evaluate_gate = GATE_MODULE.evaluate_gate
parse_epsg_from_projection_text = GATE_MODULE.parse_epsg_from_projection_text


def live_selected_payload() -> dict:
    return {
        "export_kind": "vectorworks_selected_reference_points",
        "export_version": 2,
        "project_id": "farber-haines-2521",
        "source_vwx": str(ROOT / "projects/vectorworks project files/_Farber-Haines [2521]__ESTIMATION_WORKING_COPY__2026-05-16.vwx"),
        "source_vwx_basename": "_Farber-Haines [2521]__ESTIMATION_WORKING_COPY__2026-05-16.vwx",
        "selected_count": 1,
        "object_signature_sha256": "a" * 64,
        "objects": [
            {
                "object_uuid": "0D0F1AA4-5A64-4605-A6B8-1725FF90CA8C",
                "name": "NW parcel corner",
                "class_name": "Site-PropertyBoundary",
                "layer_name": "Design Layer-1",
                "center_point": {"x": 100.0, "y": 200.0},
            }
        ],
    }


def passing_inputs() -> dict:
    return {
        "project_id": "farber-haines-2521",
        "expected_epsg_code": 3857,
        "doc_snapshot": {
            "document_is_georeferenced": True,
            "gis_origin": {"x": 799.467963, "y": -717.274797},
            "epsg_code": 3857,
        },
        "selected_payload": live_selected_payload(),
        "cycle_report": {"ok": True, "apply_performed": True},
        "binding_artifact": {"allow_apply": True, "binding_status": "runtime_apply", "epsg_code": 3857},
        "fit_report": {"fit_rmse_project_units": 0.25, "fit_max_residual_project_units": 0.5},
    }


def test_gate_passes_when_doc_binding_selection_and_fit_are_valid():
    result = evaluate_gate(passing_inputs())

    assert result["ok"] is True
    assert result["block_reasons"] == []


def test_gate_blocks_when_vectorworks_document_is_not_georeferenced():
    inputs = passing_inputs()
    inputs["doc_snapshot"]["document_is_georeferenced"] = False

    result = evaluate_gate(inputs)

    assert result["ok"] is False
    assert "document_not_georeferenced" in result["block_reasons"]


def test_gate_blocks_synthetic_selected_reference_payloads():
    inputs = passing_inputs()
    inputs["selected_payload"]["export_version"] = "v1-recreated-from-pixeltable"
    inputs["selected_payload"]["object_signature_sha256"] = "recreated-from-pixeltable-georef-control-points"
    inputs["selected_payload"]["objects"][0]["object_uuid"] = "recreated-parcel-boundary-001"

    result = evaluate_gate(inputs)

    assert result["ok"] is False
    assert "selected_reference_export_not_live_vectorworks_payload" in result["block_reasons"]


def test_gate_blocks_expected_epsg_mismatch():
    inputs = passing_inputs()
    inputs["doc_snapshot"]["epsg_code"] = 2876

    result = evaluate_gate(inputs)

    assert result["ok"] is False
    assert "document_epsg_mismatch:expected=3857,actual=2876" in result["block_reasons"]


def test_gate_blocks_unapproved_binding_even_with_good_fit():
    inputs = passing_inputs()
    inputs["cycle_report"] = {"ok": True, "apply_performed": False}
    inputs["binding_artifact"] = {"allow_apply": False, "binding_status": "candidate", "epsg_code": 3857}

    result = evaluate_gate(inputs)

    assert result["ok"] is False
    assert "binding_not_approved_for_export" in result["block_reasons"]


def test_gate_blocks_fit_residuals_over_threshold():
    inputs = passing_inputs()
    inputs["fit_report"] = {"fit_rmse_project_units": 0.25, "fit_max_residual_project_units": 25.0}

    result = evaluate_gate(inputs, max_residual=15.0)

    assert result["ok"] is False
    assert "fit_max_residual_too_high:25.0>15.0" in result["block_reasons"]


def test_projection_wkt_parser_uses_top_level_projected_crs_authority():
    wkt = (
        'PROJCS["WGS 84 / Pseudo-Mercator",'
        'GEOGCS["WGS 84",DATUM["WGS_1984",'
        'SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],'
        'AUTHORITY["EPSG","6326"]],AUTHORITY["EPSG","4326"]],'
        'UNIT["metre",1,AUTHORITY["EPSG","9001"]],AUTHORITY["EPSG","3857"]]'
    )

    assert parse_epsg_from_projection_text(wkt) == 3857
