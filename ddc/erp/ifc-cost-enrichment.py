"""Project-scoped IFC cost enrichment writeback for reliable CWICR matches."""

from __future__ import annotations

import datetime as dt
from typing import Any

from ddc.erp.project_seams import require_pxt_handle, resolve_project_ifc_surface


def _normalize_project_id(project_id: str) -> str:
    normalized_project_id = project_id.strip()
    if not normalized_project_id:
        raise ValueError("project_id required")
    return normalized_project_id


def _normalize_source_element_ids(source_element_ids: Any) -> list[str]:
    if not isinstance(source_element_ids, list | tuple):
        raise ValueError("source_element_ids required")
    normalized_ids: list[str] = []
    seen: set[str] = set()
    for value in source_element_ids:
        if not isinstance(value, str):
            raise ValueError("source_element_ids must contain only strings")
        normalized = value.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        normalized_ids.append(normalized)
    if not normalized_ids:
        raise ValueError("source_element_ids required")
    return normalized_ids


def _as_row_dict(row: Any) -> dict[str, Any]:
    if isinstance(row, dict):
        return row
    try:
        return dict(row)
    except Exception as exc:
        raise RuntimeError(
            f"ifc cost enrichment expected IFC rows as mappings; got {type(row).__name__}"
        ) from exc


def _collect_target_rows(
    project_id: str,
    *,
    ifc_surface: dict[str, Any],
    source_element_ids: list[str],
) -> list[dict[str, Any]]:
    table = ifc_surface["table"]
    collect = getattr(table, "collect", None)
    if not callable(collect):
        raise NotImplementedError(
            "ifc cost enrichment blocked: project IFC rows are not queryable at "
            f"{ifc_surface['path']}; expected collect() before cost writeback."
        )
    project_filter = ifc_surface.get("project_filter")
    rows = [_as_row_dict(row) for row in collect()]
    matching_rows = [
        row
        for row in rows
        if row.get("source_element_id") in source_element_ids
        and (project_filter is None or row.get(project_filter) == project_id)
    ]
    if matching_rows:
        return matching_rows
    source_list = ", ".join(source_element_ids)
    raise NotImplementedError(
        "ifc cost enrichment blocked: project IFC access resolves via "
        f"{ifc_surface['path']}"
        + (
            " (bridge source-of-truth)"
            if ifc_surface["documented_source_of_truth"]
            else " (project-scoped shadow)"
        )
        + f", but no IFC rows matched project_id={project_id} for source_element_id(s)={source_list}."
    )


def _normalize_unit_cost(value: Any) -> float:
    if value is None:
        raise RuntimeError("ifc cost enrichment requires unit_cost on the selected CWICR match.")
    if isinstance(value, bool):
        raise RuntimeError("ifc cost enrichment received boolean unit_cost from CWICR.")
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        normalized = value.strip()
        if not normalized:
            raise RuntimeError("ifc cost enrichment requires unit_cost on the selected CWICR match.")
        try:
            return float(normalized)
        except ValueError as exc:
            raise RuntimeError(f"ifc cost enrichment received non-numeric unit_cost {value!r}.") from exc
    raise RuntimeError(f"ifc cost enrichment received unsupported unit_cost type {type(value).__name__}.")


def _normalize_unit_cost_region(value: Any) -> str:
    if not isinstance(value, str):
        raise RuntimeError("ifc cost enrichment requires unit_cost_region on the selected CWICR match.")
    normalized = value.strip()
    if not normalized:
        raise RuntimeError("ifc cost enrichment requires unit_cost_region on the selected CWICR match.")
    return normalized


def _update_where_expr(table: Any, *, project_filter: str | None, project_id: str, source_element_id: str) -> Any:
    source_column = getattr(table, "source_element_id", None)
    if source_column is None:
        raise NotImplementedError(
            "ifc cost enrichment blocked: resolved IFC table does not expose source_element_id for writeback."
        )
    where_expr = source_column == source_element_id
    if project_filter:
        project_column = getattr(table, project_filter, None)
        if project_column is None:
            raise NotImplementedError(
                "ifc cost enrichment blocked: resolved IFC table does not expose "
                f"{project_filter!r} for project-scoped writeback."
            )
        where_expr = where_expr & (project_column == project_id)
    return where_expr


def write_cost_match(
    project_id: str,
    source_element_ids: Any,
    match: dict[str, Any],
    *,
    pxt: Any | None = None,
) -> dict[str, Any]:
    """Write one reliable CWICR match back into project-scoped IFC rows."""
    normalized_project_id = _normalize_project_id(project_id)
    normalized_source_element_ids = _normalize_source_element_ids(source_element_ids)
    pxt_handle = require_pxt_handle(
        pxt,
        blocker=(
            "ifc cost enrichment blocked: Pixeltable handle is not ready; expected get_table() "
            "for Juniper-scoped IFC writeback."
        ),
    )
    ifc_surface = resolve_project_ifc_surface(normalized_project_id, pxt_handle, capability="ifc cost enrichment")
    target_rows = _collect_target_rows(
        normalized_project_id,
        ifc_surface=ifc_surface,
        source_element_ids=normalized_source_element_ids,
    )
    table = ifc_surface["table"]
    update = getattr(table, "update", None)
    if not callable(update):
        raise NotImplementedError(
            "ifc cost enrichment blocked: project IFC access resolves via "
            f"{ifc_surface['path']}, but the table does not expose update() for unit-cost writeback."
        )
    unit_cost = _normalize_unit_cost(match.get("unit_cost"))
    unit_cost_region = _normalize_unit_cost_region(match.get("unit_cost_region"))
    cost_last_updated = dt.datetime.now(dt.UTC)
    updated_ids: list[str] = []
    for row in target_rows:
        source_element_id = str(row.get("source_element_id") or "").strip()
        if not source_element_id:
            raise RuntimeError("ifc cost enrichment requires source_element_id on every targeted IFC row.")
        update(
            {
                "unit_cost": unit_cost,
                "unit_cost_region": unit_cost_region,
                "cost_last_updated": cost_last_updated,
            },
            where=_update_where_expr(
                table,
                project_filter=ifc_surface.get("project_filter"),
                project_id=normalized_project_id,
                source_element_id=source_element_id,
            ),
        )
        updated_ids.append(source_element_id)
    return {
        "project_id": normalized_project_id,
        "ifc_surface": ifc_surface["path"],
        "rows_updated": len(updated_ids),
        "source_element_ids": updated_ids,
        "unit_cost": unit_cost,
        "unit_cost_region": unit_cost_region,
        "cost_last_updated": cost_last_updated.isoformat().replace("+00:00", "Z"),
    }
