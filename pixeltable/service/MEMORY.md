# API Service Harness — Session Memory

## Open Decisions

1. **Worker subprocess model**: currently `claude -p` spawned per-run. Should we pool a persistent subprocess or async task pool? Trade-off: pooling saves startup cost but complicates state isolation. Deferred to Phase 2 profiling.
2. **IPC transport**: Unix socket vs FastAPI + bearer token. Socket is faster + simpler for local dev; bearer token enables remote sidecar (e.g., containerized). Current: socket only, bearer planned for Phase 3 multi-host.
3. **Idempotency key scope**: currently 24h cache per key. Should replay logic be scoped to project or global? Current: global. Will refine once multi-project concurrency loads arrive.

## Failed Experiments

- (placeholder — no failed experiments logged yet for this section)

## Session Handoff Notes

**Current state (2026-05-13)**: Sidecar running, 33 endpoints live, worker loop functional. Recent commits stabilized IPC contract validation; no regressions in endpoint test suite. Next phase: profile worker CPU under sustained 10+ concurrent runs, benchmark stream-event latency via SSE fan-out.

**Known issues**: 
- Stub-501 endpoints (`/v1/georef/ingest/*`, `/v1/reality/drone/*`) return placeholder JSON; stubs will convert to 200-OK as implementations land in `georef/` and `genai/` sections.
- Worker crash recovery untested — need to add kill + auto-restart logic to sidecar health monitor.

**Ready for next agent**: Endpoint surface frozen. Worker loop ready for load testing. Contract validation model ready for lint refinement.
