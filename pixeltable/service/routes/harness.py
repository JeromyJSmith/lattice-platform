"""Meta-Harness routes — health snapshots, proposals, events, ratchet cycles.

- GET  /v1/harness/health                  — aggregate health across all sections
- GET  /v1/harness/health/{section}        — per-section health breakdown
- POST /v1/harness/proposals               — submit a harness proposal
- GET  /v1/harness/proposals               — list proposals (filterable)
- GET  /v1/harness/events                  — section events log (filterable)
- POST /v1/harness/ratchet                 — trigger a ratchet cycle (manual)
- GET  /v1/harness/score                   — latest score snapshot per section
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from service.deps import (
    get_idem_store,
    get_pxt,
    require_idempotency_key,
    require_local_socket_or_token,
)
from service.routes._idempotent import with_idempotency

router = APIRouter(dependencies=[Depends(require_local_socket_or_token)])
log = logging.getLogger("vwbridge.harness")

# Pixeltable table paths
T_HEALTH_SNAPSHOTS = "lattice/harness/health_snapshots"
T_PROPOSALS        = "lattice/harness/harness_proposals"
T_EVENTS           = "lattice/harness/section_events"

VALID_SECTIONS = frozenset({
    "schema", "api", "frontend", "georef", "genai", "vw-itwin", "ddc", "global"
})


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class AggregateHealthResponse(BaseModel):
    aggregate_score: int
    sections: dict[str, int]
    snapshot_at: str | None


class SectionHealthResponse(BaseModel):
    section: str
    score: int
    breakdown: dict[str, Any]
    snapshot_at: str | None


class ProposalRequest(BaseModel):
    section: str = Field(..., min_length=1, max_length=64)
    proposed_diff: str = Field(..., min_length=1)
    proposed_by: str = Field(..., min_length=1, max_length=256)
    rationale: str | None = Field(default=None)


class ProposalResponse(BaseModel):
    proposal_id: str


class ProposalsListResponse(BaseModel):
    proposals: list[dict[str, Any]]
    count: int


class EventsListResponse(BaseModel):
    events: list[dict[str, Any]]
    count: int


class RatchetRequest(BaseModel):
    section: str = Field(..., min_length=1, max_length=64)


class RatchetResponse(BaseModel):
    cycle_id: str
    status: Literal["started"]


class ScoreSnapshotResponse(BaseModel):
    schema_: int = Field(alias="schema")
    api: int
    frontend: int
    georef: int
    genai: int
    vw_itwin: int = Field(alias="vw-itwin")
    ddc: int
    global_: int = Field(alias="global")

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_collect(pxt, table_name: str):
    """Get table and collect rows; returns empty list on missing table."""
    try:
        t = pxt.get_table(table_name)
        return list(t.collect()), t
    except Exception as exc:
        log.warning("table %r not accessible: %s", table_name, exc)
        return [], None


def _row_to_dict(row: Any) -> dict[str, Any]:
    try:
        return dict(row)
    except Exception:
        return {}


def _iso(val: Any) -> str | None:
    if val is None:
        return None
    if isinstance(val, datetime):
        return val.isoformat()
    return str(val)


def _latest_snapshot_per_section(pxt) -> dict[str, dict[str, Any]]:
    """Return the most-recent health_snapshots row for each section."""
    rows, _ = _safe_collect(pxt, T_HEALTH_SNAPSHOTS)
    latest: dict[str, dict[str, Any]] = {}
    for row in rows:
        d = _row_to_dict(row)
        section = d.get("section") or ""
        ts = d.get("snapshot_at") or d.get("created_at")
        prev = latest.get(section)
        if prev is None:
            latest[section] = d
        else:
            prev_ts = prev.get("snapshot_at") or prev.get("created_at")
            if (ts or "") > (prev_ts or ""):
                latest[section] = d
    return latest


# ---------------------------------------------------------------------------
# GET /health  — aggregate
# ---------------------------------------------------------------------------

@router.get("/health", response_model=AggregateHealthResponse)
def get_health_aggregate(pxt=Depends(get_pxt)):
    """Return global aggregate health: average score + per-section scores."""
    latest = _latest_snapshot_per_section(pxt)
    sections: dict[str, int] = {}
    latest_ts: str | None = None
    for section, d in latest.items():
        sections[section] = int(d.get("score") or 0)
        ts = _iso(d.get("snapshot_at") or d.get("created_at"))
        if ts and (latest_ts is None or ts > latest_ts):
            latest_ts = ts

    aggregate = int(sum(sections.values()) / len(sections)) if sections else 0
    return AggregateHealthResponse(
        aggregate_score=aggregate,
        sections=sections,
        snapshot_at=latest_ts,
    )


# ---------------------------------------------------------------------------
# GET /health/{section}  — per-section
# ---------------------------------------------------------------------------

@router.get("/health/{section}", response_model=SectionHealthResponse)
def get_health_section(section: str, pxt=Depends(get_pxt)):
    """Return health detail for a specific section."""
    if section not in VALID_SECTIONS:
        raise HTTPException(
            status_code=422,
            detail=f"Unknown section {section!r}. Valid: {sorted(VALID_SECTIONS)}",
        )
    latest = _latest_snapshot_per_section(pxt)
    d = latest.get(section)
    if d is None:
        raise HTTPException(
            status_code=404,
            detail=f"No health snapshot found for section {section!r}",
        )
    breakdown = d.get("breakdown") or {}
    if not isinstance(breakdown, dict):
        breakdown = {}
    return SectionHealthResponse(
        section=section,
        score=int(d.get("score") or 0),
        breakdown=breakdown,
        snapshot_at=_iso(d.get("snapshot_at") or d.get("created_at")),
    )


# ---------------------------------------------------------------------------
# POST /proposals  — submit a proposal
# ---------------------------------------------------------------------------

@router.post("/proposals", response_model=ProposalResponse)
def post_proposal(
    body: ProposalRequest,
    pxt=Depends(get_pxt),
    store=Depends(get_idem_store),
    idem_key: str = Depends(require_idempotency_key),
):
    """Insert a harness proposal row with outcome='pending'."""
    proposal_id = str(uuid.uuid4())

    def do() -> dict[str, Any]:
        try:
            t = pxt.get_table(T_PROPOSALS)
            t.insert([{
                "proposal_id":   proposal_id,
                "section":       body.section,
                "proposed_diff": body.proposed_diff,
                "proposed_by":   body.proposed_by,
                "rationale":     body.rationale or "",
                "outcome":       "pending",
                "created_at":    datetime.now(tz=timezone.utc),
            }])
            log.info(
                "inserted proposal %s for section=%s by=%s",
                proposal_id, body.section, body.proposed_by,
            )
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"insert failed: {exc!s}")
        return {"proposal_id": proposal_id}

    return with_idempotency(store, idem_key, do)


# ---------------------------------------------------------------------------
# GET /proposals  — list proposals
# ---------------------------------------------------------------------------

@router.get("/proposals", response_model=ProposalsListResponse)
def list_proposals(
    pxt=Depends(get_pxt),
    section: str | None = Query(default=None, max_length=64),
    outcome: str | None = Query(default=None, max_length=64),
    limit: int = Query(default=50, ge=1, le=500),
):
    """List harness proposals, optionally filtered by section and/or outcome."""
    rows, t = _safe_collect(pxt, T_PROPOSALS)
    results: list[dict[str, Any]] = []
    for row in rows:
        d = _row_to_dict(row)
        if section and d.get("section") != section:
            continue
        if outcome and d.get("outcome") != outcome:
            continue
        d["created_at"] = _iso(d.get("created_at"))
        results.append(d)
    # Sort by created_at descending (most-recent first)
    results.sort(key=lambda x: x.get("created_at") or "", reverse=True)
    return ProposalsListResponse(proposals=results[:limit], count=len(results))


# ---------------------------------------------------------------------------
# GET /events  — section events log
# ---------------------------------------------------------------------------

@router.get("/events", response_model=EventsListResponse)
def list_events(
    pxt=Depends(get_pxt),
    section: str | None = Query(default=None, max_length=64),
    event_type: str | None = Query(default=None, max_length=64),
    limit: int = Query(default=100, ge=1, le=1000),
):
    """List section_events, optionally filtered by section and/or event_type."""
    rows, _ = _safe_collect(pxt, T_EVENTS)
    results: list[dict[str, Any]] = []
    for row in rows:
        d = _row_to_dict(row)
        if section and d.get("section") != section:
            continue
        if event_type and d.get("event_type") != event_type:
            continue
        d["occurred_at"] = _iso(d.get("occurred_at") or d.get("created_at"))
        results.append(d)
    results.sort(key=lambda x: x.get("occurred_at") or "", reverse=True)
    return EventsListResponse(events=results[:limit], count=len(results))


# ---------------------------------------------------------------------------
# POST /ratchet  — trigger ratchet cycle
# ---------------------------------------------------------------------------

@router.post("/ratchet", response_model=RatchetResponse)
async def post_ratchet(
    body: RatchetRequest,
    pxt=Depends(get_pxt),
    store=Depends(get_idem_store),
    idem_key: str = Depends(require_idempotency_key),
):
    """Spawn run-autoresearch.sh <section> as a subprocess (timeout 180s).

    Logs a `cycle.started` event to lattice/harness/section_events and returns
    immediately. The subprocess runs detached; completion is tracked separately.
    """
    cycle_id = str(uuid.uuid4())

    def _log_event():
        try:
            t = pxt.get_table(T_EVENTS)
            t.insert([{
                "event_id":   cycle_id,
                "section":    body.section,
                "event_type": "cycle.started",
                "payload":    {"cycle_id": cycle_id, "section": body.section},
                "occurred_at": datetime.now(tz=timezone.utc),
            }])
        except Exception as exc:
            log.warning("could not log cycle.started event: %s", exc)

    async def _run():
        script = "meta/harness/bootstrap/run-autoresearch.sh"
        cmd = ["/usr/bin/env", "bash", script, body.section]
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            log.info(
                "ratchet cycle_id=%s section=%s pid=%s started",
                cycle_id, body.section, proc.pid,
            )
            await asyncio.wait_for(proc.communicate(), timeout=180.0)
        except asyncio.TimeoutError:
            log.warning("ratchet cycle_id=%s timed out after 180s", cycle_id)
        except Exception as exc:
            log.warning("ratchet cycle_id=%s error: %s", cycle_id, exc)

    def do() -> dict[str, Any]:
        _log_event()
        asyncio.ensure_future(_run())
        return {"cycle_id": cycle_id, "status": "started"}

    return with_idempotency(store, idem_key, do)


# ---------------------------------------------------------------------------
# GET /score  — latest score snapshot for all sections
# ---------------------------------------------------------------------------

@router.get("/score")
def get_score(pxt=Depends(get_pxt)):
    """Return the latest score for every known section.

    Missing sections default to 0.
    """
    latest = _latest_snapshot_per_section(pxt)
    return {
        section: int(latest[section].get("score") or 0) if section in latest else 0
        for section in VALID_SECTIONS
    }
