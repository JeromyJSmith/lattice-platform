#!/usr/bin/env python3
"""Bridge: `lattice/bridge/ifc/ifc_elements` rows → OpenConstructionERP BOQ line items.

For each element row, POST to OpenConstructionERP's BOQ create endpoint, then
write the returned `erp_item_id` + `unit_cost` back into Pixeltable.

Tracked in meta/FEATURE_BACKLOG.md § DDC INTEGRATION → "OpenConstructionERP BOQ".

Stub — acceptance criteria are on the matching GitHub issue.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import httpx

REPO_ROOT = Path(__file__).resolve().parents[2]
if REPO_ROOT.as_posix() not in sys.path:
    sys.path.insert(0, REPO_ROOT.as_posix())

from ddc.erp.runtime import erp_client, require_erp_runtime, resolve_erp_runtime


ERP_BOQ_LIST_PATH = "/api/v1/boq/boqs/"
PROJECT_IFC_TABLE_TEMPLATE = "lattice/projects/{project_id}/ifc_elements"
BRIDGE_IFC_TABLE = "lattice/bridge/ifc/ifc_elements"
ERP_RUNTIME = resolve_erp_runtime()
ERP_BASE = ERP_RUNTIME.base_url


def _normalize_project_id(project_id: str) -> str:
    normalized_project_id = project_id.strip()
    if not normalized_project_id:
        raise ValueError("project_id required")
    return normalized_project_id


def _require_pxt_handle(pxt: Any) -> Any:
    if pxt is None or not callable(getattr(pxt, "get_table", None)):
        raise NotImplementedError(
            "boq sync blocked: Pixeltable handle is not ready; expected get_table() for "
            "project IFC row access and BOQ writeback."
        )
    return pxt


def _require_table(pxt: Any, path: str, *, blocker: str) -> Any:
    try:
        return pxt.get_table(path)
    except Exception as exc:
        raise NotImplementedError(blocker) from exc


def sync_boq(project_id: str, pxt: Any | None = None) -> dict:
    """Validate the current BOQ sync prerequisites and fail closed with a concrete blocker."""
    normalized_project_id = _normalize_project_id(project_id)
    pxt_handle = _require_pxt_handle(pxt)
    project_ifc_table = PROJECT_IFC_TABLE_TEMPLATE.format(project_id=normalized_project_id)
    _require_table(
        pxt_handle,
        project_ifc_table,
        blocker=(
            "boq sync blocked: project IFC rows are not ready at "
            f"{project_ifc_table}; the route cannot map project_id to a local BOQ input set yet."
        ),
    )
    _require_table(
        pxt_handle,
        BRIDGE_IFC_TABLE,
        blocker=(
            "boq sync blocked: BOQ writeback target "
            f"{BRIDGE_IFC_TABLE} is not available."
        ),
    )
    raise NotImplementedError(
        "boq sync blocked: the project-to-bridge writeback contract for "
        "erp_item_id/unit_cost persistence is not implemented yet."
    )

    # Sketch (uncomment when implementing):
    # import httpx
    # import pixeltable as pxt
    # t = pxt.get_table("lattice/bridge/ifc/ifc_elements")
    # rows = t.where(t.project_id == project_id).collect()
    # client = httpx.Client(base_url=ERP_BASE, timeout=30.0)
    # for r in rows:
    #     payload = {
    #         "project_id": project_id,
    #         "element_id": r["source_element_id"],
    #         "name":       r.get("user_label") or r["bis_subclass"],
    #         "bis_class":  r["bis_class"],
    #         "quantity":   r.get("quantity") or 1.0,
    #         "unit":       r.get("quantity_unit") or "ea",
    #     }
    #     res = client.post("/api/boq/create", json=payload).raise_for_status().json()
    #     # Upsert erp_item_id + unit_cost on the row via upsert_runtime_event-style pattern
    # client.close()
    # return {"updated": len(rows), "project_id": project_id}


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
