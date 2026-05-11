"""POST /v1/marpa/parse-runs — record a MARPA parse outcome.

If `body.run_inline = true`, also invokes the runner against
`body.input_tokens` before recording the result.
"""

from __future__ import annotations

import datetime as dt
import logging
import time
from typing import Any

from fastapi import APIRouter, Body, Depends

from service.deps import (
    get_idem_store,
    get_pxt,
    get_settings,
    require_idempotency_key,
    require_local_socket_or_token,
)
from service.routes._idempotent import with_idempotency
from service.upsert import upsert_marpa_parse_run

router = APIRouter(dependencies=[Depends(require_local_socket_or_token)])
log = logging.getLogger("vwbridge.marpa")


@router.post("/parse-runs")
def post_parse_run(
    body: dict[str, Any] = Body(...),
    pxt = Depends(get_pxt),
    settings = Depends(get_settings),
    store = Depends(get_idem_store),
    idem_key: str = Depends(require_idempotency_key),
):
    if body.get("run_inline"):
        from service.marpa_runner import run_marpa
        started = dt.datetime.now(dt.timezone.utc)
        t0 = time.perf_counter()
        result = run_marpa(
            tokens=body.get("input_tokens", []),
            grammar_version=body.get("grammar_version") or settings.MARPA_GRAMMAR_VERSION,
        )
        ended = dt.datetime.now(dt.timezone.utc)
        body.update({
            "parse_status":       result.parse_status,
            "ambiguity_score":    result.ambiguity_score,
            "partial_parse_json": result.record,
            "error_message":      result.error_message,
            "duration_ms":        int((time.perf_counter() - t0) * 1000),
            "runner_kind":        result.runner_kind,
            "started_at":         started,
            "ended_at":           ended,
            "grammar_version":    body.get("grammar_version") or settings.MARPA_GRAMMAR_VERSION,
        })

    def do():
        return {"ok": True, "result": upsert_marpa_parse_run(pxt, body)}

    return with_idempotency(store, idem_key, do)
