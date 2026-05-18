"""Shared ERP helpers for resolving project-scoped IFC access surfaces."""

from __future__ import annotations

from typing import Any

PROJECT_IFC_TABLE_TEMPLATE = "lattice/projects/{project_id}/ifc_elements"
BRIDGE_IFC_TABLE = "lattice/bridge/ifc/ifc_elements"


def require_pxt_handle(pxt: Any, *, blocker: str) -> Any:
    """Return the Pixeltable handle or raise the caller's concrete blocker."""
    if pxt is None or not callable(getattr(pxt, "get_table", None)):
        raise NotImplementedError(blocker)
    return pxt


def require_table(pxt: Any, path: str, *, blocker: str) -> Any:
    """Return one Pixeltable table handle or raise the caller's concrete blocker."""
    try:
        return pxt.get_table(path)
    except Exception as exc:
        raise NotImplementedError(blocker) from exc


def _as_row_dict(row: Any) -> dict[str, Any]:
    if isinstance(row, dict):
        return row
    try:
        return dict(row)
    except Exception:
        return {}


def _row_value(row: dict[str, Any], key: str) -> Any:
    value = row.get(key)
    if value is not None:
        return value
    raw_event = row.get("raw_event")
    if isinstance(raw_event, dict):
        return raw_event.get(key)
    return None


def _bridge_supports_project_scope(table: Any, project_id: str) -> bool:
    collect = getattr(table, "collect", None)
    if not callable(collect):
        return False
    try:
        rows = [_as_row_dict(row) for row in collect()]
    except Exception:
        return False
    if not rows:
        return False
    row_keys = {key for row in rows for key in row.keys()}
    if "project_id" in row_keys:
        return True
    return any(_row_value(row, "project_id") == project_id for row in rows)


def resolve_project_ifc_surface(project_id: str, pxt: Any, *, capability: str) -> dict[str, Any]:
    """Resolve the smallest project-addressable IFC surface, preferring the bridge catalog."""
    bridge_table = None
    try:
        bridge_table = pxt.get_table(BRIDGE_IFC_TABLE)
    except Exception:
        bridge_table = None
    if bridge_table is not None and _bridge_supports_project_scope(bridge_table, project_id):
        return {
            "table": bridge_table,
            "path": BRIDGE_IFC_TABLE,
            "scope": "bridge",
            "project_filter": "project_id",
            "documented_source_of_truth": True,
        }

    project_table_path = PROJECT_IFC_TABLE_TEMPLATE.format(project_id=project_id)
    project_table = None
    try:
        project_table = pxt.get_table(project_table_path)
    except Exception:
        project_table = None
    if project_table is not None:
        return {
            "table": project_table,
            "path": project_table_path,
            "scope": "project-shadow",
            "project_filter": None,
            "documented_source_of_truth": False,
        }

    if bridge_table is not None:
        return {
            "table": bridge_table,
            "path": BRIDGE_IFC_TABLE,
            "scope": "bridge",
            "project_filter": "project_id",
            "documented_source_of_truth": True,
        }

    raise NotImplementedError(
        f"{capability} blocked: project IFC rows are not ready for project_id={project_id}; "
        f"checked bridge source-of-truth {BRIDGE_IFC_TABLE} and project-scoped shadow {project_table_path}."
    )
