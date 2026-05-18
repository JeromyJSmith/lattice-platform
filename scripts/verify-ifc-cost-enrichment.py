#!/usr/bin/env python3
"""Run the bounded Juniper IFC cost-writeback proof against the ERP cost-search route."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[1]
PIXELTABLE_ROOT = REPO_ROOT / "pixeltable"
if PIXELTABLE_ROOT.as_posix() not in sys.path:
    sys.path.insert(0, PIXELTABLE_ROOT.as_posix())

from service.routes import erp  # noqa: E402

DEFAULT_PROJECT_ID = "918-juniper"
DEFAULT_SOURCE_ELEMENT_ID = "ifc-juniper-001"


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
        """Return the filtered fake IFC rows."""
        return list(self._rows)


class _VerifierIfcTable:
    project_id = _Column("project_id")
    source_element_id = _Column("source_element_id")

    def __init__(self) -> None:
        self.rows = [
            {
                "project_id": DEFAULT_PROJECT_ID,
                "source_element_id": DEFAULT_SOURCE_ELEMENT_ID,
                "name": "Juniper planting bed",
                "unit_cost": None,
                "unit_cost_region": None,
                "cost_last_updated": None,
            },
            {
                "project_id": "other-project",
                "source_element_id": DEFAULT_SOURCE_ELEMENT_ID,
                "name": "Control row",
                "unit_cost": None,
                "unit_cost_region": None,
                "cost_last_updated": None,
            },
        ]

    def where(self, predicate: _Predicate) -> _Query:
        """Filter the fake IFC rows by predicate."""
        return _Query([row for row in self.rows if predicate(row)])

    def collect(self) -> list[dict[str, Any]]:
        """Expose the fake IFC rows."""
        return list(self.rows)

    def update(self, values: dict[str, Any], where: _Predicate | None = None) -> None:
        """Apply writeback updates to matching fake IFC rows."""
        for row in self.rows:
            if where is None or where(row):
                row.update(values)


class _VerifierPxt:
    def __init__(self) -> None:
        self.table = _VerifierIfcTable()

    def get_table(self, path: str) -> Any:
        """Return the fake bridge IFC table."""
        if path == "lattice/bridge/ifc/ifc_elements":
            return self.table
        raise RuntimeError(f"table not found: {path}")


def _build_app(pxt: _VerifierPxt) -> FastAPI:
    app = FastAPI()
    app.state.pxt = pxt
    app.include_router(erp.router, prefix="/v1/erp")
    return app


def _verify_route() -> dict[str, Any]:
    pxt = _VerifierPxt()
    original_search = erp._COST_SEARCH.search
    erp._COST_SEARCH.search = lambda description, region, top: [
        {
            "item_id": "CWICR-JUNIPER-001",
            "name": description,
            "unit": "ea",
            "unit_cost": 47.5,
            "unit_currency": "USD",
            "unit_cost_region": region,
            "score": 0.91,
            "retrieval_mode": "lexical",
        }
    ]
    try:
        client = TestClient(_build_app(pxt))
        response = client.post(
            "/v1/erp/cost-search",
            json={
                "description": "Juniper planting bed",
                "region": "US",
                "top": 3,
                "project_id": DEFAULT_PROJECT_ID,
                "source_element_id": DEFAULT_SOURCE_ELEMENT_ID,
                "writeback": True,
            },
        )
    finally:
        erp._COST_SEARCH.search = original_search
    body = response.json()
    if response.status_code != 200:
        raise RuntimeError(f"/v1/erp/cost-search returned {response.status_code}: {body}")
    if body.get("verification", {}).get("status") != "passed":
        raise RuntimeError(f"/v1/erp/cost-search did not produce passed verification: {body}")
    writeback = body.get("writeback")
    if not isinstance(writeback, dict) or writeback.get("status") != "passed":
        raise RuntimeError(f"/v1/erp/cost-search did not produce passed writeback proof: {body}")
    juniper_row = next(row for row in pxt.table.rows if row["project_id"] == DEFAULT_PROJECT_ID)
    control_row = next(row for row in pxt.table.rows if row["project_id"] == "other-project")
    if juniper_row.get("unit_cost") != 47.5 or juniper_row.get("unit_cost_region") != "US":
        raise RuntimeError(f"Juniper IFC row was not enriched correctly: {juniper_row}")
    if control_row.get("unit_cost") is not None:
        raise RuntimeError(f"Non-Juniper control row should not have been mutated: {control_row}")
    return {
        "route": "/v1/erp/cost-search",
        "project_id": DEFAULT_PROJECT_ID,
        "source_element_id": DEFAULT_SOURCE_ELEMENT_ID,
        "status_code": response.status_code,
        "writeback": writeback,
        "top_item_id": body["rows"][0]["item_id"],
    }


def main() -> int:
    """Execute the bounded IFC cost-enrichment proof and return a verifier exit code."""
    report: dict[str, Any] = {
        "capability_id": "ifc-cost-enrichment",
        "route": "POST /v1/erp/cost-search",
        "project_id": DEFAULT_PROJECT_ID,
        "source_element_id": DEFAULT_SOURCE_ELEMENT_ID,
    }
    try:
        report["proof"] = _verify_route()
    except Exception as exc:
        report["status"] = "blocked"
        report["blockers"] = [str(exc)]
        print(json.dumps(report, indent=2), file=sys.stderr)
        return 1
    report["status"] = "passed"
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
