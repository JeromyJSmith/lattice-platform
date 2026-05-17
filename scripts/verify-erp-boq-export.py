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
DEFAULT_PROJECT_ID = os.environ.get("ERP_BOQ_EXPORT_VERIFY_PROJECT_ID", "ddc-boq-proof-project")
REQUEST_TIMEOUT_SECONDS = 10.0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-id", default=DEFAULT_PROJECT_ID)
    return parser.parse_args()


def _fetch_upstream_export(project_id: str) -> tuple[str, bytes]:
    url = f"{ERP_BASE}/api/boq/export"
    try:
        response = httpx.get(
            url,
            params={"project_id": project_id, "format": "csv"},
            timeout=REQUEST_TIMEOUT_SECONDS,
            follow_redirects=True,
        )
    except Exception as exc:
        raise RuntimeError(f"OpenConstructionERP BOQ export probe failed for {url}: {exc!s}") from exc
    if response.status_code == 404:
        raise RuntimeError(
            "OpenConstructionERP BOQ export probe returned 404 for "
            f"{url}?project_id={project_id}&format=csv; live dependency or verifier project data is not ready."
        )
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise RuntimeError(f"OpenConstructionERP BOQ export probe failed for {url}: {exc!s}") from exc
    if not response.content:
        raise RuntimeError(
            f"OpenConstructionERP BOQ export probe returned an empty artifact for {url}?project_id={project_id}&format=csv."
        )
    return url, response.content


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
    try:
        upstream_url, upstream_bytes = _fetch_upstream_export(args.project_id)
        route = _verify_route(args.project_id, expected_bytes=upstream_bytes)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "erp_probe": {
                    "url": upstream_url,
                    "format": "csv",
                    "document_size": len(upstream_bytes),
                },
                "route_proof": route,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
