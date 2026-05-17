#!/usr/bin/env -S uv run python
"""Validate the current Farber-Haines estimation and georef workflow state."""

from __future__ import annotations

import csv
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent.parent
sys.path.insert(0, str(_HERE.parent))

from scripts._pxt_env import get_client  # noqa: E402


PROJECT_ID = "farber-haines-2521"
PROJECT_GEOREF_TABLE = "lattice/bridge/project_georef"
SUMMARY_TABLE = f"lattice/projects/{PROJECT_ID}/vw_estimate_rows"
OBJECT_TABLE = f"lattice/projects/{PROJECT_ID}/vw_estimate_objects"

WORKING_COPY_VWX = _REPO_ROOT / "projects/vectorworks project files/_Farber-Haines [2521]__ESTIMATION_WORKING_COPY__2026-05-16.vwx"
PROJECT_GEOREF_SEED = _REPO_ROOT / "projects/farber-haines-2521/georef.config.seed.json"
PROJECT_GEOREF_EVIDENCE = _REPO_ROOT / "projects/farber-haines-2521/georef.evidence.register.json"
PROJECT_GEOREF_ARTIFACTS = _REPO_ROOT / "projects/farber-haines-2521/artifacts/georef"
REPORT_JSON = _REPO_ROOT / "docs/farber-haines-workflow-validation-report.json"
REPORT_MD = _REPO_ROOT / "docs/farber-haines-workflow-validation-report.md"

FILES_TO_CHECK = {
    "summary_csv": Path("/Users/ojeromyo/Desktop/vw_cost_estimate_summary.csv"),
    "object_csv": Path("/Users/ojeromyo/Desktop/vw_cost_estimate_object_rows.csv"),
    "mapping_csv": Path("/Users/ojeromyo/Desktop/vw_class_budget_mapping_first_pass.csv"),
    "project_georef_seed": PROJECT_GEOREF_SEED,
    "project_georef_evidence": PROJECT_GEOREF_EVIDENCE,
    "binding_json": Path("/Volumes/PixelTable/GROVE_HARNESS/juniper2026/georef/document_georef_binding.json"),
    "control_points_json": Path("/Volumes/PixelTable/GROVE_HARNESS/juniper2026/georef/control_points_wgs84_provisional.json"),
    "georef_audit_json": Path("/Volumes/PixelTable/GROVE_HARNESS/juniper2026/data/vw_extract/_audit_georeference_last_run.json"),
    "ifc_audit_json": Path("/Volumes/PixelTable/GROVE_HARNESS/juniper2026/data/vw_extract/_audit_ifc_assignment_last_run.json"),
    "ifc_project_props_json": Path("/Volumes/PixelTable/GROVE_HARNESS/juniper2026/data/vw_extract/_audit_ifc_project_props_last_run.json"),
    "ifc_project_properties_csv": Path("/Volumes/PixelTable/GROVE_HARNESS/juniper2026/data/vw_exports/farber-haines-2521/ifc_project_properties.csv"),
    "ifc_export_result": Path("/tmp/farber_haines_ifc_probe/export_result.json"),
    "ifc_probe_file": Path("/tmp/farber_haines_ifc_probe/farber_haines_probe_20260516T231627Z.ifc"),
    "ifc_diag_json": Path("/Users/ojeromyo/Desktop/fh_ifc_diag.json"),
    "ifc4x3_export_file": _REPO_ROOT / "_Farber-Haines [2521]__ESTIMATION_WORKING_COPY__2026-05-16.ifc",
    "ifc4x3_assessment_json": _REPO_ROOT / "docs/farber-haines-ifc-export-assessment.json",
    "ifc4x3_assessment_md": _REPO_ROOT / "docs/farber-haines-ifc-export-assessment.md",
    "fit_json": Path("/tmp/farber_haines_georef_fit.json"),
    "fit_binding_candidate": Path("/tmp/farber_haines_georef_binding_candidate.json"),
    "cycle_report_json": Path("/tmp/farber_haines_georef_cycle_report.json"),
    "selected_reference_json": PROJECT_GEOREF_ARTIFACTS / "farber_haines_selected_reference_points.json",
    "selected_reference_csv": PROJECT_GEOREF_ARTIFACTS / "farber_haines_selected_reference_points.csv",
    "point_pairs_working": PROJECT_GEOREF_ARTIFACTS / "farber_haines_point_pairs_working.json",
    "authoritative_point_pairs": _REPO_ROOT / "projects/farber-haines-2521/sources/farber_haines_point_pairs_authoritative_template.json",
    "authoritative_georef_source_summary": _REPO_ROOT / "projects/farber-haines-2521/sources/farber_haines_authoritative_georef_sources_summary.json",
    "trellis_server": Path("/Volumes/PixelTable/MARPA_918_JUNIPER/experiments/trees_sage/trellis_server.py"),
    "trellis_html": Path("/Volumes/PixelTable/MARPA_918_JUNIPER/experiments/trees_sage/trellis.html"),
    "trellis_outputs_dir": Path("/Volumes/PixelTable/MARPA_918_JUNIPER/experiments/trees_sage/trellis_outputs"),
    "phase1_extract": Path("/Volumes/PixelTable/MARPA_918_JUNIPER/src/python/extract/phase1_extract.py"),
    "viewer_dir": Path("/Volumes/PixelTable/MARPA_918_JUNIPER/viewer"),
    "estimation_brief": _REPO_ROOT / "docs/farber-haines-vectorworks-estimation-brief.md",
    "record_export_matrix": _REPO_ROOT / "docs/farber-haines-record-export-matrix.md",
    "georef_lock_plan": _REPO_ROOT / "docs/farber-haines-georef-lock-plan.md",
    "georef_live_sequence": _REPO_ROOT / "docs/farber-haines-georef-live-update-sequence.md",
    "henry_meeting_focus": _REPO_ROOT / "docs/farber-haines-henry-meeting-focus.md",
}


@dataclass
class Check:
    status: str
    summary: str
    details: list[str]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any] | list[Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def csv_row_count(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open(newline="", encoding="utf-8") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def path_status(path: Path) -> dict[str, Any]:
    return {
        "path": str(path),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else 0,
    }


def fetch_first(table: Any, predicate: Any) -> dict[str, Any] | None:
    rows = list(table.where(predicate).limit(1).collect())
    return rows[0] if rows else None


def fetch_count(table: Any, predicate: Any) -> int:
    return len(list(table.where(predicate).collect()))


def collect_live_state() -> dict[str, Any]:
    pxt = get_client()
    project_georef_table = pxt.get_table(PROJECT_GEOREF_TABLE)
    summary_table = pxt.get_table(SUMMARY_TABLE)
    object_table = pxt.get_table(OBJECT_TABLE)

    georef_row = fetch_first(project_georef_table, project_georef_table.project_id == PROJECT_ID)
    summary_rows = fetch_count(summary_table, summary_table.project_id == PROJECT_ID)
    object_rows = fetch_count(object_table, object_table.project_id == PROJECT_ID)
    sample_summary = fetch_first(summary_table, summary_table.project_id == PROJECT_ID)
    sample_object = fetch_first(object_table, object_table.project_id == PROJECT_ID)

    return {
        "project_georef_row": georef_row,
        "summary_row_count": summary_rows,
        "object_row_count": object_rows,
        "sample_summary_row": sample_summary,
        "sample_object_row": sample_object,
    }


def evaluate_pricing(live: dict[str, Any], files: dict[str, dict[str, Any]]) -> Check:
    summary_rows = live["summary_row_count"]
    object_rows = live["object_row_count"]
    summary_csv_rows = csv_row_count(FILES_TO_CHECK["summary_csv"])
    object_csv_rows = csv_row_count(FILES_TO_CHECK["object_csv"])
    details = [
        f"Pixeltable summary rows: {summary_rows}",
        f"Pixeltable object rows: {object_rows}",
        f"Summary CSV rows: {summary_csv_rows}",
        f"Object CSV rows: {object_csv_rows}",
    ]
    if summary_rows > 0 and object_rows > 0 and files["summary_csv"]["exists"] and files["object_csv"]["exists"]:
        return Check("pass", "Pricing and estimate exports are live in Pixeltable and on disk.", details)
    if summary_rows > 0:
        return Check("warn", "Grouped estimate pricing is live, but object-level coverage is incomplete.", details)
    return Check("fail", "Estimate ingestion is not yet proven live.", details)


def evaluate_georef_seed(live: dict[str, Any], files: dict[str, dict[str, Any]], binding: dict[str, Any] | None) -> Check:
    row = live["project_georef_row"] or {}
    control_points_doc = load_json(FILES_TO_CHECK["control_points_json"]) or {}
    control_points = list((control_points_doc or {}).get("control_points") or [])
    details = [
        f"Live project_georef row present: {bool(row)}",
        f"EPSG code: {row.get('epsg_code') or ''}",
        f"Control points in seed: {len(control_points)}",
        f"Binding status: {(binding or {}).get('binding_status') or 'missing'}",
    ]
    if row and row.get("epsg_code") and len(control_points) >= 4:
        status = "pass" if binding and binding.get("binding_status") != "unresolved" else "warn"
        summary = "Project georef seed is live in Pixeltable." if status == "pass" else "Project georef seed is live, but the document binding is still unresolved."
        return Check(status, summary, details)
    return Check("fail", "Project georef seed is incomplete or missing.", details)


def evaluate_vw_binding(live: dict[str, Any], binding: dict[str, Any] | None, georef_audit: dict[str, Any] | None) -> Check:
    row = live["project_georef_row"] or {}
    transform = row.get("transform_vw_to_wgs84") or ""
    details = [
        f"Binding status: {(binding or {}).get('binding_status') or 'missing'}",
        f"Allow apply: {(binding or {}).get('allow_apply')}",
        f"VW origin X: {row.get('vw_origin_x')}",
        f"VW origin Y: {row.get('vw_origin_y')}",
        f"VW scale: {row.get('vw_scale')}",
        f"VW rotation deg: {row.get('vw_rotation_deg')}",
        f"Transform present: {bool(transform)}",
        f"Document georeferenced: {((georef_audit or {}).get('row') or {}).get('document_georeferenced')}",
        f"Review reason: {((georef_audit or {}).get('row') or {}).get('review_reason') or ''}",
    ]
    if binding and binding.get("binding_status") == "unresolved":
        return Check("fail", "Vectorworks-to-world binding is still unresolved.", details)
    if transform:
        return Check("pass", "Vectorworks transform has been solved and written back.", details)
    return Check("warn", "Vectorworks transform path exists, but no solved fit is live yet.", details)


def evaluate_survey(files: dict[str, dict[str, Any]], live: dict[str, Any]) -> Check:
    row = live["project_georef_row"] or {}
    has_survey_csv = bool(row.get("has_survey_csv"))
    cycle_report = load_json(FILES_TO_CHECK["cycle_report_json"]) or {}
    details = [
        f"Survey CSV applied live: {has_survey_csv}",
        f"Survey file path: {row.get('survey_file_path') or ''}",
        f"Selected reference JSON present: {files['selected_reference_json']['exists']}",
        f"Point-pairs working JSON present: {files['point_pairs_working']['exists']}",
        f"Fit JSON present: {files['fit_json']['exists']}",
        f"Cycle report present: {files['cycle_report_json']['exists']}",
        f"Cycle report error: {(cycle_report or {}).get('error') or ''}",
    ]
    if has_survey_csv and files["fit_json"]["exists"]:
        return Check("pass", "Survey control and fit artifacts are both present.", details)
    if has_survey_csv or files["selected_reference_json"]["exists"]:
        return Check("warn", "Survey/point capture path exists, but the full solved control chain is incomplete.", details)
    return Check("fail", "No live survey-control solve has been applied yet.", details)


def evaluate_georef_operator(files: dict[str, dict[str, Any]]) -> Check:
    cycle_report = load_json(FILES_TO_CHECK["cycle_report_json"]) or {}
    details = [
        f"Authoritative point-pair package present: {files['authoritative_point_pairs']['exists']}",
        f"Authoritative source summary present: {files['authoritative_georef_source_summary']['exists']}",
        f"Selected reference JSON present: {files['selected_reference_json']['exists']}",
        f"Cycle report present: {files['cycle_report_json']['exists']}",
        f"Cycle report ok: {(cycle_report or {}).get('ok')}",
        f"Cycle report error: {(cycle_report or {}).get('error') or ''}",
    ]
    if files["selected_reference_json"]["exists"] and files["fit_json"]["exists"]:
        return Check("pass", "Georef operator path has live selected-reference and fit artifacts.", details)
    if files["cycle_report_json"]["exists"] and "missing selected reference export" in str((cycle_report or {}).get("error") or ""):
        return Check("warn", "Georef operator path is healthy and fail-closed, but waiting on a real Vectorworks selected-reference export.", details)
    if files["authoritative_point_pairs"]["exists"]:
        return Check("warn", "Georef operator scaffolding is present, but current runner status is incomplete.", details)
    return Check("fail", "Georef operator path is not fully in place.", details)


def evaluate_ifc(
    files: dict[str, dict[str, Any]],
    ifc_export: dict[str, Any] | None,
    ifc_audit: dict[str, Any] | None,
    ifc_diag: dict[str, Any] | None,
    ifc4x3_assessment: dict[str, Any] | None,
) -> Check:
    audit_status = ((ifc_audit or {}).get("by_mapping_status") or {})
    diag_sections = ifc_diag or {}
    direct_failures = 0
    for values in diag_sections.values():
        if isinstance(values, list):
            direct_failures += sum(1 for item in values if not item.get("set2") and not item.get("set1"))
    current_schema = (ifc4x3_assessment or {}).get("schema") or ""
    current_crs = ((ifc4x3_assessment or {}).get("projected_crs") or {}).get("epsg_code") or ""
    current_issues = list((ifc4x3_assessment or {}).get("issues") or [])
    current_geo = ((ifc4x3_assessment or {}).get("entity_counts") or {}).get("IFCGEOGRAPHICELEMENT", 0)
    details = [
        f"IFC export result ok: {bool((ifc_export or {}).get('ok'))}",
        f"IFC file present: {files['ifc_probe_file']['exists']}",
        f"Current working-copy IFC4x3 export present: {files['ifc4x3_export_file']['exists']}",
        f"Current working-copy IFC schema: {current_schema}",
        f"Current working-copy IFC projected CRS EPSG: {current_crs}",
        f"Current working-copy IFC IfcGeographicElement count: {current_geo}",
        f"Mapped objects in audit: {audit_status.get('ok', 0)}",
        f"Unmapped objects in audit: {audit_status.get('unmapped', 0)}",
        f"Direct IFC setter failures sampled: {direct_failures}",
    ]
    if current_issues:
        details.extend(f"Current working-copy IFC issue: {issue}" for issue in current_issues)
    if not ifc_export and not files["ifc4x3_export_file"]["exists"]:
        return Check("fail", "IFC export is not currently proven.", details)
    if current_issues or audit_status.get("unmapped", 0) > audit_status.get("ok", 0) or direct_failures > 0:
        return Check("warn", "IFC export runs, but the current working-copy export still has CRS, semantic typing, or custom-property payload gaps.", details)
    return Check("pass", "IFC export and semantic mapping both look healthy.", details)


def evaluate_ifc_project_settings(files: dict[str, dict[str, Any]]) -> Check:
    summary = load_json(FILES_TO_CHECK["ifc_project_props_json"]) or {}
    missing_required = list((summary or {}).get("missing_required") or [])
    fields_read = int((summary or {}).get("fields_read") or 0)
    georef = (summary or {}).get("document_georeferenced")
    details = [
        f"IFC project-properties summary present: {files['ifc_project_props_json']['exists']}",
        f"IFC project-properties CSV present: {files['ifc_project_properties_csv']['exists']}",
        f"IFC project fields read: {fields_read}",
        f"IFC project required fields missing: {len(missing_required)}",
        f"IFC project document_georeferenced snapshot: {georef}",
    ]
    if files["ifc_project_props_json"]["exists"] and files["ifc_project_properties_csv"]["exists"]:
        if missing_required:
            return Check("warn", "IFC project export dialog has been audited, but required project/site/georef fields are still missing.", details)
        return Check("pass", "IFC project export dialog settings have been audited with no required-field gaps.", details)
    return Check("warn", "IFC project export dialog settings are still un-audited for Farber-Haines.", details)


def evaluate_plant_assets(files: dict[str, dict[str, Any]]) -> Check:
    details = [
        f"TRELLIS server present: {files['trellis_server']['exists']}",
        f"TRELLIS UI present: {files['trellis_html']['exists']}",
        f"TRELLIS outputs dir present: {files['trellis_outputs_dir']['exists']}",
        f"Phase1 extract present: {files['phase1_extract']['exists']}",
        f"Viewer dir present: {files['viewer_dir']['exists']}",
    ]
    if all(files[name]["exists"] for name in ("trellis_server", "trellis_html", "trellis_outputs_dir", "phase1_extract", "viewer_dir")):
        return Check("pass", "Local plant 3D asset pipeline surfaces are present on disk.", details)
    if any(files[name]["exists"] for name in ("trellis_server", "phase1_extract", "viewer_dir")):
        return Check("warn", "Plant 3D asset lane exists, but some expected local surfaces are missing.", details)
    return Check("fail", "Local plant 3D asset pipeline surfaces are not currently present.", details)


def evaluate_docs(files: dict[str, dict[str, Any]]) -> Check:
    required = [
        "estimation_brief",
        "record_export_matrix",
        "georef_lock_plan",
        "georef_live_sequence",
        "henry_meeting_focus",
    ]
    missing = [name for name in required if not files[name]["exists"]]
    details = [f"{name}: {files[name]['exists']}" for name in required]
    if not missing:
        return Check("pass", "Presentation and operator docs are in place.", details)
    return Check("warn", "Some meeting/operator docs are missing.", details)


def determine_top_gap(checks: dict[str, Check], live: dict[str, Any]) -> str:
    if checks["vw_binding"].status == "fail":
        return (
            "Solve the Vectorworks-to-world binding from real survey corners/stakes, then write the fit back to "
            "`lattice.bridge.project_georef`. That is the highest-value blocker because Cesium/iTwin alignment, "
            "IFC georef trust, and downstream overlay validation all depend on it."
        )
    if checks["ifc"].status != "pass":
        return (
            "Broaden IFC semantic coverage after georef is locked. The export runs, but most objects are still "
            "unmapped and plant/tree/boulder families are not sticking through the direct setter path."
        )
    if checks["pricing"].status != "pass":
        return (
            "Repair the estimate ingest path so grouped and object-level pricing are both live and current in Pixeltable."
        )
    row = live["project_georef_row"] or {}
    return (
        f"Current highest-value gap is no longer structural. Next slice is controlled validation against Cesium/iTwin "
        f"with the latest `project_georef` row version `{row.get('config_version') or 'unknown'}`."
    )


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Farber-Haines Workflow Validation Report",
        "",
        f"- Generated at: `{report['generated_at']}`",
        f"- Project: `{report['project_id']}`",
        f"- Working copy: `{report['working_copy_vwx']}`",
        "",
        "## Overall",
        "",
        f"- Overall status: `{report['overall_status']}`",
        f"- Highest-value gap: {report['highest_value_gap']}",
        "",
        "## Checks",
        "",
    ]
    for name, check in report["checks"].items():
        lines.append(f"### {name}")
        lines.append("")
        lines.append(f"- Status: `{check['status']}`")
        lines.append(f"- Summary: {check['summary']}")
        for detail in check["details"]:
            lines.append(f"- {detail}")
        lines.append("")
    lines.extend([
        "## Live Pixeltable",
        "",
        f"- `project_georef` row present: `{report['live']['project_georef_present']}`",
        f"- `vw_estimate_rows` count: `{report['live']['summary_row_count']}`",
        f"- `vw_estimate_objects` count: `{report['live']['object_row_count']}`",
        f"- `project_georef` config version: `{report['live']['project_georef_config_version']}`",
        "",
        "## Artifacts",
        "",
    ])
    for name, file_info in report["files"].items():
        lines.append(f"- `{name}`: exists=`{file_info['exists']}` path=`{file_info['path']}`")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    files = {name: path_status(path) for name, path in FILES_TO_CHECK.items()}
    live = collect_live_state()
    binding = load_json(FILES_TO_CHECK["binding_json"])
    georef_audit = load_json(FILES_TO_CHECK["georef_audit_json"])
    ifc_export = load_json(FILES_TO_CHECK["ifc_export_result"])
    ifc_audit = load_json(FILES_TO_CHECK["ifc_audit_json"])
    ifc_diag = load_json(FILES_TO_CHECK["ifc_diag_json"])

    checks = {
        "pricing": evaluate_pricing(live, files),
        "georef_seed": evaluate_georef_seed(live, files, binding if isinstance(binding, dict) else None),
        "vw_binding": evaluate_vw_binding(live, binding if isinstance(binding, dict) else None, georef_audit if isinstance(georef_audit, dict) else None),
        "survey_control": evaluate_survey(files, live),
        "georef_operator": evaluate_georef_operator(files),
        "ifc": evaluate_ifc(
            files,
            ifc_export if isinstance(ifc_export, dict) else None,
            ifc_audit if isinstance(ifc_audit, dict) else None,
            ifc_diag if isinstance(ifc_diag, dict) else None,
            load_json(FILES_TO_CHECK["ifc4x3_assessment_json"]) if FILES_TO_CHECK["ifc4x3_assessment_json"].exists() else None,
        ),
        "ifc_project_settings": evaluate_ifc_project_settings(files),
        "plant_assets": evaluate_plant_assets(files),
        "docs": evaluate_docs(files),
    }

    statuses = [check.status for check in checks.values()]
    overall_status = "fail" if "fail" in statuses else "warn" if "warn" in statuses else "pass"
    highest_value_gap = determine_top_gap(checks, live)

    report = {
        "generated_at": now_iso(),
        "project_id": PROJECT_ID,
        "working_copy_vwx": str(WORKING_COPY_VWX),
        "overall_status": overall_status,
        "highest_value_gap": highest_value_gap,
        "checks": {
            name: {
                "status": check.status,
                "summary": check.summary,
                "details": check.details,
            }
            for name, check in checks.items()
        },
        "live": {
            "project_georef_present": bool(live["project_georef_row"]),
            "project_georef_config_version": (live["project_georef_row"] or {}).get("config_version") or "",
            "summary_row_count": live["summary_row_count"],
            "object_row_count": live["object_row_count"],
            "sample_summary_row": live["sample_summary_row"],
            "sample_object_row": live["sample_object_row"],
        },
        "files": files,
    }

    REPORT_JSON.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "report_json": str(REPORT_JSON),
        "report_md": str(REPORT_MD),
        "overall_status": overall_status,
        "highest_value_gap": highest_value_gap,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
