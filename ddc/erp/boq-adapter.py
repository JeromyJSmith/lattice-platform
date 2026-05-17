#!/usr/bin/env python3
"""Bridge: `lattice/bridge/ifc/ifc_elements` rows → OpenConstructionERP BOQ line items.

For each element row, POST to OpenConstructionERP's BOQ create endpoint, then
write the returned `erp_item_id` + `unit_cost` back into Pixeltable.

Tracked in meta/FEATURE_BACKLOG.md § DDC INTEGRATION → "OpenConstructionERP BOQ".

Stub — acceptance criteria are on the matching GitHub issue.
"""

from __future__ import annotations

import os
import sys
from typing import Any

import httpx


ERP_BASE = os.environ.get("OPENCONSTRUCTIONERP_URL", "http://localhost:8080")


def sync_boq(project_id: str, pxt: Any | None = None) -> dict:
    """Walk ifc_elements for the project, upsert into ERP, write IDs back."""
    raise NotImplementedError(
        "boq-adapter stub. See ddc/erp/README.md for the endpoint contract and "
        "meta/DDC_MAPPING.md § Repo 2 for the OpenConstructionERP endpoints used."
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


def fetch_boq(project_id: str) -> dict:
    """Return one project's current BOQ document from OpenConstructionERP."""
    normalized_project_id = project_id.strip()
    with httpx.Client(base_url=ERP_BASE, timeout=30.0) as client:
        response = client.get(f"/api/boq/{normalized_project_id}")
        response.raise_for_status()
        try:
            payload = response.json()
        except ValueError as exc:
            raise RuntimeError("OpenConstructionERP BOQ response was not valid JSON") from exc
    return {
        "ok": True,
        "project_id": normalized_project_id,
        "erp_base": ERP_BASE,
        "boq": _normalize_boq_payload(payload),
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: boq-adapter.py <project_id>", file=sys.stderr)
        raise SystemExit(1)
    print(sync_boq(sys.argv[1]))
