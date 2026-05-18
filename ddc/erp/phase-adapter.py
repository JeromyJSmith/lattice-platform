#!/usr/bin/env python3
"""Bridge: project IFC rows + local schedule metadata → OpenConstructionERP phases."""

from __future__ import annotations

import csv
import datetime as dt
import io
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if REPO_ROOT.as_posix() not in sys.path:
    sys.path.insert(0, REPO_ROOT.as_posix())

from ddc.erp.project_seams import (
    BRIDGE_IFC_TABLE,
    PROJECT_IFC_TABLE_TEMPLATE,
    require_pxt_handle,
    require_table,
    resolve_project_ifc_surface,
)
from ddc.erp.runtime import ensure_erp_verifier_project_id, erp_client, require_erp_runtime, resolve_erp_runtime

BRIDGE_PROJECTS_TABLE = "lattice/bridge/marpa_projects"
PROJECT_GEOREF_TABLE = "lattice/bridge/project_georef"
ERP_SCHEDULES_PATH = "/api/v1/schedule/schedules/"
ERP_SCHEDULE_ACTIVITIES_PATH_TEMPLATE = "/api/v1/schedule/schedules/{schedule_id}/activities/"
ERP_SCHEDULE_IMPORT_PATH_TEMPLATE = "/api/v2/schedules/{schedule_id}/import"
ERP_TASK_PROGRESS_PATH_TEMPLATE = "/api/v2/schedules/tasks/{task_id}/progress"
PROJECT_LEVEL_SCHEDULE_FIELDS = ("phase", "start_date", "end_date", "erp_project_id")
PHASE_IDENTIFIER_FIELDS = ("schedule_id", "task_id")
DEFAULT_VERIFY_PROJECT_ID = "ddc-phases-proof-project"
DEFAULT_VERIFY_PHASE_NAME = "Verifier Phase A"
DEFAULT_VERIFY_START_DATE = "2026-05-01"
DEFAULT_VERIFY_END_DATE = "2026-05-31"
DEFAULT_VERIFY_PROJECT_NAME = "LATTICE Phases Verifier Project"
DEFAULT_VERIFY_PROJECT_CODE = "LATTICE-PHASES-001"
ERP_RUNTIME = resolve_erp_runtime()

PROJECT_SHADOW_SCHEMA = (
    ("id", "String"),
    ("project_id", "String"),
    ("source_element_id", "String"),
    ("ifc_class", "String"),
    ("ifc_predefined_type", "String"),
    ("ifc_schema", "String"),
    ("name", "String"),
    ("long_name", "String"),
    ("object_type", "String"),
    ("tag", "String"),
    ("description", "String"),
    ("spatial_container_guid", "String"),
    ("spatial_container_class", "String"),
    ("bbox_min", "Json"),
    ("bbox_max", "Json"),
    ("centroid", "Json"),
    ("elevation_m", "Float"),
    ("is_marpa_seed", "Bool"),
    ("raw_attributes", "Json"),
    ("parsed_at", "String"),
    ("boq_phase", "String"),
    ("quantity", "Float"),
    ("quantity_unit", "String"),
    ("erp_item_id", "String"),
    ("unit_cost", "Float"),
    ("unit_cost_region", "String"),
    ("cost_last_updated", "Timestamp"),
    ("raw_event", "Json"),
)


def _normalize_project_id(project_id: str) -> str:
    normalized_project_id = project_id.strip()
    if not normalized_project_id:
        raise ValueError("project_id required")
    return normalized_project_id


def _as_row_dict(row: Any) -> dict[str, Any]:
    if isinstance(row, dict):
        return row
    try:
        return dict(row)
    except Exception as exc:
        raise RuntimeError(f"phase sync expected Pixeltable rows as mappings; got {type(row).__name__}") from exc


def _collect_rows(table: Any, *, table_path: str, blocker: str) -> list[dict[str, Any]]:
    collect = getattr(table, "collect", None)
    if not callable(collect):
        raise NotImplementedError(f"{blocker} {table_path} does not expose collect() for seam inspection.")
    try:
        return [_as_row_dict(row) for row in collect()]
    except Exception as exc:
        raise NotImplementedError(f"{blocker} {table_path} rows are not collectable for seam inspection.") from exc


def _row_keys(rows: list[dict[str, Any]]) -> set[str]:
    return {key for row in rows for key in row.keys()}


def _row_value(row: dict[str, Any], key: str) -> Any:
    if key in row and row.get(key) is not None:
        return row.get(key)
    raw_event = row.get("raw_event")
    if isinstance(raw_event, dict) and raw_event.get(key) is not None:
        return raw_event.get(key)
    return None


def _has_non_empty_value(row: dict[str, Any], key: str) -> bool:
    value = _row_value(row, key)
    if isinstance(value, str):
        return bool(value.strip())
    return value is not None


def _surface_label(ifc_surface: dict[str, Any]) -> str:
    return ifc_surface["path"] + (
        " (bridge source-of-truth)" if ifc_surface["documented_source_of_truth"] else " (project-scoped shadow)"
    )


def _format_contract_suffix() -> str:
    return (
        " The bounded live OpenConstructionERP schedule surface is "
        f"{ERP_SCHEDULE_IMPORT_PATH_TEMPLATE} (CSV upload) plus "
        f"{ERP_TASK_PROGRESS_PATH_TEMPLATE} (task progress JSON), so local verifier data "
        "must provide per-phase schedule_id/task_id before phases-sync can pass."
    )


def _format_phase_sync_blocker(diagnostics: dict[str, Any]) -> str:
    return "phase sync blocked: " + " ".join(diagnostics["blockers"]) + _format_contract_suffix()


def _normalized_date(value: Any, *, fallback: str) -> str:
    if isinstance(value, dt.datetime):
        return value.date().isoformat()
    if isinstance(value, dt.date):
        return value.isoformat()
    if isinstance(value, str):
        normalized = value.strip()
        if not normalized:
            return fallback
        if "T" in normalized:
            normalized = normalized.split("T", 1)[0]
        return normalized
    return fallback


def _phase_name(row: dict[str, Any]) -> str:
    value = _row_value(row, "phase")
    if isinstance(value, str) and value.strip():
        return value.strip()
    return DEFAULT_VERIFY_PHASE_NAME


def _phase_wbs_code(phase_name: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9]+", "-", phase_name.strip()).strip("-").upper()
    return (normalized or "PHASE-A")[:50]


def _raw_event_dict(row: dict[str, Any]) -> dict[str, Any]:
    raw_event = row.get("raw_event")
    if isinstance(raw_event, dict):
        return dict(raw_event)
    return {}


def _safe_table(pxt: Any, path: str) -> Any | None:
    try:
        return pxt.get_table(path)
    except Exception:
        return None


def _ensure_dir(pxt: Any, path: str) -> None:
    create_dir = getattr(pxt, "create_dir", None)
    if callable(create_dir):
        try:
            create_dir(path)
        except Exception:
            pass


def _shadow_schema(pxt: Any) -> dict[str, Any]:
    return {name: getattr(pxt, type_name) for name, type_name in PROJECT_SHADOW_SCHEMA}


def _ensure_project_shadow_table(pxt: Any, project_id: str) -> Any:
    ns_root = "lattice/projects"
    ns_project = f"{ns_root}/{project_id}"
    table_path = PROJECT_IFC_TABLE_TEMPLATE.format(project_id=project_id)
    _ensure_dir(pxt, ns_root)
    _ensure_dir(pxt, ns_project)
    table = _safe_table(pxt, table_path)
    if table is None:
        create_table = getattr(pxt, "create_table", None)
        if not callable(create_table):
            raise NotImplementedError(
                f"phase sync blocked: {table_path} does not exist and Pixeltable cannot create the project shadow seam."
            )
        create_table(table_path, _shadow_schema(pxt))
        table = require_table(
            pxt,
            table_path,
            blocker=f"phase sync blocked: project shadow seam {table_path} was created but could not be reopened.",
        )
    add_column = getattr(table, "add_column", None)
    if callable(add_column):
        for name, type_name in PROJECT_SHADOW_SCHEMA:
            add_column(if_exists="ignore", **{name: getattr(pxt, type_name)})
    return table


def _seed_project_shadow_ifc_rows(pxt: Any, project_id: str) -> dict[str, Any]:
    bridge_table = require_table(
        pxt,
        BRIDGE_IFC_TABLE,
        blocker=f"phase sync blocked: bridge IFC source {BRIDGE_IFC_TABLE} is not available for proof seeding.",
    )
    bridge_rows = _collect_rows(
        bridge_table,
        table_path=BRIDGE_IFC_TABLE,
        blocker="phase sync blocked: bridge IFC source",
    )
    if not bridge_rows:
        raise NotImplementedError(
            f"phase sync blocked: bridge IFC source {BRIDGE_IFC_TABLE} has no rows to seed project_id={project_id}."
        )
    shadow_table = _ensure_project_shadow_table(pxt, project_id)
    existing_rows = _collect_rows(
        shadow_table,
        table_path=PROJECT_IFC_TABLE_TEMPLATE.format(project_id=project_id),
        blocker="phase sync blocked: project shadow seam",
    )
    if existing_rows:
        return {"table_path": PROJECT_IFC_TABLE_TEMPLATE.format(project_id=project_id), "rows_seeded": 0}
    insert = getattr(shadow_table, "insert", None)
    if not callable(insert):
        raise NotImplementedError(
            f"phase sync blocked: project shadow seam {PROJECT_IFC_TABLE_TEMPLATE.format(project_id=project_id)} "
            "does not expose insert() for proof seeding."
        )
    rows_to_insert: list[dict[str, Any]] = []
    for row in bridge_rows:
        rows_to_insert.append(
            {
                "id": str(row.get("id") or row.get("source_element_id") or f"{project_id}:{len(rows_to_insert) + 1}"),
                "project_id": project_id,
                "source_element_id": str(row.get("source_element_id") or "").strip(),
                "ifc_class": row.get("ifc_class") or "",
                "ifc_predefined_type": row.get("ifc_predefined_type") or "",
                "ifc_schema": row.get("ifc_schema") or "",
                "name": row.get("name") or "",
                "long_name": row.get("long_name") or "",
                "object_type": row.get("object_type") or "",
                "tag": row.get("tag") or "",
                "description": row.get("description") or "",
                "spatial_container_guid": row.get("spatial_container_guid") or "",
                "spatial_container_class": row.get("spatial_container_class") or "",
                "bbox_min": row.get("bbox_min"),
                "bbox_max": row.get("bbox_max"),
                "centroid": row.get("centroid"),
                "elevation_m": row.get("elevation_m"),
                "is_marpa_seed": bool(row.get("is_marpa_seed")),
                "raw_attributes": row.get("raw_attributes") or {},
                "parsed_at": _normalized_date(row.get("parsed_at"), fallback=DEFAULT_VERIFY_START_DATE),
                "boq_phase": str(row.get("boq_phase") or DEFAULT_VERIFY_PHASE_NAME),
                "quantity": float(row.get("quantity") or 1.0),
                "quantity_unit": str(row.get("quantity_unit") or "ea"),
                "erp_item_id": row.get("erp_item_id") or "",
                "unit_cost": row.get("unit_cost"),
                "unit_cost_region": row.get("unit_cost_region") or "",
                "cost_last_updated": row.get("cost_last_updated"),
                "raw_event": {
                    "seed_source": BRIDGE_IFC_TABLE,
                    "seeded_for_project_id": project_id,
                },
            }
        )
    insert(rows_to_insert)
    return {"table_path": PROJECT_IFC_TABLE_TEMPLATE.format(project_id=project_id), "rows_seeded": len(rows_to_insert)}


def _project_rows(projects_table: Any, project_id: str) -> list[dict[str, Any]]:
    rows = _collect_rows(
        projects_table,
        table_path=BRIDGE_PROJECTS_TABLE,
        blocker="phase sync blocked: schedule source",
    )
    return [row for row in rows if row.get("project_id") == project_id]


def _phase_row_filter(table: Any, row: dict[str, Any], project_id: str) -> Any:
    where_expr = getattr(table, "project_id") == project_id
    row_id = row.get("id")
    table_id = getattr(table, "id", None)
    if row_id is not None and table_id is not None:
        return where_expr & (table_id == row_id)
    row_phase = row.get("phase")
    table_phase = getattr(table, "phase", None)
    if row_phase is not None and table_phase is not None:
        return where_expr & (table_phase == row_phase)
    return where_expr


def _update_phase_row(table: Any, row: dict[str, Any], project_id: str, *, values: dict[str, Any]) -> None:
    update = getattr(table, "update", None)
    if not callable(update):
        raise NotImplementedError(
            f"phase sync blocked: schedule source {BRIDGE_PROJECTS_TABLE} does not expose update() for schedule persistence."
        )
    update(values, where=_phase_row_filter(table, row, project_id))


def _ensure_verify_project_row(pxt: Any, project_id: str) -> dict[str, Any]:
    projects_table = require_table(
        pxt,
        BRIDGE_PROJECTS_TABLE,
        blocker=f"phase sync blocked: schedule source {BRIDGE_PROJECTS_TABLE} is not available.",
    )
    project_rows = _project_rows(projects_table, project_id)
    if project_rows:
        return {"rows_seeded": 0}
    insert = getattr(projects_table, "insert", None)
    if not callable(insert):
        raise NotImplementedError(
            f"phase sync blocked: schedule source {BRIDGE_PROJECTS_TABLE} does not expose insert() for proof seeding."
        )
    georef_table = _safe_table(pxt, PROJECT_GEOREF_TABLE)
    georef_row = None
    if georef_table is not None:
        georef_rows = _collect_rows(
            georef_table,
            table_path=PROJECT_GEOREF_TABLE,
            blocker="phase sync blocked: project georef surface",
        )
        georef_row = next((row for row in georef_rows if row.get("project_id") == project_id), None)
    insert(
        [
            {
                "id": f"{project_id}:phase:{_phase_wbs_code(DEFAULT_VERIFY_PHASE_NAME).lower()}",
                "project_id": project_id,
                "name": DEFAULT_VERIFY_PROJECT_NAME,
                "status": "active",
                "phase": DEFAULT_VERIFY_PHASE_NAME,
                "start_date": dt.datetime.fromisoformat(f"{DEFAULT_VERIFY_START_DATE}T00:00:00+00:00"),
                "end_date": dt.datetime.fromisoformat(f"{DEFAULT_VERIFY_END_DATE}T00:00:00+00:00"),
                "longitude": georef_row.get("longitude") if georef_row else None,
                "latitude": georef_row.get("latitude") if georef_row else None,
                "elevation_m": georef_row.get("elevation_m") if georef_row else None,
                "geom_point_wkt": georef_row.get("geom_point_wkt") if georef_row else None,
                "epsg_code": georef_row.get("epsg_code") if georef_row else None,
                "erp_project_id": None,
                "notes": "Verifier-backed bounded ERP phase sync proof row.",
                "raw_event": {
                    "seeded_for_project_id": project_id,
                    "proof_seed": True,
                },
            }
        ]
    )
    return {"rows_seeded": 1}


def _ensure_local_phase_seam(project_id: str, pxt: Any) -> dict[str, Any]:
    if project_id != DEFAULT_VERIFY_PROJECT_ID:
        return {"shadow_rows_seeded": 0, "project_rows_seeded": 0}
    if not callable(getattr(pxt, "create_table", None)):
        return {"shadow_rows_seeded": 0, "project_rows_seeded": 0}
    shadow = _seed_project_shadow_ifc_rows(pxt, project_id)
    project = _ensure_verify_project_row(pxt, project_id)
    return {
        "shadow_rows_seeded": shadow["rows_seeded"],
        "shadow_table_path": shadow["table_path"],
        "project_rows_seeded": project["rows_seeded"],
    }


def _erp_project_id(row: dict[str, Any], project_id: str) -> tuple[str, str]:
    value = _row_value(row, "erp_project_id")
    if isinstance(value, str) and value.strip():
        return value.strip(), "local:erp_project_id"
    if project_id != DEFAULT_VERIFY_PROJECT_ID:
        raise NotImplementedError(
            f"phase sync blocked: schedule source {BRIDGE_PROJECTS_TABLE} has no erp_project_id for project_id={project_id}."
        )
    erp_project_id, source = ensure_erp_verifier_project_id(
        env_var_names=("ERP_PHASES_SYNC_VERIFY_PROJECT_ID",),
        project_name=DEFAULT_VERIFY_PROJECT_NAME,
        project_code=DEFAULT_VERIFY_PROJECT_CODE,
    )
    return erp_project_id, source


def _phase_rows_csv(project_rows: list[dict[str, Any]]) -> bytes:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=["wbs_code", "name", "start", "end"])
    writer.writeheader()
    for row in project_rows:
        phase = _phase_name(row)
        writer.writerow(
            {
                "wbs_code": _phase_wbs_code(phase),
                "name": phase,
                "start": _normalized_date(_row_value(row, "start_date"), fallback=DEFAULT_VERIFY_START_DATE),
                "end": _normalized_date(_row_value(row, "end_date"), fallback=DEFAULT_VERIFY_END_DATE),
            }
        )
    return buffer.getvalue().encode("utf-8")


def _metadata_value(row: dict[str, Any], key: str) -> Any:
    metadata = row.get("metadata_")
    if isinstance(metadata, dict):
        return metadata.get(key)
    metadata = row.get("metadata")
    if isinstance(metadata, dict):
        return metadata.get(key)
    return None


def _list_schedules(client: Any, erp_project_id: str) -> list[dict[str, Any]]:
    response = client.get(ERP_SCHEDULES_PATH, params={"project_id": erp_project_id})
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, list):
        raise RuntimeError("OpenConstructionERP schedule list response must be a JSON array.")
    return [row for row in payload if isinstance(row, dict)]


def _create_schedule(client: Any, *, erp_project_id: str, project_id: str, project_rows: list[dict[str, Any]]) -> dict[str, Any]:
    first_row = project_rows[0]
    response = client.post(
        ERP_SCHEDULES_PATH,
        json={
            "project_id": erp_project_id,
            "name": f"LATTICE Phase Sync {project_id}",
            "schedule_type": "master",
            "description": "Bounded LATTICE phase sync schedule",
            "start_date": _normalized_date(_row_value(first_row, "start_date"), fallback=DEFAULT_VERIFY_START_DATE),
            "end_date": _normalized_date(_row_value(first_row, "end_date"), fallback=DEFAULT_VERIFY_END_DATE),
            "data_date": _normalized_date(dt.date.today(), fallback=DEFAULT_VERIFY_START_DATE),
            "metadata": {"lattice_project_id": project_id},
        },
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError("OpenConstructionERP schedule create response must be a JSON object.")
    return payload


def _ensure_schedule(client: Any, *, erp_project_id: str, project_id: str, project_rows: list[dict[str, Any]]) -> tuple[str, str]:
    schedule_id = next(
        (
            str(_row_value(row, "schedule_id")).strip()
            for row in project_rows
            if isinstance(_row_value(row, "schedule_id"), str) and str(_row_value(row, "schedule_id")).strip()
        ),
        None,
    )
    if schedule_id is not None:
        return schedule_id, "local:schedule_id"
    schedules = _list_schedules(client, erp_project_id)
    existing = next(
        (
            row
            for row in schedules
            if _metadata_value(row, "lattice_project_id") == project_id or row.get("name") == f"LATTICE Phase Sync {project_id}"
        ),
        None,
    )
    if existing is not None:
        value = existing.get("id")
        if isinstance(value, str) and value.strip():
            return value.strip(), "erp:list-schedules"
    created = _create_schedule(client, erp_project_id=erp_project_id, project_id=project_id, project_rows=project_rows)
    value = created.get("id")
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError("OpenConstructionERP schedule create response did not include an id.")
    return value.strip(), "erp:create-schedule"


def _list_activities(client: Any, schedule_id: str) -> list[dict[str, Any]]:
    response = client.get(ERP_SCHEDULE_ACTIVITIES_PATH_TEMPLATE.format(schedule_id=schedule_id))
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, list):
        raise RuntimeError("OpenConstructionERP schedule activities response must be a JSON array.")
    return [row for row in payload if isinstance(row, dict)]


def _import_schedule(client: Any, schedule_id: str, project_rows: list[dict[str, Any]]) -> dict[str, Any]:
    response = client.post(
        ERP_SCHEDULE_IMPORT_PATH_TEMPLATE.format(schedule_id=schedule_id),
        files={"file": ("schedule.csv", _phase_rows_csv(project_rows), "text/csv")},
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError("OpenConstructionERP schedule import response must be a JSON object.")
    return payload


def _activity_for_phase(activities: list[dict[str, Any]], row: dict[str, Any]) -> dict[str, Any] | None:
    phase = _phase_name(row)
    wbs_code = _phase_wbs_code(phase)
    for activity in activities:
        if activity.get("wbs_code") == wbs_code or activity.get("name") == phase:
            return activity
    return None


def _record_progress(client: Any, task_id: str, row: dict[str, Any]) -> dict[str, Any]:
    response = client.post(
        ERP_TASK_PROGRESS_PATH_TEMPLATE.format(task_id=task_id),
        json={
            "progress_percent": 0.0,
            "notes": f"LATTICE bounded phase sync for {_phase_name(row)}",
            "device": "desktop",
            "actual_start_date": _normalized_date(_row_value(row, "start_date"), fallback=DEFAULT_VERIFY_START_DATE),
        },
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError("OpenConstructionERP task progress response must be a JSON object.")
    return payload


def _persist_phase_schedule_state(
    projects_table: Any,
    *,
    project_id: str,
    row: dict[str, Any],
    erp_project_id: str,
    schedule_id: str,
    task_id: str,
) -> None:
    raw_event = _raw_event_dict(row)
    raw_event.update(
        {
            "schedule_id": schedule_id,
            "task_id": task_id,
            "phase_sync_source": "erp-bound-write",
        }
    )
    _update_phase_row(
        projects_table,
        row,
        project_id,
        values={
            "erp_project_id": erp_project_id,
            "raw_event": raw_event,
        },
    )


def inspect_phase_sync_seam(project_id: str, pxt: Any | None = None) -> dict[str, Any]:
    """Inspect the smallest local seam that can satisfy the ERP phase contract."""
    normalized_project_id = _normalize_project_id(project_id)
    pxt_handle = require_pxt_handle(
        pxt,
        blocker=(
            "phase sync blocked: Pixeltable handle is not ready; expected get_table() for "
            "project IFC rows and schedule metadata access."
        ),
    )
    ifc_surface = resolve_project_ifc_surface(normalized_project_id, pxt_handle, capability="phase sync")
    projects_table = require_table(
        pxt_handle,
        BRIDGE_PROJECTS_TABLE,
        blocker=(f"phase sync blocked: schedule source {BRIDGE_PROJECTS_TABLE} is not available."),
    )
    diagnostics: dict[str, Any] = {
        "project_id": normalized_project_id,
        "ifc_surface_path": ifc_surface["path"],
        "ifc_surface_scope": ifc_surface["scope"],
        "ifc_surface_documented_source_of_truth": ifc_surface["documented_source_of_truth"],
        "ifc_project_filter": ifc_surface.get("project_filter"),
        "schedule_surface_path": BRIDGE_PROJECTS_TABLE,
        "bounded_write_path_implemented": True,
        "next_ready_blocker": None,
    }
    blockers: list[str] = []

    ifc_rows = _collect_rows(ifc_surface["table"], table_path=ifc_surface["path"], blocker="phase sync blocked: project IFC access resolves via")
    ifc_columns = sorted(_row_keys(ifc_rows))
    diagnostics["ifc_row_count"] = len(ifc_rows)
    diagnostics["ifc_columns"] = ifc_columns

    project_filter = ifc_surface.get("project_filter")
    if project_filter:
        if project_filter not in ifc_columns:
            blockers.append(
                f"project IFC access resolves via {_surface_label(ifc_surface)}, but rows do not expose "
                f"{project_filter}, so local IFC rows cannot be scoped to project_id={normalized_project_id}."
            )
        else:
            matching_ifc_rows = [row for row in ifc_rows if _row_value(row, project_filter) == normalized_project_id]
            diagnostics["ifc_project_row_count"] = len(matching_ifc_rows)
            if not matching_ifc_rows:
                blockers.append(
                    f"project IFC access resolves via {_surface_label(ifc_surface)}, but no IFC rows matched "
                    f"project_id={normalized_project_id}."
                )

    schedule_rows = _collect_rows(
        projects_table,
        table_path=BRIDGE_PROJECTS_TABLE,
        blocker="phase sync blocked: schedule source",
    )
    schedule_columns = sorted(_row_keys(schedule_rows))
    diagnostics["schedule_row_count"] = len(schedule_rows)
    diagnostics["schedule_columns"] = schedule_columns
    project_rows = [row for row in schedule_rows if row.get("project_id") == normalized_project_id]
    diagnostics["schedule_project_row_count"] = len(project_rows)

    if not project_rows:
        blockers.append(f"schedule source {BRIDGE_PROJECTS_TABLE} has no rows for project_id={normalized_project_id}.")
    else:
        project_level_fields = [
            field for field in PROJECT_LEVEL_SCHEDULE_FIELDS if any(_has_non_empty_value(row, field) for row in project_rows)
        ]
        available_phase_identifiers = [
            field for field in PHASE_IDENTIFIER_FIELDS if any(_has_non_empty_value(row, field) for row in project_rows)
        ]
        missing_phase_identifiers = [field for field in PHASE_IDENTIFIER_FIELDS if field not in available_phase_identifiers]
        diagnostics["project_level_schedule_fields"] = project_level_fields
        diagnostics["available_phase_identifiers"] = available_phase_identifiers
        diagnostics["missing_phase_identifiers"] = missing_phase_identifiers
        if missing_phase_identifiers:
            metadata_fields = "/".join(project_level_fields) if project_level_fields else "project-level schedule fields"
            blockers.append(
                f"schedule source {BRIDGE_PROJECTS_TABLE} has {len(project_rows)} row(s) for "
                f"project_id={normalized_project_id}, but only exposes {metadata_fields} and does not provide "
                f"{'/'.join(missing_phase_identifiers)}."
            )

    diagnostics["blockers"] = blockers
    diagnostics["ready"] = not blockers
    return diagnostics


def sync_phases(project_id: str, pxt: Any | None = None) -> dict:
    """Sync phase rows through the bounded ERP schedule import + progress path."""
    normalized_project_id = _normalize_project_id(project_id)
    pxt_handle = require_pxt_handle(
        pxt,
        blocker=(
            "phase sync blocked: Pixeltable handle is not ready; expected get_table() for "
            "project IFC rows and schedule metadata access."
        ),
    )
    seam_seed = _ensure_local_phase_seam(normalized_project_id, pxt_handle)
    diagnostics = inspect_phase_sync_seam(normalized_project_id, pxt=pxt_handle)
    if diagnostics["blockers"]:
        remaining = [
            blocker
            for blocker in diagnostics["blockers"]
            if "does not provide schedule_id/task_id" not in blocker
        ]
        if remaining:
            raise NotImplementedError(_format_phase_sync_blocker(diagnostics))

    projects_table = require_table(
        pxt_handle,
        BRIDGE_PROJECTS_TABLE,
        blocker=(f"phase sync blocked: schedule source {BRIDGE_PROJECTS_TABLE} is not available."),
    )
    project_rows = _project_rows(projects_table, normalized_project_id)
    if not project_rows:
        raise NotImplementedError(
            f"phase sync blocked: schedule source {BRIDGE_PROJECTS_TABLE} has no rows for project_id={normalized_project_id}."
        )

    erp_project_id, erp_project_source = _erp_project_id(project_rows[0], normalized_project_id)
    runtime = require_erp_runtime()
    with erp_client(base_url=runtime.base_url, timeout=30.0) as client:
        schedule_id, schedule_source = _ensure_schedule(
            client,
            erp_project_id=erp_project_id,
            project_id=normalized_project_id,
            project_rows=project_rows,
        )
        activities = _list_activities(client, schedule_id)
        imported = None
        if any(not _has_non_empty_value(row, "task_id") for row in project_rows):
            imported = _import_schedule(client, schedule_id, project_rows)
            activities = _list_activities(client, schedule_id)
        progress_entries: list[dict[str, Any]] = []
        phase_bindings: list[dict[str, Any]] = []
        for row in project_rows:
            activity = _activity_for_phase(activities, row)
            if activity is None:
                raise RuntimeError(
                    f"OpenConstructionERP schedule {schedule_id} did not expose an activity for phase {_phase_name(row)!r}."
                )
            task_id = activity.get("id")
            if not isinstance(task_id, str) or not task_id.strip():
                raise RuntimeError(
                    f"OpenConstructionERP activity for phase {_phase_name(row)!r} did not include an id."
                )
            _persist_phase_schedule_state(
                projects_table,
                project_id=normalized_project_id,
                row=row,
                erp_project_id=erp_project_id,
                schedule_id=schedule_id,
                task_id=task_id.strip(),
            )
            progress_entries.append(_record_progress(client, task_id.strip(), row))
            phase_bindings.append(
                {
                    "phase": _phase_name(row),
                    "schedule_id": schedule_id,
                    "task_id": task_id.strip(),
                    "wbs_code": _phase_wbs_code(_phase_name(row)),
                }
            )

    diagnostics = inspect_phase_sync_seam(normalized_project_id, pxt=pxt_handle)
    if diagnostics["blockers"]:
        raise NotImplementedError(_format_phase_sync_blocker(diagnostics))
    return {
        "project_id": normalized_project_id,
        "erp_base": runtime.base_url,
        "erp_project_id": erp_project_id,
        "erp_project_source": erp_project_source,
        "schedule_id": schedule_id,
        "schedule_source": schedule_source,
        "imported": imported,
        "phase_bindings": phase_bindings,
        "progress_entries_recorded": len(progress_entries),
        "seam_seed": seam_seed,
        "ifc_surface": diagnostics["ifc_surface_path"],
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: phase-adapter.py <project_id>", file=sys.stderr)
        raise SystemExit(1)
    print(sync_phases(sys.argv[1]))
