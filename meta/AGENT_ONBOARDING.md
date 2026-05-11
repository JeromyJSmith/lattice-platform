# Agent Onboarding (5-minute read)

You're an AI agent picking up work in LATTICE. Read this top to bottom — then you can pick an issue and start.

## 1. What LATTICE is

A local-first AEC digital-twin platform: Vectorworks → IFC → Pixeltable → operator console (TanStack Start) → two render contexts (ThatOpen 3D + deck.gl analytical) → Cinema 4D handoff. Real agents (Claude via CLI subprocess) write back into Pixeltable as runs stream.

## 2. Boot the stack (do this before any task)

```bash
# Terminal 1 — sidecar (FastAPI + Pixeltable + worker)
cd pixeltable
make sidecar-up-tcp   # binds 127.0.0.1:7770

# Terminal 2 — frontend
bun run dev           # http://localhost:3000

# Verify
curl 127.0.0.1:7770/healthz
curl http://localhost:3000/runtime  # should be HTTP 200
```

If `make sidecar-up-tcp` fails on `PIXELTABLE_HOME not set`, prepend:
```bash
PIXELTABLE_HOME=/Volumes/PixelTable/.pixeltable make sidecar-up-tcp
```

## 3. What's in Pixeltable right now

```
lattice/execution/          ← runtime ledger (owned by this body)
  agent_threads / messages / runs / stream_events / artifacts / outcomes

lattice/bridge/             ← cross-system bridges (owned by this body)
  vw/        vectorworks_exports
  ifc/       ifc_elements (20 cols), ifc_property_sets
  itwin/     itwin_sync_jobs, itwin_changed_elements, connector_versions
  marpa/     marpa_parse_runs
  semantic/  semantic_sidecars, landscape_entities  (with pgvector indices)
  evidence/  promotion_events, harness_run_refs
  health/    schema_drift_events, bridge_gap_matrix

marpa/                      ← OWNED BY MARPA_PLATFORM (read-only here)
lattice/source, lattice/qa, lattice/budget, lattice/worksheet
                            ← other bodies (DO NOT WRITE)
```

Migrations are in `pixeltable/migrations/0001`–`0011`. The ownership guard in `migrations/_helpers.py::assert_ownership` blocks any accidental writes outside the owned tree.

## 4. The MCP / sidecar endpoints you can call

All on `http://127.0.0.1:7770`:

| Endpoint                              | What it does                                                                  |
|---------------------------------------|-------------------------------------------------------------------------------|
| `GET  /healthz`                       | Liveness check                                                                |
| `GET  /v1/runtime/runs`               | List agent_runs rows (newest first, capped at 100)                           |
| `GET  /v1/runtime/stream-events`     | Poll stream events for a run (paginated, `after_seq`)                         |
| `GET  /v1/runtime/stream-events/sse` | EventSource push of stream events for a run                                   |
| `POST /v1/runtime/events`             | Bulk ingest TS `RuntimeEvent`s (requires `Idempotency-Key` header)            |
| `POST /v1/vw/sidecars`                | Ingest a Vectorworks sidecar.json + IFC pointer                               |
| `GET  /v1/itwin/*`                    | iTwin/IMS adapter (Bentley OAuth, needs `BENTLEY_CLIENT_ID/SECRET`)           |
| `POST /v1/marpa/*`                    | MARPA parse run intake                                                        |
| `POST /v1/evidence/promotions`        | Record draw/validate/promote events                                            |
| `POST /v1/semantic/*`                 | Semantic sidecar + landscape entity intake                                    |

The TypeScript-side wrapper is at [`src/runtime/pixeltable/sidecar-client.ts`](../src/runtime/pixeltable/sidecar-client.ts) — auto idempotency-key, UDS/TCP modes. **Use it, don't roll your own fetch.**

## 5. How to pick up work

1. Find an issue labelled [`agent-ready`](https://github.com/JeromyJSmith/lattice-platform/issues?q=is%3Aopen+label%3Aagent-ready) (also filter by your area label — `data-layer`, `3d-viewer`, etc.).
2. Create a branch: `agent/<issue-number>-<short-slug>` off `main`.
3. Implement against the acceptance criteria in the issue body.
4. Tests: at minimum `make test-no-pxt`. If you touched `pixeltable/` also run `make test-pxt` locally.
5. Open a PR — `agent-pr-review.yml` will auto-comment with classification.

## 6. What's queued up

The full prioritised backlog is [`meta/FEATURE_BACKLOG.md`](FEATURE_BACKLOG.md). The current priority queue lives at the top of that file. Every unchecked item should have a corresponding GitHub issue with the same title.

## 7. If something is broken

| Symptom | First check |
|---|---|
| Sidecar won't start | `tail /tmp/vwbridge-sidecar.log` — usually `PIXELTABLE_HOME` not exported |
| `claude -p` not found | `which claude` — worker falls back to mock automatically, agent_kind=`mock` |
| HTTP 500 on `/runtime` | `tail /tmp/vwbridge-frontend.log` — most failures are stale module cache, restart bun dev |
| No deltas in EventTimeline | Open devtools Network → EventSource — should see `/v1/runtime/stream-events/sse` open |
| Pixeltable schema drift | `cd pixeltable && make verify` — exits non-zero if live vs snapshot diverge |

The session memory at `~/.claude/projects/-Volumes-PixelTable-VW-iTWIN-Bridge/memory/` has detailed pattern docs for: boot sequence, TanStack Start quirks, sidecar wiring, streaming pipeline, SSE stream events.

## 8. Cardinal rules (see CONTRIBUTING.md for the full list)

1. No `@itwin/core-backend` — Pixeltable owns persistence.
2. No Anthropic SDK in client code — server functions only.
3. uv only for Python — never pip / conda / poetry.
4. IFC4.3 at the boundary — no Revit, no DGN.
5. Pixeltable is the only database.
