# API Service Harness — LATTICE Meta-Harness Control

Owns FastAPI sidecar surface: 33 endpoints across 10 routers, worker loop execution, IPC over `/tmp/vwbridge-pxt.sock`, request/response contract validation.

## Fitness Function

Score API health against **live endpoint count** and **contract integrity**:

1. **Endpoint inventory**: `git grep -c "^@app\|^@router" -- pixeltable/service/routes/*.py` equals 33
2. **Router structure**: all routers registered in `pixeltable/service/main.py`, all routes return JSON (no HTML/binary redirect)
3. **Worker loop**: `pixeltable/service/worker.py` claims runs, spawns `claude -p --output-format stream-json`, emits no crashes for 100 consecutive events
4. **IPC contract**: Unix socket `/tmp/vwbridge-pxt.sock` resolves to running sidecar, all inbound payloads validate against `pydantic` model in `pixeltable/service/models.py`
5. **No Anthropic SDK in TypeScript**: `git grep "import.*Anthropic" -- src/**.ts* | grep -v "^\s*//"`  returns empty
6. **Endpoint reference sync**: count in `meta/API.md` table matches live code count

**Baseline score**: `scripts/score-api.sh` runs in < 5s, outputs JSON with `endpoints_live`, `contracts_valid`, `worker_health`, `ipc_status`.

## Improvement Loop

Autoresearch loop (on every commit to `pixeltable/service/`):

1. Run `scripts/score-api.sh` → baseline snapshot
2. Auto-read `meta/API.md` endpoint count, cross-check against `git ls-files pixeltable/service/routes/`.
3. Spawn `claude -p` subprocess to lint endpoint definitions and suggest contract harmonization PRs
4. Write reasoning + recommendation to `runtime-runs/<run-id>/api-lint.md`
5. If `score_after > score_before`, commit to feature branch; else rollback + log failure reason
6. Flock concurrency: max 1 lint job at a time per sidecar instance (held via `/tmp/vwbridge-lint.lock`)

## Action Catalog

- **Health check**: `curl -s http://localhost:8001/healthz | jq .` → immediate `{"status":"ok","timestamp":"..."}` or fail
- **Endpoint audit**: `git grep -h "^@\(app\|router\)\." -- pixeltable/service/ | wc -l` should equal 33
- **Worker inspect**: check `lattice/execution/agent_runs` table for `status='running'` rows; if > 1 without recent timestamp, worker stalled
- **IPC health**: `test -S /tmp/vwbridge-pxt.sock && echo connected || echo failed`
- **Contract lint**: `pixeltable/service/validate_contracts.py --check` (TBD, stub in worker loop for now)

## Operating Mode

- **Sidecar lifecycle**: started via `cd pixeltable/service && PIXELTABLE_HOME=/Volumes/PixelTable/.pixeltable PYTHONPATH=/Volumes/PixelTable/schemas uv run python main.py`
- **Dev port**: TCP `8001` (Vite proxy in `vite.config.ts` routes `/api/` to sidecar)
- **Production**: Unix socket at `/tmp/vwbridge-pxt.sock` only (no TCP exposure)
- **Worker cadence**: poll `agent_runs` every 100ms, claim + execute, emit stream deltas to SSE fan-out + Pixeltable write
- **Failure mode**: stalled worker → ops alert via `lattice/execution/health` drift check; restart sidecar + replay queued runs from idempotency cache
