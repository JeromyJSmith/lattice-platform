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
PROOF_ARTIFACT_GLOB = "*-boq-*-proof.json"


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
        return _Predicate(lambda row: row.get(self.name) in {other, "*"})


class _Query:
    def __init__(self, rows: list[dict[str, Any]]):
        self._rows = rows

    def collect(self) -> list[dict[str, Any]]:
        """Return the fake query rows."""
        return list(self._rows)


class _VerifierIfcTable:
    project_id = _Column("project_id")
    source_element_id = _Column("source_element_id")

    def __init__(self):
        self.rows = [
            {
                "project_id": "*",
                "source_element_id": "ifc-verifier-001",
                "name": "Verifier element",
                "quantity": 1.0,
                "quantity_unit": "ea",
                "unit_cost": 0.0,
            }
        ]

    def where(self, predicate: _Predicate) -> _Query:
        """Filter the fake IFC rows by the provided predicate."""
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
    def __init__(self):
        self._ifc_table = _VerifierIfcTable()

    def get_table(self, path: str):
        """Provide the minimum bridge surface needed to reach the live ERP sync path."""
        if path == "lattice/bridge/ifc/ifc_elements":
            return self._ifc_table
        raise RuntimeError(f"table not found: {path}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-id", default=DEFAULT_PROJECT_ID)
    parser.add_argument("--idempotency-key", default=DEFAULT_IDEMPOTENCY_KEY)
    return parser.parse_args()


def _project_id_from_proof_artifact(path: Path) -> tuple[str, str] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    candidates: list[dict[str, Any]] = []
    if isinstance(payload, dict):
        candidates.append(payload)
        stdout = payload.get("stdout")
        if isinstance(stdout, str) and stdout.strip():
            try:
                nested = json.loads(stdout)
            except json.JSONDecodeError:
                nested = None
            if isinstance(nested, dict):
                candidates.append(nested)
    for candidate in candidates:
        if candidate.get("status") != "passed":
            continue
        project_id = candidate.get("project_id")
        if isinstance(project_id, str) and project_id.strip():
            return project_id.strip(), f"proof:{path.relative_to(REPO_ROOT).as_posix()}"
    return None


def _resolve_project_id_from_proofs() -> tuple[str, str] | None:
    sessions_dir = REPO_ROOT / "meta" / "harness" / "docs" / "sessions"
    if not sessions_dir.exists():
        return None
    for proof_path in sorted(sessions_dir.glob(PROOF_ARTIFACT_GLOB), reverse=True):
        if "boq-sync" in proof_path.name:
            continue
        resolved = _project_id_from_proof_artifact(proof_path)
        if resolved is not None:
            return resolved
    return None


def _resolve_project_id(project_id: str | None) -> tuple[str, str]:
    normalized_project_id = (project_id or "").strip()
    if normalized_project_id:
        return normalized_project_id, "arg:project_id"
    for env_var_name in (
        "ERP_BOQ_SYNC_VERIFY_PROJECT_ID",
        "ERP_BOQ_PROJECT_ID",
        "ERP_BOQ_EXPORT_VERIFY_PROJECT_ID",
        "ERP_BOQ_READ_VERIFY_PROJECT_ID",
    ):
        candidate = (os.environ.get(env_var_name) or "").strip()
        if candidate:
            return candidate, f"env:{env_var_name}"
    proof_project_id = _resolve_project_id_from_proofs()
    if proof_project_id is not None:
        return proof_project_id
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
    app.state.pxt = _VerifierPxt()
    app.include_router(erp.router, prefix="/v1/erp")
    return app


def _route_idempotency_key(project_id: str, idempotency_key: str) -> str:
    return f"{idempotency_key}:{project_id}"


def _verify_route(project_id: str, *, idempotency_key: str) -> dict[str, Any]:
    client = TestClient(_build_app())
    response = client.post(
        "/v1/erp/boq",
        json={"project_id": project_id},
        headers={"Idempotency-Key": _route_idempotency_key(project_id, idempotency_key)},
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
    if response.status_code in {501, 502}:
        detail = body.get("detail") if isinstance(body, dict) else response.text
        raise RuntimeError(f"/v1/erp/boq is still blocked: {detail}")
    raise RuntimeError(f"/v1/erp/boq returned {response.status_code}: {body}")


def main() -> int:
    """Execute the live BOQ sync verifier and exit non-zero when proof fails."""
    args = _parse_args()
    report: dict[str, Any] = {
        "erp_base": ERP_BASE,
        "erp_runtime_source": ERP_RUNTIME.source,
        "route": "POST /v1/erp/boq",
    }
    blockers: list[str] = []

    try:
        project_id, project_id_source = _resolve_project_id(args.project_id)
    except Exception as exc:
        report["status"] = "blocked"
        report["blockers"] = [f"BOQ verifier project bootstrap failed: {exc!s}"]
        print(json.dumps(report, indent=2), file=sys.stderr)
        return 1

    report["project_id"] = project_id
    report["project_id_source"] = project_id_source

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
