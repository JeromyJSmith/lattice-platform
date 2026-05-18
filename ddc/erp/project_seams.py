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


def resolve_project_ifc_surface(project_id: str, pxt: Any, *, capability: str) -> dict[str, Any]:
    """Resolve the smallest project-addressable IFC surface, preferring the bridge catalog."""
    bridge_table = None
    try:
        bridge_table = pxt.get_table(BRIDGE_IFC_TABLE)
    except Exception:
        bridge_table = None
    if bridge_table is not None:
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

    raise NotImplementedError(
        f"{capability} blocked: project IFC rows are not ready for project_id={project_id}; "
        f"checked bridge source-of-truth {BRIDGE_IFC_TABLE} and project-scoped shadow {project_table_path}."
    )
