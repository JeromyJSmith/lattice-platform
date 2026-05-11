"""POST /v1/evidence/promotions — record a draw/validate/promote/reject event."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Body, Depends

from service.deps import (
    get_idem_store,
    get_pxt,
    require_idempotency_key,
    require_local_socket_or_token,
)
from service.routes._idempotent import with_idempotency
from service.upsert import upsert_promotion_event

router = APIRouter(dependencies=[Depends(require_local_socket_or_token)])
log = logging.getLogger("vwbridge.evidence")


@router.post("/promotions")
def post_promotion(
    body: dict[str, Any] = Body(...),
    pxt = Depends(get_pxt),
    store = Depends(get_idem_store),
    idem_key: str = Depends(require_idempotency_key),
):
    def do():
        return {"ok": True, "result": upsert_promotion_event(pxt, body)}
    return with_idempotency(store, idem_key, do)
