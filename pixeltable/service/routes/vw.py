"""POST /v1/vw/sidecars — ingest a Vectorworks sidecar.json + IFC pointer.

If `payload.ifc_path` is present and the file exists, the IFC parser is
invoked server-side to enrich/replace `payload.elements` before storage.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException

from service.deps import (
    get_idem_store,
    get_pxt,
    get_settings,
    require_idempotency_key,
    require_local_socket_or_token,
)
from service.routes._idempotent import with_idempotency
from service.upsert import upsert_vw_sidecar

router = APIRouter(dependencies=[Depends(require_local_socket_or_token)])
log = logging.getLogger("vwbridge.vw")


@router.post("/sidecars")
def post_sidecar(
    body: dict[str, Any] = Body(...),
    pxt = Depends(get_pxt),
    settings = Depends(get_settings),
    store = Depends(get_idem_store),
    idem_key: str = Depends(require_idempotency_key),
):
    if "vw_export_hash" not in body:
        raise HTTPException(status_code=400, detail="vw_export_hash required")

    ifc_path = body.get("ifc_path") or body.get("ifc", {}).get("path")
    if ifc_path and Path(ifc_path).exists():
        try:
            from service.ifc_parser import enrich_payload_with_ifc
            body = enrich_payload_with_ifc(body, Path(ifc_path), settings)
        except Exception as exc:
            log.warning("IFC enrichment failed for %s: %s", ifc_path, exc)
            body.setdefault("exporter_warnings", []).append(
                f"ifc_parse_failed: {exc!s}")

    def do() -> dict[str, Any]:
        log.info("ingesting sidecar %s elements=%d (key=%s)",
                 body["vw_export_hash"], len(body.get("elements") or []), idem_key,
                 extra={
                     "idempotency_key": idem_key,
                     "vw_export_hash": body["vw_export_hash"],
                     "harness_run_id": body.get("harness_run_id", ""),
                     "route": "/v1/vw/sidecars",
                 })
        result = upsert_vw_sidecar(pxt, body)
        return {"ok": True, "result": result}

    return with_idempotency(store, idem_key, do)
