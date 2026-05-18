#!/usr/bin/env python3
"""Run the live POST /v1/erp/phases proof against current route code and local ERP."""

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
ERP_SCHEDULES_PREFIX = os.environ.get("OPENCONSTRUCTIONERP_SCHEDULES_PREFIX", "/api/v2/schedules")
ERP_SCHEDULE_LINKS_PREFIX = os.environ.get("OPENCONSTRUCTIONERP_SCHEDULE_LINKS_PREFIX", "/api/v2/eac/schedule-links")
ERP_SCHEDULE_IMPORT_PATH_TEMPLATE = os.environ.get(
    "OPENCONSTRUCTIONERP_SCHEDULE_IMPORT_PATH_TEMPLATE",
    "/api/v2/schedules/{schedule_id}/import",
)
ERP_TASK_PROGRESS_PATH_TEMPLATE = os.environ.get(
    "OPENCONSTRUCTIONERP_TASK_PROGRESS_PATH_TEMPLATE",
    "/api/v2/schedules/tasks/{task_id}/progress",
)
DEFAULT_PROJECT_ID = os.environ.get("ERP_PHASES_SYNC_VERIFY_PROJECT_ID", "ddc-phases-proof-project")
DEFAULT_IDEMPOTENCY_KEY = os.environ.get(
    "ERP_PHASES_SYNC_VERIFY_IDEMPOTENCY_KEY",
    "ddc-phases-sync-proof-0001",
)
REQUEST_TIMEOUT_SECONDS = 10.0


class _PhaseSyncPrereqPxt:
    def get_table(self, path: str):
        """Return the minimum table set needed to reach the current blocker path."""
        if path in {
            "lattice/projects/ddc-phases-proof-project/ifc_elements",
            "lattice/bridge/marpa_projects",
        }:
            return {"path": path}
        raise RuntimeError(f"table not found: {path}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-id", default=DEFAULT_PROJECT_ID)
    parser.add_argument("--idempotency-key", default=DEFAULT_IDEMPOTENCY_KEY)
    return parser.parse_args()


def _normalize_path(path: str, default: str) -> str:
    normalized = path.strip() or default
    return normalized if normalized.startswith("/") else f"/{normalized}"


def _probe_upstream_phase_endpoint(project_id: str) -> dict[str, Any]:
    schedules_url = f"{ERP_BASE}{_normalize_path(ERP_SCHEDULES_PREFIX, '/api/v2/schedules')}"
    links_url = f"{ERP_BASE}{_normalize_path(ERP_SCHEDULE_LINKS_PREFIX, '/api/v2/eac/schedule-links')}"
    try:
        schedules_response = httpx.get(
            schedules_url,
            timeout=REQUEST_TIMEOUT_SECONDS,
            follow_redirects=True,
        )
        links_response = httpx.get(
            links_url,
            timeout=REQUEST_TIMEOUT_SECONDS,
            follow_redirects=True,
        )
    except Exception as exc:
        raise RuntimeError(
            f"OpenConstructionERP phase probe failed for {schedules_url} or {links_url}: {exc!s}"
        ) from exc
    if schedules_response.status_code == 404 and links_response.status_code == 404:
        raise RuntimeError(
            "OpenConstructionERP phase probe returned 404 for "
            f"{schedules_url} and {links_url}; live ERP phase endpoint contract is not ready "
            "at the bounded schedule surface."
        )
    if schedules_response.status_code >= 500 or links_response.status_code >= 500:
        raise RuntimeError(
            "OpenConstructionERP phase probe returned server errors for "
            f"{schedules_url} ({schedules_response.status_code}) or {links_url} ({links_response.status_code})."
        )
    return {
        "project_id": project_id,
        "schedules_url": schedules_url,
        "schedules_status_code": schedules_response.status_code,
        "schedules_response_kind": schedules_response.headers.get("content-type", "unknown"),
        "schedule_import_contract": _normalize_path(
            ERP_SCHEDULE_IMPORT_PATH_TEMPLATE,
            "/api/v2/schedules/{schedule_id}/import",
        ),
        "links_url": links_url,
        "links_status_code": links_response.status_code,
        "links_response_kind": links_response.headers.get("content-type", "unknown"),
        "task_progress_contract": _normalize_path(
            ERP_TASK_PROGRESS_PATH_TEMPLATE,
            "/api/v2/schedules/tasks/{task_id}/progress",
        ),
    }


def _build_app() -> FastAPI:
    app = FastAPI()
    app.state.idem = IdempotencyStore(REPO_ROOT / ".tmp" / ".verify-erp-phases-sync.idem.json")
    app.state.pxt = _PhaseSyncPrereqPxt()
    app.include_router(erp.router, prefix="/v1/erp")
    return app


def _verify_route(project_id: str, *, idempotency_key: str) -> dict[str, Any]:
    client = TestClient(_build_app())
    response = client.post(
        "/v1/erp/phases",
        json={"project_id": project_id},
        headers={"Idempotency-Key": idempotency_key},
    )
    body = response.json()
    if response.status_code == 200:
        if not isinstance(body, dict):
            raise RuntimeError(f"/v1/erp/phases returned a non-object payload: {body!r}")
        if body.get("ok") is not True:
            raise RuntimeError(f"/v1/erp/phases did not report ok=true: {body}")
        if body.get("project_id") != project_id:
            raise RuntimeError(f"/v1/erp/phases returned mismatched project_id: {body}")
        return {
            "route": "/v1/erp/phases",
            "status_code": response.status_code,
            "result_kind": "object",
        }
    if response.status_code == 501:
        detail = body.get("detail") if isinstance(body, dict) else response.text
        raise RuntimeError(f"/v1/erp/phases is still blocked: {detail}")
    raise RuntimeError(f"/v1/erp/phases returned {response.status_code}: {body}")


def main() -> int:
    """Execute the live phases-sync verifier and exit non-zero when proof fails."""
    args = _parse_args()
    report: dict[str, Any] = {
        "project_id": args.project_id,
        "erp_base": ERP_BASE,
        "route": "POST /v1/erp/phases",
        "phase_probe_surface": {
            "schedules_prefix": _normalize_path(ERP_SCHEDULES_PREFIX, "/api/v2/schedules"),
            "schedule_links_prefix": _normalize_path(
                ERP_SCHEDULE_LINKS_PREFIX,
                "/api/v2/eac/schedule-links",
            ),
            "schedule_import_contract": _normalize_path(
                ERP_SCHEDULE_IMPORT_PATH_TEMPLATE,
                "/api/v2/schedules/{schedule_id}/import",
            ),
            "task_progress_contract": _normalize_path(
                ERP_TASK_PROGRESS_PATH_TEMPLATE,
                "/api/v2/schedules/tasks/{task_id}/progress",
            ),
        },
    }
    blockers: list[str] = []

    try:
        report["erp_probe"] = _probe_upstream_phase_endpoint(args.project_id)
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
