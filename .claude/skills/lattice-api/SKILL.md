---
description: Author and maintain FastAPI endpoints in the LATTICE sidecar, enforce the 33-endpoint contract, validate router registration and JSON responses, and sync meta/API.md.
---

# LATTICE FastAPI Endpoint Authoring

The API section owns the FastAPI sidecar at `pixeltable/service/`, which exposes 33
endpoints across 10 routers over TCP port 8001 (dev) and Unix socket
`/tmp/vwbridge-pxt.sock` (production). Every new route must be reflected in
`meta/API.md` and `meta/ARCHITECTURE.md` in the same commit. The scoring script
`scripts/score-api.sh` checks live endpoint counts, worker health, and contract sync.

## When this skill applies

- Adding a new FastAPI route to any router under `pixeltable/service/routes/`
- Registering a new router in `pixeltable/service/main.py`
- Fixing endpoint count drift between code and `meta/API.md`
- Validating worker loop health (`pixeltable/service/worker.py`)
- Running the api section cycle: `bash meta/harness/bootstrap/run-autoresearch.sh api`
- Sidecar returns non-JSON or endpoint count is not 33

## How it works

1. Check sidecar health:
   ```bash
   curl -s http://localhost:8001/healthz | jq .
   ```
   Expected: `{"status":"ok","timestamp":"..."}`. If down, restart:
   ```bash
   cd pixeltable/service
   PIXELTABLE_HOME=/Volumes/PixelTable/.pixeltable \
   PYTHONPATH=/Volumes/PixelTable/schemas \
   uv run python main.py
   ```

2. Audit live endpoint count:
   ```bash
   git grep -h "^@\(app\|router\)\." -- pixeltable/service/ | wc -l
   ```
   Must equal the declared count in `meta/API.md`.

3. Add a new route in `pixeltable/service/routes/<section>.py`:
   ```python
   @router.get("/v1/<section>/<resource>", response_model=MySchema)
   async def get_resource(project_id: str) -> MySchema:
       ...
   ```
   Router must already be imported and included in `main.py` via
   `app.include_router(router, prefix="/v1")`.

4. Validate that every route returns JSON (no HTML, no binary redirect):
   ```bash
   git grep -h "return HTMLResponse\|return FileResponse\|redirect" -- pixeltable/service/routes/
   ```
   Must return empty.

5. Update `meta/API.md` endpoint table and increment total count.
   Update `meta/ARCHITECTURE.md` FastAPI surface table and endpoint count.
   Both files must change in the same commit as the route file.

6. Check IPC socket:
   ```bash
   test -S /tmp/vwbridge-pxt.sock && echo connected || echo failed
   ```

7. Confirm no Anthropic SDK in TypeScript client:
   ```bash
   git grep "import.*Anthropic" -- "src/**/*.ts" "src/**/*.tsx" | grep -v "^\s*//"
   ```
   Must return empty.

8. Run docs-sync check before commit:
   ```bash
   bash scripts/pre-commit-docs-check.sh
   ```

## Files used

- `pixeltable/service/routes/*.py` — route definitions (one file per section)
- `pixeltable/service/main.py` — router registration and app startup
- `pixeltable/service/worker.py` — background worker loop for agent runs
- `pixeltable/service/models.py` — Pydantic request/response models
- `pixeltable/service/GOAL.md` — API section fitness function
- `meta/API.md` — canonical endpoint table (must sync with code)
- `meta/ARCHITECTURE.md` — FastAPI surface overview + endpoint count
- `scripts/score-api.sh` — section scoring script
- `scripts/pre-commit-docs-check.sh` — docs-drift validator
- `lattice/execution/agent_runs` — Pixeltable table tracking worker run state

## Constraints

- All routes must return JSON. No HTML responses from sidecar routes.
- Never import Anthropic SDK in TypeScript client files (`src/`).
- The endpoint count in `meta/API.md` must match the live code count exactly;
  the docs-sync-check CI workflow enforces this and will block merges on drift.
- IPC is Unix socket in production — never expose the sidecar on a public port.
- Worker loop must poll `agent_runs` at 100 ms cadence; no blocking Pixeltable calls
  on the FastAPI event loop (offload to thread pool or async Pixeltable API).
- Pydantic models live in `models.py`; raw dict responses are not acceptable for
  contracted endpoints.
- Use `uv` for all Python dependency management inside `pixeltable/service/`.
