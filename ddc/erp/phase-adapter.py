#!/usr/bin/env python3
"""Bridge: project IFC rows + local schedule metadata → OpenConstructionERP phases.

The full 4D/5D sync is not promotable yet. This adapter only validates the
minimum local prerequisites and fails closed with a concrete blocker until the
repo has a real per-phase schedule surface to join against project IFC rows.
"""

from __future__ import annotations

from typing import Any
import sys

PROJECT_IFC_TABLE_TEMPLATE = "lattice/projects/{project_id}/ifc_elements"
BRIDGE_PROJECTS_TABLE = "lattice/bridge/marpa_projects"
ERP_SCHEDULE_IMPORT_PATH_TEMPLATE = "/api/v2/schedules/{schedule_id}/import"
ERP_TASK_PROGRESS_PATH_TEMPLATE = "/api/v2/schedules/tasks/{task_id}/progress"


def _normalize_project_id(project_id: str) -> str:
    normalized_project_id = project_id.strip()
    if not normalized_project_id:
        raise ValueError("project_id required")
    return normalized_project_id


def _require_pxt_handle(pxt: Any) -> Any:
    if pxt is None or not callable(getattr(pxt, "get_table", None)):
        raise NotImplementedError(
            "phase sync blocked: Pixeltable handle is not ready; expected get_table() for "
            "project IFC rows and schedule metadata access."
        )
    return pxt


def _require_table(pxt: Any, path: str, *, blocker: str) -> Any:
    try:
        return pxt.get_table(path)
    except Exception as exc:
        raise NotImplementedError(blocker) from exc


def sync_phases(project_id: str, pxt: Any | None = None) -> dict:
    """Validate local phase-sync prerequisites and fail closed with a real blocker."""
    normalized_project_id = _normalize_project_id(project_id)
    pxt_handle = _require_pxt_handle(pxt)
    project_ifc_table = PROJECT_IFC_TABLE_TEMPLATE.format(project_id=normalized_project_id)
    _require_table(
        pxt_handle,
        project_ifc_table,
        blocker=(
            "phase sync blocked: project IFC rows are not ready at "
            f"{project_ifc_table}; the route cannot derive phase assignments without a "
            "project-scoped element set."
        ),
    )
    _require_table(
        pxt_handle,
        BRIDGE_PROJECTS_TABLE,
        blocker=(
            "phase sync blocked: schedule source "
            f"{BRIDGE_PROJECTS_TABLE} is not available."
        ),
    )
    raise NotImplementedError(
        "phase sync blocked: local schedule metadata is only project-level in "
        "lattice/bridge/marpa_projects (phase/start_date/end_date) and cannot express "
        f"per-phase assignments for {normalized_project_id}. The bounded live "
        "OpenConstructionERP schedule surface is "
        f"{ERP_SCHEDULE_IMPORT_PATH_TEMPLATE} (CSV upload) plus "
        f"{ERP_TASK_PROGRESS_PATH_TEMPLATE} (task progress JSON), so verifier data "
        "must include schedule_id/task_id rather than only project_id."
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: phase-adapter.py <project_id>", file=sys.stderr)
        raise SystemExit(1)
    print(sync_phases(sys.argv[1]))
