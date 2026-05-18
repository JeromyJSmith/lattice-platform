#!/usr/bin/env python3
"""Run the live GET /v1/erp/boq/{project_id} proof against OpenConstructionERP."""

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
from service.routes import erp  # noqa: E402

ERP_RUNTIME = resolve_erp_runtime()
ERP_BASE = ERP_RUNTIME.base_url
ERP_BOQ_LIST_PATH = "/api/v1/boq/boqs/"
DEFAULT_PROJECT_ID = (os.environ.get("ERP_BOQ_VERIFY_PROJECT_ID") or "").strip() or None
REQUEST_TIMEOUT_SECONDS = 10.0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-id", default=DEFAULT_PROJECT_ID)
    return parser.parse_args()


def _resolve_project_id(project_id: str | None) -> tuple[str, str]:
    normalized_project_id = (project_id or "").strip()
    if normalized_project_id:
        return normalized_project_id, "arg:project_id"
    return ensure_erp_verifier_project_id(
        env_var_names=("ERP_BOQ_VERIFY_PROJECT_ID", "ERP_BOQ_PROJECT_ID"),
    )


def _fetch_upstream_json(project_id: str) -> tuple[str, dict[str, Any] | list[Any]]:
    erp_runtime = require_erp_runtime()
    url = f"{erp_runtime.base_url}{ERP_BOQ_LIST_PATH}"
    try:
        response = httpx.get(
            url,
            params={"project_id": project_id},
            **erp_request_kwargs(
                base_url=erp_runtime.base_url,
                timeout=REQUEST_TIMEOUT_SECONDS,
                follow_redirects=True,
            ),
        )
    except Exception as exc:
        raise RuntimeError(f"OpenConstructionERP BOQ probe failed for {url}: {exc!s}") from exc
    if response.status_code == 401:
        raise RuntimeError(
            "OpenConstructionERP BOQ probe returned 401 "
            f"{erp_response_detail(response)} for {url}?project_id={project_id}; "
            "live ERP authentication is required before this capability can pass."
        )
    if response.status_code == 404:
        raise RuntimeError(
            f"OpenConstructionERP BOQ probe returned 404 for {url}?project_id={project_id}; live dependency or verifier project data is not ready."
        )
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise RuntimeError(f"OpenConstructionERP BOQ probe failed for {url}: {exc!s}") from exc
    try:
        payload = response.json()
    except ValueError as exc:
        raise RuntimeError(f"OpenConstructionERP BOQ probe returned non-JSON payload for {url}.") from exc
    if not isinstance(payload, dict | list):
        raise RuntimeError(f"OpenConstructionERP BOQ probe returned unsupported JSON payload for {url}.")
    if isinstance(payload, list) and not payload:
        raise RuntimeError(
            "OpenConstructionERP BOQ probe returned an empty BOQ list for "
            f"{url}?project_id={project_id}; verifier project data must point at a real ERP project with BOQs."
        )
    return f"{url}?project_id={project_id}", payload


def _build_app() -> FastAPI:
    app = FastAPI()
    app.include_router(erp.router, prefix="/v1/erp")
    return app


def _verify_route(project_id: str) -> dict[str, Any]:
    client = TestClient(_build_app())
    response = client.get(f"/v1/erp/boq/{project_id}")
    body = response.json()
    expected_erp_base = ERP_BASE if ERP_BASE is not None else body.get("erp_base")
    if response.status_code != 200:
        raise RuntimeError(f"/v1/erp/boq/{project_id} returned {response.status_code}: {body}")
    if not isinstance(body, dict):
        raise RuntimeError(f"/v1/erp/boq/{project_id} returned a non-object payload: {body!r}")
    if body.get("ok") is not True:
        raise RuntimeError(f"/v1/erp/boq/{project_id} did not report ok=true: {body}")
    if body.get("project_id") != project_id:
        raise RuntimeError(f"/v1/erp/boq/{project_id} returned mismatched project_id: {body}")
    if body.get("erp_base") != expected_erp_base:
        raise RuntimeError(f"/v1/erp/boq/{project_id} returned mismatched erp_base: {body}")
    payload = body.get("boq")
    if not isinstance(payload, dict | list):
        raise RuntimeError(f"/v1/erp/boq/{project_id} returned unsupported BOQ payload: {body}")
    return {
        "route": f"/v1/erp/boq/{project_id}",
        "payload_kind": "object" if isinstance(payload, dict) else "array",
        "document_size": len(payload),
        "erp_base": body["erp_base"],
    }


def main() -> int:
    """Execute the live BOQ read verifier and exit non-zero when proof fails."""
    args = _parse_args()
    project_id, project_id_source = _resolve_project_id(args.project_id)
    report: dict[str, Any] = {
        "project_id": project_id,
        "project_id_source": project_id_source,
        "erp_base": ERP_BASE,
        "erp_runtime_source": ERP_RUNTIME.source,
        "route": f"/v1/erp/boq/{project_id}",
        "boq_list_contract": f"{ERP_BOQ_LIST_PATH}?project_id={project_id}",
    }
    try:
        upstream_url, upstream_payload = _fetch_upstream_json(project_id)
        report["erp_probe"] = {
            "url": upstream_url,
            "payload_kind": "object" if isinstance(upstream_payload, dict) else "array",
            "document_size": len(upstream_payload),
        }
        report["route_proof"] = _verify_route(project_id)
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
