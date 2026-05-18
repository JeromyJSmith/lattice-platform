#!/usr/bin/env python3
"""Run the live POST /v1/erp/boq proof against current route code and OpenConstructionERP."""

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
if REPO_ROOT.as_posix() not in sys.path:
    sys.path.insert(0, REPO_ROOT.as_posix())
if PIXELTABLE_ROOT.as_posix() not in sys.path:
    sys.path.insert(0, PIXELTABLE_ROOT.as_posix())

from ddc.erp.runtime import (  # noqa: E402
    ensure_erp_verifier_project_id,
    erp_request_kwargs,
    erp_response_detail,
    require_erp_runtime,
    resolve_erp_runtime,
)
from service.idempotency import IdempotencyStore  # noqa: E402
from service.routes import erp  # noqa: E402

ERP_RUNTIME = resolve_erp_runtime()
ERP_BASE = ERP_RUNTIME.base_url
ERP_BOQ_CREATE_PATH = "/api/v1/boq/boqs/"
DEFAULT_PROJECT_ID = (os.environ.get("ERP_BOQ_SYNC_VERIFY_PROJECT_ID") or "").strip() or None
DEFAULT_IDEMPOTENCY_KEY = os.environ.get("ERP_BOQ_SYNC_VERIFY_IDEMPOTENCY_KEY", "ddc-boq-sync-proof-0001")
DEFAULT_BOQ_NAME = os.environ.get("ERP_BOQ_SYNC_VERIFY_NAME", "LATTICE verifier BOQ")
REQUEST_TIMEOUT_SECONDS = 10.0


class _MissingProjectIfcPxt:
    def get_table(self, path: str):
        """Provide the minimum bridge surface needed to reach the writeback blocker."""
        if path == "lattice/bridge/ifc/ifc_elements":
            return {"path": path}
        raise RuntimeError(f"table not found: {path}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-id", default=DEFAULT_PROJECT_ID)
    parser.add_argument("--idempotency-key", default=DEFAULT_IDEMPOTENCY_KEY)
    return parser.parse_args()


def _resolve_project_id(project_id: str | None) -> tuple[str, str]:
    normalized_project_id = (project_id or "").strip()
    if normalized_project_id:
        return normalized_project_id, "arg:project_id"
    return ensure_erp_verifier_project_id(
        env_var_names=("ERP_BOQ_SYNC_VERIFY_PROJECT_ID", "ERP_BOQ_PROJECT_ID"),
    )


def _probe_upstream_create(project_id: str) -> dict[str, Any]:
    erp_runtime = require_erp_runtime()
    url = f"{erp_runtime.base_url}{ERP_BOQ_CREATE_PATH}"
    payload = {
        "project_id": project_id,
        "name": DEFAULT_BOQ_NAME,
        "description": "LATTICE verifier BOQ sync probe",
    }
    try:
        response = httpx.post(
            url,
            json=payload,
            **erp_request_kwargs(
                base_url=erp_runtime.base_url,
                timeout=REQUEST_TIMEOUT_SECONDS,
                follow_redirects=True,
            ),
        )
    except Exception as exc:
        raise RuntimeError(f"OpenConstructionERP BOQ create probe failed for {url}: {exc!s}") from exc
    if response.status_code == 401:
        raise RuntimeError(
            "OpenConstructionERP BOQ create probe returned 401 "
            f"{erp_response_detail(response)} for {url}; "
            "live ERP authentication is required before this capability can pass."
        )
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
    project_id, project_id_source = _resolve_project_id(args.project_id)
    report: dict[str, Any] = {
        "project_id": project_id,
        "project_id_source": project_id_source,
        "erp_base": ERP_BASE,
        "erp_runtime_source": ERP_RUNTIME.source,
        "route": "POST /v1/erp/boq",
    }
    blockers: list[str] = []

    try:
        report["erp_probe"] = _probe_upstream_create(project_id)
    except Exception as exc:
        blockers.append(str(exc))

    try:
        report["route_probe"] = _verify_route(project_id, idempotency_key=args.idempotency_key)
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
