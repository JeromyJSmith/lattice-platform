"""POST /v1/health/drift, GET /v1/health/gap-matrix/{vw_export_hash}."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException

from service.deps import (
    get_idem_store,
    get_pxt,
    require_idempotency_key,
    require_local_socket_or_token,
)
from service.routes._idempotent import with_idempotency
from service.upsert import insert_drift_event

router = APIRouter(dependencies=[Depends(require_local_socket_or_token)])
log = logging.getLogger("vwbridge.health")


@router.post("/drift")
def post_drift(
    body: dict[str, Any] = Body(...),
    pxt = Depends(get_pxt),
    store = Depends(get_idem_store),
    idem_key: str = Depends(require_idempotency_key),
):
    def do():
        return {"ok": True, "result": insert_drift_event(pxt, body)}
    return with_idempotency(store, idem_key, do)


@router.get("/gap-matrix/{vw_export_hash}")
def get_gap_matrix(vw_export_hash: str, pxt = Depends(get_pxt)):
    if not vw_export_hash or len(vw_export_hash) > 256:
        raise HTTPException(status_code=400, detail="invalid vw_export_hash")
    try:
        t = pxt.get_table("lattice/bridge/health/bridge_gap_matrix")
        rows = t.where(t.vw_export_hash == vw_export_hash).collect()
        try:
            data = [dict(r) for r in rows]
        except Exception:
            data = list(rows)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"query failed: {exc!s}")
    return {"ok": True, "vw_export_hash": vw_export_hash, "rows": data}
