"""Runtime ledger routes.

- POST /v1/runtime/events            — bulk-ingest TS RuntimeEvents (idempotent).
- GET  /v1/runtime/runs              — list rows from `lattice/execution/agent_runs`.
- GET  /v1/runtime/stream-events     — paginated read of stream events for a run.
- GET  /v1/runtime/stream-events/sse — live SSE push of stream events for a run.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from fastapi import APIRouter, Body, Depends, Query, Request
from fastapi.responses import StreamingResponse

from service.deps import (
    get_idem_store,
    get_pxt,
    require_idempotency_key,
    require_local_socket_or_token,
)
from service.routes._idempotent import with_idempotency
from service.upsert import upsert_runtime_events
from service.worker import subscribe, unsubscribe

router = APIRouter(dependencies=[Depends(require_local_socket_or_token)])
log = logging.getLogger("vwbridge.runtime")


@router.post("/events")
def post_events(
    body: dict[str, Any] = Body(...),
    pxt = Depends(get_pxt),
    store = Depends(get_idem_store),
    idem_key: str = Depends(require_idempotency_key),
):
    events = body.get("events") or []
    if not isinstance(events, list):
        return {"error": "events must be a list", "received_type": type(events).__name__}

    def do() -> dict[str, Any]:
        log.info("ingesting %d runtime events (key=%s)", len(events), idem_key,
                 extra={"idempotency_key": idem_key, "route": "/v1/runtime/events"})
        result = upsert_runtime_events(pxt, events)
        return {"ok": True, "result": result}

    return with_idempotency(store, idem_key, do)


@router.get("/runs")
def list_runs(
    pxt = Depends(get_pxt),
    limit: int = Query(default=100, ge=1, le=1000),
    include_mock: bool = Query(default=False),
):
    """Return the most recent rows from `lattice/execution/agent_runs`.

    Output rows expose the fields the operator console renders:
    run_id, status, agent_kind, started_at (ISO-8601 UTC).
    """
    t = pxt.get_table("lattice/execution/agent_runs")
    df = t.select(
        t.run_id, t.status, t.agent_kind, t.started_at, t.raw_event,
    ).collect()
    rows = []
    for r in df:
        started = r.get("started_at")
        raw = r.get("raw_event") or {}
        payload = raw.get("payload") if isinstance(raw, dict) else None
        task = (payload or {}).get("task", "") if isinstance(payload, dict) else ""
        rows.append({
            "run_id":     r.get("run_id") or "",
            "status":     r.get("status") or "",
            "agent_kind": r.get("agent_kind") or "",
            "task":       task or "",
            "started_at": started.isoformat() if started is not None else None,
        })
    if not include_mock:
        rows = [row for row in rows if (row.get("agent_kind") or "").lower() != "mock"]
    rows.sort(key=lambda x: x["started_at"] or "", reverse=True)
    return {"rows": rows[:limit], "count": len(rows)}


@router.get("/stream-events")
def list_stream_events(
    pxt = Depends(get_pxt),
    run_id: str = Query(..., min_length=1, max_length=256),
    after_seq: int = Query(default=0, ge=0),
    limit: int = Query(default=500, ge=1, le=2000),
):
    """Return `agent_stream_events` rows for a given run, ordered by seq.

    `after_seq` lets the client poll incrementally — pass the highest seq
    seen so far and only newer events come back.
    """
    t = pxt.get_table("lattice/execution/agent_stream_events")
    df = t.where(t.run_id == run_id).select(
        t.event_id, t.event_kind, t.seq, t.delta_text, t.tool_name, t.created_at,
    ).collect()

    rows = []
    for r in df:
        seq = int(r.get("seq") or 0)
        if seq <= after_seq:
            continue
        created = r.get("created_at")
        rows.append({
            "event_id":   r.get("event_id") or "",
            "event_kind": r.get("event_kind") or "",
            "seq":        seq,
            "delta_text": r.get("delta_text") or "",
            "tool_name":  r.get("tool_name") or "",
            "created_at": created.isoformat() if created is not None else None,
        })
    rows.sort(key=lambda x: x["seq"])
    return {"rows": rows[:limit], "count": len(rows), "run_id": run_id}


# The SSE endpoint deliberately bypasses the router-level auth dependency: a
# browser EventSource cannot set custom auth headers reliably, and we're on
# localhost-only TCP for now. If/when this becomes public, wire a signed
# query-param token here.
@router.get("/stream-events/sse", dependencies=[])
async def sse_stream_events(
    request: Request,
    run_id: str = Query(..., min_length=1, max_length=256),
    pxt = Depends(get_pxt),
):
    """Server-Sent Events: live `stream.delta` events for `run_id`.

    On connect, the historical events for `run_id` are flushed first, then
    the connection stays open and pushes new deltas as the worker produces
    them. A terminal `event: end` is sent when the run completes (or when
    the client disconnects).
    """
    queue = subscribe(run_id)

    async def gen():
        seen_event_ids: set[str] = set()
        try:
            # 1. Replay historical events from Pixeltable.
            t = pxt.get_table("lattice/execution/agent_stream_events")
            df = await asyncio.to_thread(
                lambda: t.where(t.run_id == run_id).select(
                    t.event_id, t.event_kind, t.seq, t.delta_text,
                    t.tool_name, t.created_at,
                ).collect()
            )
            historical = []
            for r in df:
                created = r.get("created_at")
                historical.append({
                    "event_id":   r.get("event_id") or "",
                    "event_kind": r.get("event_kind") or "",
                    "seq":        int(r.get("seq") or 0),
                    "delta_text": r.get("delta_text") or "",
                    "tool_name":  r.get("tool_name") or "",
                    "created_at": created.isoformat() if created is not None else None,
                })
            historical.sort(key=lambda x: x["seq"])
            for ev in historical:
                seen_event_ids.add(ev["event_id"])
                yield f"event: delta\ndata: {json.dumps(ev)}\n\n"

            # 2. Live tail from the worker pub/sub queue.
            while True:
                if await request.is_disconnected():
                    return
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=15.0)
                except asyncio.TimeoutError:
                    # Keep-alive comment so proxies don't drop the connection.
                    yield ": keep-alive\n\n"
                    continue
                if event.get("type") == "run.completed":
                    yield f"event: end\ndata: {json.dumps(event)}\n\n"
                    return
                eid = event.get("event_id")
                if eid and eid in seen_event_ids:
                    continue
                if eid:
                    seen_event_ids.add(eid)
                yield f"event: delta\ndata: {json.dumps(event)}\n\n"
        finally:
            unsubscribe(run_id, queue)

    return StreamingResponse(
        gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # disable any intermediary buffering
        },
    )
