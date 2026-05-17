#!/usr/bin/env python3
"""Run the live GET /v1/erp/boq/{project_id} proof against local OpenConstructionERP."""

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

from service.routes import erp  # noqa: E402

ERP_BASE = os.environ.get("OPENCONSTRUCTIONERP_URL", "http://localhost:8080").rstrip("/")
DEFAULT_PROJECT_ID = os.environ.get("ERP_BOQ_VERIFY_PROJECT_ID", "ddc-boq-proof-project")
REQUEST_TIMEOUT_SECONDS = 10.0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-id", default=DEFAULT_PROJECT_ID)
    return parser.parse_args()


def _fetch_upstream_json(project_id: str) -> tuple[str, dict[str, Any] | list[Any]]:
    url = f"{ERP_BASE}/api/boq/{project_id}"
    try:
        response = httpx.get(url, timeout=REQUEST_TIMEOUT_SECONDS, follow_redirects=True)
    except Exception as exc:
        raise RuntimeError(f"OpenConstructionERP BOQ probe failed for {url}: {exc!s}") from exc
    if response.status_code == 404:
        raise RuntimeError(
            f"OpenConstructionERP BOQ probe returned 404 for {url}; live dependency or verifier project data is not ready."
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
    return url, payload


def _build_app() -> FastAPI:
    app = FastAPI()
    app.include_router(erp.router, prefix="/v1/erp")
    return app


def _verify_route(project_id: str) -> dict[str, Any]:
    client = TestClient(_build_app())
    response = client.get(f"/v1/erp/boq/{project_id}")
    body = response.json()
    if response.status_code != 200:
        raise RuntimeError(f"/v1/erp/boq/{project_id} returned {response.status_code}: {body}")
    if not isinstance(body, dict):
        raise RuntimeError(f"/v1/erp/boq/{project_id} returned a non-object payload: {body!r}")
    if body.get("ok") is not True:
        raise RuntimeError(f"/v1/erp/boq/{project_id} did not report ok=true: {body}")
    if body.get("project_id") != project_id:
        raise RuntimeError(f"/v1/erp/boq/{project_id} returned mismatched project_id: {body}")
    if body.get("erp_base") != ERP_BASE:
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
    try:
        upstream_url, upstream_payload = _fetch_upstream_json(args.project_id)
        route = _verify_route(args.project_id)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "erp_probe": {
                    "url": upstream_url,
                    "payload_kind": "object" if isinstance(upstream_payload, dict) else "array",
                    "document_size": len(upstream_payload),
                },
                "route_proof": route,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
