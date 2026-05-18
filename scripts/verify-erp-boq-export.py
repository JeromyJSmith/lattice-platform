#!/usr/bin/env python3
"""Run the live GET /v1/erp/export/{project_id} proof against local OpenConstructionERP."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import httpx
from fastapi import FastAPI
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[1]
PIXELTABLE_ROOT = REPO_ROOT / "pixeltable"
if PIXELTABLE_ROOT.as_posix() not in sys.path:
    sys.path.insert(0, PIXELTABLE_ROOT.as_posix())

from service.routes import erp  # noqa: E402

ERP_BASE = os.environ.get("OPENCONSTRUCTIONERP_URL", "http://localhost:8080").rstrip("/")
ERP_BOQ_LIST_PATH = "/api/v1/boq/boqs/"
ERP_BOQ_EXPORT_PATH_TEMPLATE = "/api/v1/boq/boqs/{boq_id}/export/{export_kind}"
DEFAULT_PROJECT_ID = os.environ.get("ERP_BOQ_EXPORT_VERIFY_PROJECT_ID", "ddc-boq-proof-project")
DEFAULT_BOQ_ID = (os.environ.get("ERP_BOQ_EXPORT_VERIFY_BOQ_ID") or "").strip() or None
REQUEST_TIMEOUT_SECONDS = 10.0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-id", default=DEFAULT_PROJECT_ID)
    parser.add_argument("--boq-id", default=DEFAULT_BOQ_ID)
    return parser.parse_args()


def _resolve_boq_id(project_id: str, boq_id: str | None) -> tuple[str, str]:
    if boq_id is not None:
        return "env:ERP_BOQ_EXPORT_VERIFY_BOQ_ID", boq_id
    list_url = f"{ERP_BASE}{ERP_BOQ_LIST_PATH}"
    try:
        response = httpx.get(
            list_url,
            params={"project_id": project_id},
            timeout=REQUEST_TIMEOUT_SECONDS,
            follow_redirects=True,
        )
    except Exception as exc:
        raise RuntimeError(f"OpenConstructionERP BOQ export probe failed for {list_url}: {exc!s}") from exc
    if response.status_code == 404:
        raise RuntimeError(
            "OpenConstructionERP BOQ export probe returned 404 for "
            f"{list_url}?project_id={project_id}; live dependency or verifier project data is not ready."
        )
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise RuntimeError(f"OpenConstructionERP BOQ export probe failed for {list_url}: {exc!s}") from exc
    try:
        payload = response.json()
    except ValueError as exc:
        raise RuntimeError(f"OpenConstructionERP BOQ export probe returned non-JSON payload for {list_url}.") from exc
    if not isinstance(payload, list) or not all(isinstance(row, dict) for row in payload):
        raise RuntimeError(f"OpenConstructionERP BOQ export probe returned unsupported JSON payload for {list_url}.")
    if not payload:
        raise RuntimeError(
            "OpenConstructionERP BOQ export probe found no BOQs for "
            f"{list_url}?project_id={project_id}; verifier data must include a project with an existing BOQ."
        )
    resolved_boq_id = payload[0].get("id")
    if not isinstance(resolved_boq_id, str) or not resolved_boq_id.strip():
        raise RuntimeError(f"OpenConstructionERP BOQ export probe did not find a usable BOQ id in {list_url}.")
    return f"{list_url}?project_id={project_id}", resolved_boq_id.strip()


def _fetch_upstream_export(project_id: str, boq_id: str | None = None) -> tuple[str, bytes, str]:
    resolution_source, resolved_boq_id = _resolve_boq_id(project_id, boq_id)
    url = f"{ERP_BASE}{ERP_BOQ_EXPORT_PATH_TEMPLATE.format(boq_id=resolved_boq_id, export_kind='csv')}"
    try:
        response = httpx.get(
            url,
            timeout=REQUEST_TIMEOUT_SECONDS,
            follow_redirects=True,
        )
    except Exception as exc:
        raise RuntimeError(f"OpenConstructionERP BOQ export probe failed for {url}: {exc!s}") from exc
    if response.status_code == 404:
        raise RuntimeError(
            "OpenConstructionERP BOQ export probe returned 404 for "
            f"{url}; live dependency or verifier project data is not ready."
        )
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise RuntimeError(f"OpenConstructionERP BOQ export probe failed for {url}: {exc!s}") from exc
    if not response.content:
        raise RuntimeError(
            f"OpenConstructionERP BOQ export probe returned an empty artifact for {url}."
        )
    return url, response.content, resolution_source


def _build_app() -> FastAPI:
    app = FastAPI()
    app.include_router(erp.router, prefix="/v1/erp")
    return app


def _verify_route(project_id: str, *, expected_bytes: bytes) -> dict[str, object]:
    client = TestClient(_build_app())
    response = client.get(f"/v1/erp/export/{project_id}?fmt=csv")
    if response.status_code != 200:
        raise RuntimeError(f"/v1/erp/export/{project_id}?fmt=csv returned {response.status_code}: {response.text}")
    content_type = response.headers.get("content-type", "").split(";", 1)[0]
    if content_type != "text/csv":
        raise RuntimeError(
            f"/v1/erp/export/{project_id}?fmt=csv returned unexpected content-type: {response.headers.get('content-type')}"
        )
    filename = response.headers.get("content-disposition", "")
    if "filename=" not in filename:
        raise RuntimeError(f"/v1/erp/export/{project_id}?fmt=csv did not expose a download filename.")
    if response.content != expected_bytes:
        raise RuntimeError(f"/v1/erp/export/{project_id}?fmt=csv did not match the upstream export bytes.")
    filename_value = filename.split("filename=", 1)[1].strip().strip('"')
    return {
        "route": f"/v1/erp/export/{project_id}?fmt=csv",
        "content_type": content_type,
        "filename": filename_value,
        "document_size": len(response.content),
    }


def main() -> int:
    """Execute the live BOQ export verifier and exit non-zero when proof fails."""
    args = _parse_args()
    report = {
        "project_id": args.project_id,
        "boq_id": args.boq_id,
        "erp_base": ERP_BASE,
        "route": f"/v1/erp/export/{args.project_id}?fmt=csv",
        "boq_list_contract": f"{ERP_BOQ_LIST_PATH}?project_id={args.project_id}",
    }
    try:
        upstream_url, upstream_bytes, boq_resolution = _fetch_upstream_export(args.project_id, args.boq_id)
        report["erp_probe"] = {
            "url": upstream_url,
            "boq_resolution": boq_resolution,
            "format": "csv",
            "document_size": len(upstream_bytes),
        }
        report["route_proof"] = _verify_route(args.project_id, expected_bytes=upstream_bytes)
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
