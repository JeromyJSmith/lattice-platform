#!/usr/bin/env python3
"""Run the live POST /v1/erp/boq proof against current route code and local OpenConstructionERP."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[1]
PIXELTABLE_ROOT = REPO_ROOT / "pixeltable"
if PIXELTABLE_ROOT.as_posix() not in sys.path:
    sys.path.insert(0, PIXELTABLE_ROOT.as_posix())

from service.idempotency import IdempotencyStore  # noqa: E402
from service.routes import erp  # noqa: E402

ERP_BASE = os.environ.get("OPENCONSTRUCTIONERP_URL", "http://localhost:8080").rstrip("/")
ERP_BOQ_CREATE_PATH = "/api/v1/boq/boqs/"
DEFAULT_PROJECT_ID = os.environ.get("ERP_BOQ_SYNC_VERIFY_PROJECT_ID", "ddc-boq-proof-project")
DEFAULT_IDEMPOTENCY_KEY = os.environ.get("ERP_BOQ_SYNC_VERIFY_IDEMPOTENCY_KEY", "ddc-boq-sync-proof-0001")
DEFAULT_BOQ_NAME = os.environ.get("ERP_BOQ_SYNC_VERIFY_NAME", "LATTICE verifier BOQ")
REQUEST_TIMEOUT_SECONDS = 10.0


class _MissingProjectIfcPxt:
    def get_table(self, path: str):
        """Mirror the current missing project-table blocker seen by BOQ sync."""
        raise RuntimeError(f"table not found: {path}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-id", default=DEFAULT_PROJECT_ID)
    parser.add_argument("--idempotency-key", default=DEFAULT_IDEMPOTENCY_KEY)
    return parser.parse_args()


def _probe_upstream_create(project_id: str) -> dict[str, Any]:
    url = f"{ERP_BASE}{ERP_BOQ_CREATE_PATH}"
    payload = {
        "project_id": project_id,
        "name": DEFAULT_BOQ_NAME,
        "description": "LATTICE verifier BOQ sync probe",
    }
    try:
        response = httpx.post(
            url,
            json=payload,
            timeout=REQUEST_TIMEOUT_SECONDS,
            follow_redirects=True,
        )
    except Exception as exc:
        raise RuntimeError(f"OpenConstructionERP BOQ create probe failed for {url}: {exc!s}") from exc
    if response.status_code == 404:
        raise RuntimeError(
            f"OpenConstructionERP BOQ create probe returned 404 for {url}; live ERP create contract is not ready."
        )
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise RuntimeError(f"OpenConstructionERP BOQ create probe failed for {url}: {exc!s}") from exc

    try:
        response_payload: dict[str, Any] | list[Any] | str = response.json()
    except ValueError:
        response_payload = response.text
    return {
        "url": url,
        "status_code": response.status_code,
        "request_contract": {
            "project_id": project_id,
            "name": DEFAULT_BOQ_NAME,
            "description": "LATTICE verifier BOQ sync probe",
        },
        "response_kind": (
            "object"
            if isinstance(response_payload, dict)
            else "array"
            if isinstance(response_payload, list)
            else "text"
        ),
    }


def _build_app() -> FastAPI:
    app = FastAPI()
    app.state.idem = IdempotencyStore(REPO_ROOT / ".tmp" / ".verify-erp-boq-sync.idem.json")
    app.state.pxt = _MissingProjectIfcPxt()
    app.include_router(erp.router, prefix="/v1/erp")
    return app


def _verify_route(project_id: str, *, idempotency_key: str) -> dict[str, Any]:
    client = TestClient(_build_app())
    response = client.post(
        "/v1/erp/boq",
        json={"project_id": project_id},
        headers={"Idempotency-Key": idempotency_key},
    )
    body = response.json()
    if response.status_code == 200:
        if not isinstance(body, dict):
            raise RuntimeError(f"/v1/erp/boq returned a non-object payload: {body!r}")
        if body.get("ok") is not True:
            raise RuntimeError(f"/v1/erp/boq did not report ok=true: {body}")
        if body.get("project_id") != project_id:
            raise RuntimeError(f"/v1/erp/boq returned mismatched project_id: {body}")
        return {
            "route": "/v1/erp/boq",
            "status_code": response.status_code,
            "result_kind": "object",
        }
    if response.status_code == 501:
        detail = body.get("detail") if isinstance(body, dict) else response.text
        raise RuntimeError(f"/v1/erp/boq is still blocked: {detail}")
    raise RuntimeError(f"/v1/erp/boq returned {response.status_code}: {body}")


def main() -> int:
    """Execute the live BOQ sync verifier and exit non-zero when proof fails."""
    args = _parse_args()
    report: dict[str, Any] = {
        "project_id": args.project_id,
        "erp_base": ERP_BASE,
        "route": "POST /v1/erp/boq",
    }
    blockers: list[str] = []

    try:
        report["erp_probe"] = _probe_upstream_create(args.project_id)
    except Exception as exc:
        blockers.append(str(exc))

    try:
        report["route_probe"] = _verify_route(args.project_id, idempotency_key=args.idempotency_key)
    except Exception as exc:
        blockers.append(str(exc))

    if blockers:
        report["status"] = "blocked"
        report["blockers"] = blockers
        print(json.dumps(report, indent=2), file=sys.stderr)
        return 1

    report["status"] = "passed"
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
