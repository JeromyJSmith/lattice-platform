"""Governed Juniper quantity-takeoff proof runtime."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[2]
PIXELTABLE_ROOT = REPO_ROOT / "pixeltable"
if REPO_ROOT.as_posix() not in sys.path:
    sys.path.insert(0, REPO_ROOT.as_posix())
if PIXELTABLE_ROOT.as_posix() not in sys.path:
    sys.path.insert(0, PIXELTABLE_ROOT.as_posix())

from ddc.erp.project_seams import resolve_project_ifc_surface
from ddc.erp.runtime import ensure_erp_verifier_project_id
from service.idempotency import IdempotencyStore
from service.routes import erp

DEFAULT_PROJECT_ID = "918-juniper"
PROJECT_TARGET = "MARPA — 918 Juniper Avenue"
PROOF_LINEAGE = [
    "ROSE Residence workbook pilot proof (external to this repo)",
    "Farber-Haines 2521 IFC source lineage attached to the Juniper fixture in this repo",
]
SUPPORTED_BY = [
    "cwicr-seed",
    "cwicr-qdrant-cost-search",
    "ifc-cost-enrichment",
    "boq-sync",
    "boq-read",
    "boq-export",
]

JUNIPER_FIXTURE_ROWS: list[dict[str, Any]] = [
    {
        "project_id": DEFAULT_PROJECT_ID,
        "source_element_id": "ifc-juniper-001",
        "name": "Juniper planting bed",
        "quantity": 3.0,
        "quantity_unit": "ea",
        "erp_item_id": None,
        "unit_cost": None,
        "unit_cost_region": None,
        "cost_last_updated": None,
        "ifc_class": "IfcBuildingElementProxy",
        "bis_class": "Landscape.Planting",
        "bis_subclass": "ShrubBed",
    },
    {
        "project_id": DEFAULT_PROJECT_ID,
        "source_element_id": "ifc-juniper-002",
        "name": "Juniper decomposed granite path",
        "quantity": 12.5,
        "quantity_unit": "m2",
        "erp_item_id": None,
        "unit_cost": None,
        "unit_cost_region": None,
        "cost_last_updated": None,
        "ifc_class": "IfcSlab",
        "bis_class": "Site.Paving",
        "bis_subclass": "GranitePath",
    },
    {
        "project_id": "control-project",
        "source_element_id": "ifc-juniper-001",
        "name": "Control row",
        "quantity": 1.0,
        "quantity_unit": "ea",
        "erp_item_id": None,
        "unit_cost": None,
        "unit_cost_region": None,
        "cost_last_updated": None,
        "ifc_class": "IfcBuildingElementProxy",
        "bis_class": "Landscape.Planting",
        "bis_subclass": "Control",
    },
]

_COST_MATCHES = {
    "Juniper planting bed": {
        "item_id": "CWICR-JUNIPER-001",
        "unit_cost": 47.5,
        "unit": "ea",
    },
    "Juniper decomposed granite path": {
        "item_id": "CWICR-JUNIPER-002",
        "unit_cost": 18.25,
        "unit": "m2",
    },
}


class _Predicate:
    def __init__(self, fn):
        self._fn = fn

    def __call__(self, row: dict[str, Any]) -> bool:
        return self._fn(row)

    def __and__(self, other: "_Predicate") -> "_Predicate":
        return _Predicate(lambda row: self(row) and other(row))


class _Column:
    def __init__(self, name: str):
        self.name = name

    def __eq__(self, other: object) -> _Predicate:  # type: ignore[override]
        return _Predicate(lambda row: row.get(self.name) == other)


class _Query:
    def __init__(self, rows: list[dict[str, Any]]):
        self._rows = rows

    def collect(self) -> list[dict[str, Any]]:
        """Return the filtered in-memory rows."""
        return list(self._rows)


class VerifierIfcTable:
    """In-memory IFC bridge surface for governed Juniper proof runs."""

    project_id = _Column("project_id")
    source_element_id = _Column("source_element_id")

    def __init__(self, rows: list[dict[str, Any]] | None = None) -> None:
        self.rows = [dict(row) for row in (JUNIPER_FIXTURE_ROWS if rows is None else rows)]

    def where(self, predicate: _Predicate) -> _Query:
        """Filter IFC rows with the proof predicate contract."""
        return _Query([row for row in self.rows if predicate(row)])

    def collect(self) -> list[dict[str, Any]]:
        """Expose the full in-memory IFC row set."""
        return list(self.rows)

    def update(self, values: dict[str, Any], where: _Predicate | None = None) -> None:
        """Apply writeback updates to matching IFC proof rows."""
        for row in self.rows:
            if where is None or where(row):
                row.update(values)


class VerifierPxt:
    """Minimal Pixeltable handle exposing the governed IFC proof table."""

    def __init__(self, rows: list[dict[str, Any]] | None = None) -> None:
        self.table = VerifierIfcTable(rows)

    def get_table(self, path: str) -> Any:
        """Return the governed IFC proof table for the expected bridge path."""
        if path == "lattice/bridge/ifc/ifc_elements":
            return self.table
        raise RuntimeError(f"table not found: {path}")


def _build_app(root: Path, pxt: VerifierPxt) -> FastAPI:
    app = FastAPI()
    idem_path = root / ".tmp" / ".verify-ddc-quantity-takeoff.idem.json"
    idem_path.parent.mkdir(parents=True, exist_ok=True)
    app.state.idem = IdempotencyStore(idem_path)
    app.state.pxt = pxt
    app.include_router(erp.router, prefix="/v1/erp")
    return app


def _resolve_erp_project_id() -> tuple[str, str]:
    return ensure_erp_verifier_project_id(
        env_var_names=(
            "ERP_BOQ_SYNC_VERIFY_PROJECT_ID",
            "ERP_BOQ_PROJECT_ID",
            "ERP_BOQ_READ_VERIFY_PROJECT_ID",
            "ERP_BOQ_EXPORT_VERIFY_PROJECT_ID",
        )
    )


def _clone_for_erp_scope(rows: list[dict[str, Any]], *, erp_project_id: str) -> VerifierPxt:
    cloned_rows = []
    for row in rows:
        cloned = dict(row)
        if cloned.get("project_id") == DEFAULT_PROJECT_ID:
            cloned["project_id"] = erp_project_id
        cloned_rows.append(cloned)
    return VerifierPxt(cloned_rows)


def _cost_search_stub(description: str, region: str, top: int) -> list[dict[str, Any]]:
    match = _COST_MATCHES.get(description)
    if match is None:
        return []
    return [
        {
            "item_id": match["item_id"],
            "name": description,
            "unit": match["unit"],
            "unit_cost": match["unit_cost"],
            "unit_currency": "USD",
            "unit_cost_region": region,
            "score": 0.91,
            "retrieval_mode": "lexical",
        }
    ]


def extract_quantities(project_id: str, *, pxt: VerifierPxt) -> dict[str, Any]:
    """Collect governed Juniper quantities from the in-memory IFC proof surface."""
    ifc_surface = resolve_project_ifc_surface(project_id, pxt, capability="quantity takeoff agent")
    rows = [
        dict(row)
        for row in ifc_surface["table"].collect()
        if row.get(ifc_surface.get("project_filter") or "project_id") == project_id
    ]
    if not rows:
        raise RuntimeError(f"quantity takeoff agent found no IFC rows for project_id={project_id}")
    total_quantity = 0.0
    for row in rows:
        quantity = row.get("quantity")
        if not isinstance(quantity, int | float):
            raise RuntimeError("quantity takeoff agent requires numeric quantity values on the Juniper fixture rows.")
        total_quantity += float(quantity)
    return {
        "project_id": project_id,
        "ifc_surface": ifc_surface["path"],
        "row_count": len(rows),
        "total_quantity": total_quantity,
        "rows": [
            {
                "source_element_id": str(row["source_element_id"]),
                "name": str(row["name"]),
                "quantity": float(row["quantity"]),
                "quantity_unit": str(row.get("quantity_unit") or "ea"),
            }
            for row in rows
        ],
    }


def _expect_json_response(response, *, route: str) -> dict[str, Any]:
    payload = response.json()
    if response.status_code != 200:
        raise RuntimeError(f"{route} returned {response.status_code}: {payload}")
    if not isinstance(payload, dict):
        raise RuntimeError(f"{route} returned a non-object payload: {payload!r}")
    return payload


def _run_cost_writeback(client: TestClient, *, row: dict[str, Any]) -> dict[str, Any]:
    response = client.post(
        "/v1/erp/cost-search",
        json={
            "description": row["name"],
            "region": "US",
            "top": 3,
            "project_id": DEFAULT_PROJECT_ID,
            "source_element_id": row["source_element_id"],
            "writeback": True,
        },
    )
    body = _expect_json_response(response, route="/v1/erp/cost-search")
    if body.get("verification", {}).get("status") != "passed":
        raise RuntimeError(f"quantity takeoff cost-search step did not verify: {body}")
    writeback = body.get("writeback")
    if not isinstance(writeback, dict) or writeback.get("status") != "passed":
        raise RuntimeError(f"quantity takeoff cost-search writeback did not pass: {body}")
    return {
        "source_element_id": row["source_element_id"],
        "item_id": body["rows"][0]["item_id"],
        "unit_cost": body["rows"][0]["unit_cost"],
        "verification": body["verification"]["status"],
        "writeback": writeback,
    }


def _run_boq_sync(client: TestClient, *, project_id: str, idempotency_key: str) -> dict[str, Any]:
    response = client.post(
        "/v1/erp/boq",
        json={"project_id": project_id},
        headers={"Idempotency-Key": f"{idempotency_key}:{project_id}"},
    )
    body = _expect_json_response(response, route="/v1/erp/boq")
    if body.get("ok") is not True:
        raise RuntimeError(f"quantity takeoff BOQ sync did not report ok=true: {body}")
    return body


def _run_boq_read(client: TestClient, *, project_id: str) -> dict[str, Any]:
    response = client.get(f"/v1/erp/boq/{project_id}")
    body = _expect_json_response(response, route=f"/v1/erp/boq/{project_id}")
    if body.get("ok") is not True:
        raise RuntimeError(f"quantity takeoff BOQ read did not report ok=true: {body}")
    boq = body.get("boq")
    boq_count = len(boq) if isinstance(boq, list) else 1 if isinstance(boq, dict) else 0
    if boq_count < 1:
        raise RuntimeError(f"quantity takeoff BOQ read returned no BOQ payload for project_id={project_id}")
    return {
        "project_id": body["project_id"],
        "boq_count": boq_count,
        "erp_base": body.get("erp_base"),
    }


def _run_boq_export(client: TestClient, *, project_id: str) -> dict[str, Any]:
    response = client.get(f"/v1/erp/export/{project_id}?fmt=csv")
    if response.status_code != 200:
        raise RuntimeError(f"/v1/erp/export/{project_id}?fmt=csv returned {response.status_code}: {response.text}")
    content_type = response.headers.get("content-type", "")
    if not content_type.startswith("text/csv"):
        raise RuntimeError(
            f"/v1/erp/export/{project_id}?fmt=csv returned unexpected content-type {content_type!r}"
        )
    disposition = response.headers.get("content-disposition", "")
    if "filename=" not in disposition:
        raise RuntimeError(f"/v1/erp/export/{project_id}?fmt=csv did not expose a download filename.")
    if not response.content:
        raise RuntimeError(f"/v1/erp/export/{project_id}?fmt=csv returned an empty artifact.")
    return {
        "project_id": project_id,
        "content_type": content_type,
        "content_length": len(response.content),
        "filename": disposition.split("filename=", 1)[1].strip('"'),
    }


def run_quantity_takeoff_proof(root: Path, *, idempotency_key: str = "ddc-quantity-takeoff-proof-0001") -> dict[str, Any]:
    """Run the governed Juniper quantity path through writeback, BOQ sync, and evidence capture."""
    pxt = VerifierPxt()
    quantity_extract = extract_quantities(DEFAULT_PROJECT_ID, pxt=pxt)
    original_search = erp._COST_SEARCH.search
    erp._COST_SEARCH.search = _cost_search_stub
    try:
        with TestClient(_build_app(root, pxt)) as client:
            cost_search_writeback = [
                _run_cost_writeback(client, row=row)
                for row in quantity_extract["rows"]
            ]
    finally:
        erp._COST_SEARCH.search = original_search

    erp_project_id, erp_project_id_source = _resolve_erp_project_id()
    erp_scope_pxt = _clone_for_erp_scope(pxt.table.rows, erp_project_id=erp_project_id)
    run_idempotency_key = f"{idempotency_key}-{uuid4().hex[:8]}"
    with TestClient(_build_app(root, erp_scope_pxt)) as client:
        boq_sync = _run_boq_sync(client, project_id=erp_project_id, idempotency_key=run_idempotency_key)
        boq_read = _run_boq_read(client, project_id=erp_project_id)
        boq_export = _run_boq_export(client, project_id=erp_project_id)
    erp_linkage = {
        str(row.get("source_element_id")): str(row.get("erp_item_id") or "").strip()
        for row in erp_scope_pxt.table.rows
        if row.get("project_id") == erp_project_id
    }
    for row in pxt.table.rows:
        if row.get("project_id") != DEFAULT_PROJECT_ID:
            continue
        source_element_id = str(row.get("source_element_id") or "").strip()
        erp_item_id = erp_linkage.get(source_element_id)
        if erp_item_id:
            row["erp_item_id"] = erp_item_id

    enriched_rows = [
        dict(row)
        for row in pxt.table.rows
        if row.get("project_id") == DEFAULT_PROJECT_ID
    ]
    for row in enriched_rows:
        if row.get("unit_cost") is None or row.get("unit_cost_region") != "US":
            raise RuntimeError(f"quantity takeoff proof expected enriched Juniper IFC rows: {row}")
        if not str(row.get("erp_item_id") or "").strip():
            raise RuntimeError(f"quantity takeoff proof expected BOQ-linked Juniper IFC rows: {row}")

    return {
        "capability_id": "quantity-takeoff-agent",
        "status": "passed",
        "project_id": DEFAULT_PROJECT_ID,
        "project_target": PROJECT_TARGET,
        "erp_project_id": erp_project_id,
        "erp_project_id_source": erp_project_id_source,
        "proof_lineage": PROOF_LINEAGE,
        "supported_by": SUPPORTED_BY,
        "blockers": [],
        "steps": {
            "quantity_extract": quantity_extract,
            "cost_search_writeback": cost_search_writeback,
            "boq_sync": {
                "project_id": boq_sync["project_id"],
                "result": boq_sync["result"],
            },
            "boq_read": boq_read,
            "boq_export": boq_export,
        },
        "evidence": {
            "ifc_rows": [
                {
                    "source_element_id": str(row["source_element_id"]),
                    "quantity": float(row["quantity"]),
                    "quantity_unit": str(row["quantity_unit"]),
                    "unit_cost": float(row["unit_cost"]),
                    "unit_cost_region": str(row["unit_cost_region"]),
                    "erp_item_id": str(row["erp_item_id"]),
                }
                for row in enriched_rows
            ]
        },
    }
