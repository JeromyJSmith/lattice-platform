#!/usr/bin/env python3
"""Bridge: project IFC rows + local schedule metadata → OpenConstructionERP phases.

The full 4D/5D sync is not promotable yet. This adapter only validates the
minimum local prerequisites and fails closed with a concrete blocker until the
repo has a real per-phase schedule surface to join against project IFC rows.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if REPO_ROOT.as_posix() not in sys.path:
    sys.path.insert(0, REPO_ROOT.as_posix())

from ddc.erp.project_seams import require_pxt_handle, require_table, resolve_project_ifc_surface

BRIDGE_PROJECTS_TABLE = "lattice/bridge/marpa_projects"
ERP_SCHEDULE_IMPORT_PATH_TEMPLATE = "/api/v2/schedules/{schedule_id}/import"
ERP_TASK_PROGRESS_PATH_TEMPLATE = "/api/v2/schedules/tasks/{task_id}/progress"
PROJECT_LEVEL_SCHEDULE_FIELDS = ("phase", "start_date", "end_date", "erp_project_id")
PHASE_IDENTIFIER_FIELDS = ("schedule_id", "task_id")


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
    }
    blockers: list[str] = []

    ifc_rows = _collect_rows(
        ifc_surface["table"],
        table_path=ifc_surface["path"],
        blocker="phase sync blocked: project IFC access resolves via",
    )
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
            matching_ifc_rows = [row for row in ifc_rows if row.get(project_filter) == normalized_project_id]
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
    """Validate local phase-sync prerequisites and fail closed with a real blocker."""
    diagnostics = inspect_phase_sync_seam(project_id, pxt=pxt)
    if diagnostics["blockers"]:
        raise NotImplementedError(_format_phase_sync_blocker(diagnostics))
    raise NotImplementedError(
        "phase sync blocked: local project and schedule seam is ready, but the bounded "
        "OpenConstructionERP schedule write path is not yet implemented in this adapter."
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: phase-adapter.py <project_id>", file=sys.stderr)
        raise SystemExit(1)
    print(sync_phases(sys.argv[1]))
