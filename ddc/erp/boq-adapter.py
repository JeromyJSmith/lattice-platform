#!/usr/bin/env python3
"""Bridge: `lattice/bridge/ifc/ifc_elements` rows → OpenConstructionERP BOQ line items.

For each element row, POST to OpenConstructionERP's BOQ create endpoint, then
write the returned `erp_item_id` + `unit_cost` back into Pixeltable.

Tracked in meta/FEATURE_BACKLOG.md § DDC INTEGRATION → "OpenConstructionERP BOQ".

Current implementation is intentionally narrow: create one BOQ for the sync run,
add BOQ positions for bridge rows that still lack `erp_item_id`, and write the
returned position id / unit rate back into the bridge row.
"""

from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path
from typing import Any

import httpx

REPO_ROOT = Path(__file__).resolve().parents[2]
if REPO_ROOT.as_posix() not in sys.path:
    sys.path.insert(0, REPO_ROOT.as_posix())

from ddc.erp.project_seams import BRIDGE_IFC_TABLE, require_pxt_handle, require_table, resolve_project_ifc_surface
from ddc.erp.runtime import erp_client, require_erp_runtime, resolve_erp_runtime


ERP_BOQ_LIST_PATH = "/api/v1/boq/boqs/"
ERP_BOQ_CREATE_PATH = "/api/v1/boq/boqs/"
ERP_BOQ_POSITIONS_PATH_TEMPLATE = "/api/v1/boq/boqs/{boq_id}/positions/"
ERP_RUNTIME = resolve_erp_runtime()
ERP_BASE = ERP_RUNTIME.base_url


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
        raise RuntimeError(f"OpenConstructionERP BOQ sync expected IFC rows as mappings; got {type(row).__name__}") from exc


def _collect_project_ifc_rows(project_id: str, ifc_surface: dict[str, Any]) -> list[dict[str, Any]]:
    table = ifc_surface["table"]
    collect = getattr(table, "collect", None)
    if not callable(collect):
        raise NotImplementedError(
            "boq sync blocked: project IFC rows are not queryable at "
            f"{ifc_surface['path']}; expected collect() before BOQ writeback."
        )

    project_filter = ifc_surface.get("project_filter")
    where = getattr(table, "where", None)
    if project_filter and callable(where):
        project_column = getattr(table, project_filter, None)
        if project_column is not None:
            try:
                return [_as_row_dict(row) for row in table.where(project_column == project_id).collect()]
            except Exception:
                pass

    rows = [_as_row_dict(row) for row in collect()]
    if project_filter:
        rows = [row for row in rows if row.get(project_filter) == project_id]
    return rows


def _normalize_quantity(value: Any) -> float:
    if value is None:
        return 1.0
    if isinstance(value, bool):
        raise RuntimeError("OpenConstructionERP BOQ sync requires numeric quantity values.")
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        normalized = value.strip()
        if not normalized:
            return 1.0
        try:
            return float(normalized)
        except ValueError as exc:
            raise RuntimeError(f"OpenConstructionERP BOQ sync received non-numeric quantity {value!r}.") from exc
    raise RuntimeError(f"OpenConstructionERP BOQ sync received unsupported quantity type {type(value).__name__}.")


def _normalize_unit(value: Any) -> str:
    if not isinstance(value, str):
        return "ea"
    normalized = value.strip()
    return normalized or "ea"


def _position_description(row: dict[str, Any]) -> str:
    for key in ("user_label", "name", "description", "bis_subclass", "bis_class", "ifc_class", "source_element_id"):
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "LATTICE IFC element"


def _position_ordinal(row: dict[str, Any]) -> str:
    for key in ("tag", "source_element_id", "ifc_global_id", "bis_federation_guid"):
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()[:50]
    return "LATTICE-ITEM"


def _position_unit_rate(row: dict[str, Any]) -> float:
    value = row.get("unit_cost")
    if value is None:
        value = row.get("unit_rate")
    if value is None:
        return 0.0
    if isinstance(value, bool):
        raise RuntimeError("OpenConstructionERP BOQ sync received boolean unit_cost.")
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        normalized = value.strip()
        if not normalized:
            return 0.0
        try:
            return float(normalized)
        except ValueError as exc:
            raise RuntimeError(f"OpenConstructionERP BOQ sync received non-numeric unit_cost {value!r}.") from exc
    raise RuntimeError(f"OpenConstructionERP BOQ sync received unsupported unit_cost type {type(value).__name__}.")


def _build_position_payload(project_id: str, boq_id: str, row: dict[str, Any]) -> dict[str, Any]:
    source_element_id = str(row.get("source_element_id", "")).strip()
    if not source_element_id:
        raise RuntimeError("OpenConstructionERP BOQ sync requires source_element_id on every IFC row.")
    return {
        "boq_id": boq_id,
        "ordinal": _position_ordinal(row),
        "description": _position_description(row),
        "unit": _normalize_unit(row.get("quantity_unit")),
        "quantity": _normalize_quantity(row.get("quantity")),
        "unit_rate": _position_unit_rate(row),
        "source": "cad_import",
        "cad_element_ids": [source_element_id],
        "classification": {
            "ifc_class": row.get("ifc_class"),
            "bis_class": row.get("bis_class"),
            "bis_subclass": row.get("bis_subclass"),
        },
        "metadata": {
            "lattice_project_id": project_id,
            "lattice_source_element_id": source_element_id,
        },
    }


def _create_boq(client: httpx.Client, project_id: str) -> dict[str, Any]:
    response = client.post(
        ERP_BOQ_CREATE_PATH,
        json={
            "project_id": project_id,
            "name": f"LATTICE Sync {project_id}",
            "description": "LATTICE BOQ sync from IFC bridge rows",
        },
        follow_redirects=True,
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError("OpenConstructionERP BOQ create response must be a JSON object")
    return payload


def _create_position(client: httpx.Client, boq_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    response = client.post(
        ERP_BOQ_POSITIONS_PATH_TEMPLATE.format(boq_id=boq_id),
        json=payload,
        follow_redirects=True,
    )
    response.raise_for_status()
    position = response.json()
    if not isinstance(position, dict):
        raise RuntimeError("OpenConstructionERP BOQ position response must be a JSON object")
    return position


def _writeback_row(
    table: Any,
    *,
    project_id: str,
    project_filter: str | None,
    source_element_id: str,
    erp_item_id: str,
    unit_cost: float,
    cost_last_updated: str | None,
    table_path: str,
) -> None:
    update = getattr(table, "update", None)
    if not callable(update):
        raise NotImplementedError(
            "boq sync blocked: project IFC access resolves via "
            f"{table_path}, but the table does not expose update() for erp_item_id/unit_cost writeback."
        )

    where_expr = getattr(table, "source_element_id") == source_element_id
    if project_filter:
        project_column = getattr(table, project_filter, None)
        if project_column is None:
            raise NotImplementedError(
                "boq sync blocked: project IFC access resolves via "
                f"{table_path}, but the project filter column {project_filter!r} is not writable."
            )
        where_expr = where_expr & (project_column == project_id)

    values: dict[str, Any] = {
        "erp_item_id": erp_item_id,
        "unit_cost": unit_cost,
    }
    if cost_last_updated:
        try:
            values["cost_last_updated"] = dt.datetime.fromisoformat(cost_last_updated.replace("Z", "+00:00"))
        except ValueError:
            values["cost_last_updated"] = cost_last_updated
    update(values, where=where_expr)


def sync_boq(project_id: str, pxt: Any | None = None) -> dict:
    """Create BOQ positions from project IFC rows and write back ERP identifiers."""
    normalized_project_id = _normalize_project_id(project_id)
    pxt_handle = require_pxt_handle(
        pxt,
        blocker=(
            "boq sync blocked: Pixeltable handle is not ready; expected get_table() for "
            "project IFC row access and BOQ writeback."
        ),
    )
    ifc_surface = resolve_project_ifc_surface(normalized_project_id, pxt_handle, capability="boq sync")
    require_table(
        pxt_handle,
        BRIDGE_IFC_TABLE,
        blocker=(
            "boq sync blocked: project IFC rows are not ready at "
            f"{BRIDGE_IFC_TABLE}; the route cannot persist BOQ writeback fields yet."
        ),
    )

    rows = _collect_project_ifc_rows(normalized_project_id, ifc_surface)
    pending_rows = [row for row in rows if not str(row.get("erp_item_id") or "").strip()]
    if not rows:
        raise NotImplementedError(
            "boq sync blocked: project IFC access resolves via "
            f"{ifc_surface['path']}"
            + (
                " (bridge source-of-truth)"
                if ifc_surface["documented_source_of_truth"]
                else " (project-scoped shadow)"
            )
            + f", but no IFC rows matched project_id={normalized_project_id} for BOQ position writeback."
        )
    if not pending_rows:
        return {
            "project_id": normalized_project_id,
            "erp_base": ERP_BASE,
            "ifc_surface": ifc_surface["path"],
            "boq_id": None,
            "rows_seen": len(rows),
            "rows_updated": 0,
            "rows_skipped": len(rows),
        }

    erp_runtime = require_erp_runtime()
    with erp_client(base_url=erp_runtime.base_url, timeout=30.0) as client:
        boq = _create_boq(client, normalized_project_id)
        boq_id = str(boq.get("id", "")).strip()
        if not boq_id:
            raise RuntimeError("OpenConstructionERP BOQ create response did not include an id.")
        updated = 0
        for row in pending_rows:
            position = _create_position(
                client,
                boq_id,
                _build_position_payload(normalized_project_id, boq_id, row),
            )
            position_id = str(position.get("id", "")).strip()
            if not position_id:
                raise RuntimeError("OpenConstructionERP BOQ position response did not include an id.")
            source_element_id = str(row.get("source_element_id", "")).strip()
            if not source_element_id:
                raise RuntimeError("OpenConstructionERP BOQ sync requires source_element_id on every IFC row.")
            _writeback_row(
                ifc_surface["table"],
                project_id=normalized_project_id,
                project_filter=ifc_surface.get("project_filter"),
                source_element_id=source_element_id,
                erp_item_id=position_id,
                unit_cost=_position_unit_rate(position),
                cost_last_updated=position.get("updated_at"),
                table_path=ifc_surface["path"],
            )
            updated += 1

    return {
        "project_id": normalized_project_id,
        "erp_base": erp_runtime.base_url,
        "ifc_surface": ifc_surface["path"],
        "boq_id": boq_id,
        "rows_seen": len(rows),
        "rows_updated": updated,
        "rows_skipped": len(rows) - len(pending_rows),
    }


def _normalize_boq_payload(payload: Any) -> dict[str, Any] | list[Any]:
    if isinstance(payload, dict | list):
        return payload
    raise RuntimeError("OpenConstructionERP BOQ response must be a JSON object or array")


def _fetch_project_boqs(client: httpx.Client, project_id: str) -> list[dict[str, Any]]:
    response = client.get(ERP_BOQ_LIST_PATH, params={"project_id": project_id})
    response.raise_for_status()
    try:
        payload = response.json()
    except ValueError as exc:
        raise RuntimeError("OpenConstructionERP BOQ list response was not valid JSON") from exc
    if not isinstance(payload, list) or not all(isinstance(row, dict) for row in payload):
        raise RuntimeError("OpenConstructionERP BOQ list response must be a JSON array of objects")
    return payload


def fetch_boq(project_id: str) -> dict:
    """Return one project's current BOQ document from OpenConstructionERP."""
    normalized_project_id = _normalize_project_id(project_id)
    erp_runtime = require_erp_runtime()
    with erp_client(base_url=erp_runtime.base_url, timeout=30.0) as client:
        payload = _fetch_project_boqs(client, normalized_project_id)
    return {
        "ok": True,
        "project_id": normalized_project_id,
        "erp_base": erp_runtime.base_url,
        "boq": _normalize_boq_payload(payload),
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: boq-adapter.py <project_id>", file=sys.stderr)
        raise SystemExit(1)
    print(sync_boq(sys.argv[1]))
