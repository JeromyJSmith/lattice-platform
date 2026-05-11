"""POST /v1/itwin/sync-jobs and /v1/itwin/changed-elements.

These accept *normalized* payloads. The actual Bentley API calls are made
by `service.itwin_adapter` and can also be invoked via:

  POST /v1/itwin/poll   { "imodel_id": "...", "since_changeset_id": "..." }

which fetches changed-elements from Bentley and writes them through.
"""

from __future__ import annotations

import logging
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
from service.upsert import upsert_itwin_changed_elements, upsert_itwin_sync_job

router = APIRouter(dependencies=[Depends(require_local_socket_or_token)])
log = logging.getLogger("vwbridge.itwin")


@router.post("/sync-jobs")
def post_sync_job(
    body: dict[str, Any] = Body(...),
    pxt = Depends(get_pxt),
    store = Depends(get_idem_store),
    idem_key: str = Depends(require_idempotency_key),
):
    if "sync_run_id" not in body:
        raise HTTPException(status_code=400, detail="sync_run_id required")

    def do():
        return {"ok": True, "result": upsert_itwin_sync_job(pxt, body)}

    return with_idempotency(store, idem_key, do)


@router.post("/changed-elements")
def post_changed_elements(
    body: dict[str, Any] = Body(...),
    pxt = Depends(get_pxt),
    store = Depends(get_idem_store),
    idem_key: str = Depends(require_idempotency_key),
):
    if "imodel_id" not in body:
        raise HTTPException(status_code=400, detail="imodel_id required")

    def do():
        return {"ok": True, "result": upsert_itwin_changed_elements(pxt, body)}

    return with_idempotency(store, idem_key, do)


@router.post("/poll")
def post_poll(
    body: dict[str, Any] = Body(...),
    pxt = Depends(get_pxt),
    settings = Depends(get_settings),
    store = Depends(get_idem_store),
    idem_key: str = Depends(require_idempotency_key),
):
    """Server-side poll: fetch changes from Bentley and write through."""
    from service.itwin_adapter import fetch_changed_elements_paginated

    def do():
        results = fetch_changed_elements_paginated(
            settings,
            itwin_id=body["itwin_id"],
            imodel_id=body["imodel_id"],
            since_changeset_id=body.get("since_changeset_id"),
        )
        total = 0
        for page_payload in results:
            r = upsert_itwin_changed_elements(pxt, page_payload)
            total += int(r.get("inserted", 0))
        return {"ok": True, "result": {"inserted_total": total}}

    return with_idempotency(store, idem_key, do)
