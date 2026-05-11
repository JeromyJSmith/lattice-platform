"""Background dispatcher for pending runs.

A single asyncio task polls `lattice/execution/agent_runs` for rows with
`status == "pending"`, claims each by transitioning to `running`, then
streams an agent response into `lattice/execution/agent_stream_events`
before writing the terminal `run.completed` event.

Two backends:
  - Real Claude via the local `claude -p` CLI subprocess (uses your
    existing Claude Max auth — no API key needed). Stdout is read line
    by line; each non-empty line becomes one `stream.delta` row.
  - Deterministic mock (4 chunks, 600ms apart) when `claude` is not on
    PATH — so the worker never crashes on hosts without the CLI.

The Pixeltable write path is identical for both. Same table, same seq
ordering, same `run.completed` transition. The only thing that changes
is where the chunks come from and what `agent_kind` gets recorded.
"""

from __future__ import annotations

import asyncio
import json
import logging
import shutil
import uuid
from datetime import datetime, timezone
from typing import Any, AsyncIterator

from service.upsert import upsert_runtime_event

log = logging.getLogger("vwbridge.worker")

POLL_INTERVAL_S = 1.0
MOCK_DELTA_GAP_S = 0.6

# ---- in-process pub/sub for SSE -------------------------------------------
# One asyncio.Queue per active SSE subscriber, keyed by run_id. The worker
# publishes each `stream.delta` to every subscriber for that run; the SSE
# endpoint pops events off its queue and writes them to the response stream.
# Subscribers also receive a synthetic `{"type": "run.completed"}` sentinel
# on the queue when the run terminates so the SSE handler can close cleanly.
_subscribers: dict[str, set[asyncio.Queue]] = {}


def subscribe(run_id: str) -> asyncio.Queue:
    q: asyncio.Queue = asyncio.Queue()
    _subscribers.setdefault(run_id, set()).add(q)
    return q


def unsubscribe(run_id: str, q: asyncio.Queue) -> None:
    bucket = _subscribers.get(run_id)
    if bucket is None:
        return
    bucket.discard(q)
    if not bucket:
        _subscribers.pop(run_id, None)


def _publish(run_id: str, event: dict[str, Any]) -> None:
    for q in list(_subscribers.get(run_id, ())):
        try:
            q.put_nowait(event)
        except asyncio.QueueFull:
            # Subscriber is slow — drop is preferable to backpressuring the worker.
            pass

CLAUDE_CLI: str | None = shutil.which("claude")
SYSTEM_PROMPT = (
    "You are LATTICE, an AI agent for landscape architecture and AEC "
    "digital twin workflows. Be concise and direct."
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _backend_label() -> str:
    return "claude-cli" if CLAUDE_CLI else "mock"


async def _mock_chunks(task: str) -> AsyncIterator[str]:
    """Fallback streamer — deterministic 4 chunks with visible gaps."""
    for chunk in (
        f"Mock agent received task: {task!r}.",
        "Thinking…",
        "Sketching a plan: parse → reason → respond.",
        f"Done. (mock) Task '{task}' has no real side-effects.",
    ):
        await asyncio.sleep(MOCK_DELTA_GAP_S)
        yield chunk


async def _claude_cli_chunks(task: str) -> AsyncIterator[str]:
    """Stream text deltas from `claude -p` using JSON event mode.

    The Claude Code CLI wraps Anthropic stream events in `stream_event`
    envelopes:

        {"type":"stream_event","event":{"type":"content_block_delta",
         "delta":{"type":"text_delta","text":"..."}}}

    Everything else (rate_limit_event, system/init, message_start,
    content_block_start/stop, message_stop, result) is metadata —
    we drop it.
    """
    assert CLAUDE_CLI is not None
    cmd = [
        CLAUDE_CLI, "-p",
        "--output-format", "stream-json",
        "--verbose",                      # required by stream-json
        "--include-partial-messages",     # the actual token-streaming switch
        "--system-prompt", SYSTEM_PROMPT,
        task,
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    assert proc.stdout is not None
    try:
        async for raw in proc.stdout:
            line = raw.decode("utf-8", errors="replace").strip()
            if not line:
                continue
            try:
                evt = json.loads(line)
            except json.JSONDecodeError:
                continue
            if evt.get("type") != "stream_event":
                continue
            inner = evt.get("event") or {}
            if inner.get("type") != "content_block_delta":
                continue
            delta = inner.get("delta") or {}
            if delta.get("type") != "text_delta":
                continue
            text = delta.get("text") or ""
            if text:
                yield text
    finally:
        rc = await proc.wait()
        if rc != 0:
            err_bytes = await proc.stderr.read() if proc.stderr else b""
            err = err_bytes.decode("utf-8", errors="replace").strip()[:1000]
            raise RuntimeError(f"claude CLI exited {rc}: {err or '(no stderr)'}")


async def _emit_delta(pxt, *, run_id: str, thread_id: str, seq: int, text: str) -> None:
    """Write one stream.delta row. Wrapped in to_thread so we don't block
    the asyncio loop on Pixeltable's sync upsert path."""
    event_id = str(uuid.uuid4())
    created_at = _now_iso()
    event = {
        "kind": "stream.delta",
        "payload": {
            "run_id":     run_id,
            "thread_id":  thread_id,
            "event_id":   event_id,
            "seq":        seq,
            "delta_text": text,
            "created_at": created_at,
        },
    }
    await asyncio.to_thread(upsert_runtime_event, pxt, event)
    _publish(run_id, {
        "type":       "stream.delta",
        "event_id":   event_id,
        "event_kind": "stream.delta",
        "seq":        seq,
        "delta_text": text,
        "tool_name":  "",
        "created_at": created_at,
    })


async def _write_completed(pxt, *, run_id: str, thread_id: str, task: str,
                           agent_kind: str, started_at: str,
                           status: str = "completed") -> None:
    event = {
        "kind": "run.completed",
        "payload": {
            "run_id":     run_id,
            "thread_id":  thread_id,
            "agent_kind": agent_kind,
            "task":       task,
            "status":     status,
            "started_at": started_at,
            "ended_at":   _now_iso(),
        },
    }
    await asyncio.to_thread(upsert_runtime_event, pxt, event)
    _publish(run_id, {"type": "run.completed", "status": status})


async def _stream_run(pxt, run_id: str, thread_id: str, task: str,
                      started_at: str, agent_kind: str) -> None:
    """Run a single dispatched run: emit stream.delta events, then run.completed."""
    use_real = agent_kind == "claude-cli" and CLAUDE_CLI is not None
    log.info("streaming run %s mode=%s task=%r", run_id, agent_kind, task)

    try:
        chunks = _claude_cli_chunks(task) if use_real else _mock_chunks(task)
        seq = 0
        async for text in chunks:
            seq += 1
            await _emit_delta(pxt, run_id=run_id, thread_id=thread_id, seq=seq, text=text)

        await _write_completed(
            pxt, run_id=run_id, thread_id=thread_id, task=task,
            agent_kind=agent_kind, started_at=started_at, status="completed",
        )
        log.info("run %s completed (mode=%s, deltas=%d)", run_id, agent_kind, seq)
    except Exception as exc:  # noqa: BLE001
        log.exception("run %s failed", run_id)
        try:
            # Surface the error as one final delta so the operator console
            # shows *why* the run failed before flipping the row to failed.
            await _emit_delta(
                pxt, run_id=run_id, thread_id=thread_id, seq=9999,
                text=f"[error] {type(exc).__name__}: {exc}",
            )
            await _write_completed(
                pxt, run_id=run_id, thread_id=thread_id, task=task,
                agent_kind=agent_kind, started_at=started_at, status="failed",
            )
        except Exception:  # noqa: BLE001
            log.exception("could not record failure for %s", run_id)


def _claim_pending(pxt) -> list[dict[str, Any]]:
    """Return pending rows and transition them to `running`.

    The pending → running transition stamps `agent_kind` based on whether
    the `claude` CLI is on PATH at claim time. That field persists
    through to the terminal `run.completed` event.
    """
    agent_kind = _backend_label()

    t = pxt.get_table("lattice/execution/agent_runs")
    df = t.where(t.status == "pending").select(
        t.run_id, t.thread_id, t.started_at, t.raw_event,
    ).collect()

    claimed: list[dict[str, Any]] = []
    for r in df:
        run_id = r.get("run_id") or ""
        if not run_id:
            continue
        raw = r.get("raw_event") or {}
        payload = raw.get("payload") if isinstance(raw, dict) else {}
        task = (payload or {}).get("task", "") if isinstance(payload, dict) else ""
        thread_id = r.get("thread_id") or "thread-local"
        started = r.get("started_at")
        started_iso = started.isoformat() if started is not None else _now_iso()

        upsert_runtime_event(pxt, {
            "kind": "run.started",
            "payload": {
                "run_id":     run_id,
                "thread_id":  thread_id,
                "agent_kind": agent_kind,
                "status":     "running",
                "task":       task,
                "started_at": started_iso,
            },
        })
        claimed.append({
            "run_id": run_id, "thread_id": thread_id,
            "task": task, "started_at": started_iso, "agent_kind": agent_kind,
        })
    return claimed


async def worker_loop(pxt, stop_event: asyncio.Event) -> None:
    log.info("worker_loop started (poll=%.1fs, backend=%s, claude_cli=%s)",
             POLL_INTERVAL_S, _backend_label(), CLAUDE_CLI or "(not found on PATH)")
    while not stop_event.is_set():
        try:
            for claim in _claim_pending(pxt):
                asyncio.create_task(_stream_run(
                    pxt,
                    run_id=claim["run_id"],
                    thread_id=claim["thread_id"],
                    task=claim["task"],
                    started_at=claim["started_at"],
                    agent_kind=claim["agent_kind"],
                ))
        except Exception:  # noqa: BLE001
            log.exception("worker poll failed")
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=POLL_INTERVAL_S)
        except asyncio.TimeoutError:
            pass
    log.info("worker_loop stopped")
