# Handoff: Bonsai 4B Real Use-Case Validation (2026-05-17)

## Objective

Validate that local PrismML Bonsai 4B is useful for **actual VW_iTwin_Bridge workflows** (not synthetic benchmark-only), then preserve full session context for a follow-on agent.

## What Was Completed

### 0) Added Juniper Avenue use-case dropdown + execution flow in UI

New implementation adds practical scenarios to the Benchmarks page and executes a real
CWICR + Bonsai workflow end-to-end.

Changes:

- `src/server/harness/run-bonsai-use-case.ts` (new)
  - Declares scenario catalog (`bonsaiUseCaseScenarios`) including:
    - Juniper Ave creeping thyme estimate
    - Juniper Ave reinforced slab estimate
    - Juniper Ave drainage estimate
  - Runs sidecar `POST /v1/erp/cost-search`
  - Runs local Bonsai 4B (`meta/harness/bin/llm`)
  - Returns confidence signal + estimate + operator note.
- `src/routes/harness/benchmarks.tsx`
  - Adds **Use case** dropdown
  - Adds **Run Bonsai Use Case** button
  - Renders returned operator note inline.
- `src/runtime/pixeltable/sidecar-client.ts`
  - Adds `runErpCostSearch()` convenience method.

Outcome: operators can run scenario-driven, domain-relevant checks directly from UI.

---

### 1) Removed mock fallback behavior from runtime path

Previously completed in this session chain:

- `pixeltable/service/worker.py`
  - Removed mock backend fallback path for missing CLI execution.
- `pixeltable/service/routes/runtime.py`
  - Added filtering support so mock runs are not shown by default.
- `src/server/runtime/list-runs.ts`
  - Explicitly requests non-mock runs.

Outcome: runtime no longer silently falls back to fake run content.

---

### 2) Benchmarks UI now loads real local benchmark artifacts

Added server + UI wiring so the Benchmarks tab uses real files under:

- `meta/harness/benchy/server/reports/*.json`

Changes:

- `pixeltable/service/routes/harness.py`
  - Added `GET /v1/harness/benchmarks/reports?limit=...`
  - Normalizes legacy/raw Benchy report JSON into console-compatible shape.
- `src/runtime/pixeltable/sidecar-client.ts`
  - Added `listHarnessBenchmarkReports(limit)`.
- `src/server/harness/list-benchmark-reports.ts`
  - Added server function wrapper for route consumption.
- `src/routes/harness/benchmarks.tsx`
  - Auto-loads latest report from sidecar.
  - Adds report selector dropdown for switching between local artifacts.

Outcome: Benchmarks tab reflects real local runs by default.

---

### 3) Added one-click Bonsai 4B smoke test

Changes:

- `pixeltable/service/routes/harness.py`
  - Added `POST /v1/harness/models/smoke`
  - Runs `python3 meta/harness/bin/llm --backend=mlx-lm:prism-ml/Ternary-Bonsai-4B-mlx-2bit ...`
  - Returns pass/fail, latency, stdout/stderr, and command.
- `src/runtime/pixeltable/sidecar-client.ts`
  - Added `runHarnessModelSmokeTest(payload)`.
- `src/server/harness/run-bonsai-smoke-test.ts`
  - Added server function for UI action.
- `src/routes/harness/benchmarks.tsx`
  - Added `Smoke Bonsai 4B` button.

Validation already run:

- Endpoint call returned `ok: true`, marker `BONSAI_4B_OK`, ~2.6s latency.

---

### 4) Ran a real domain use-case with Bonsai 4B

Use-case executed:

1. Queried real sidecar CWICR endpoint:
   - `POST /v1/erp/cost-search`
   - Description: `reinforced concrete slab on grade with vapor barrier`
   - Region: `US`, Top: `3`
2. Passed actual JSON result into Bonsai 4B prompt.
3. Asked model for operator note with:
   - best match
   - 1200 m2 budget estimate
   - confidence/risk note
   - next BOQ check

Result quality:

- Bonsai correctly selected reinforced slab row (highest score).
- Correct arithmetic: `1200 * 145 = 174000 USD`.
- Produced useful risk and next-check recommendations.

This confirms Bonsai 4B can produce practical workflow guidance on project data, not just benchmark responses.

## Service/Runtime State at Handoff

At end of work:

- Frontend dev server expected on `http://localhost:3000`
- Sidecar expected on `http://127.0.0.1:7770`

Primary UI:

- `http://localhost:3000/harness/benchmarks`

## Reproduction Commands

Run from repo root (`/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge`):

```bash
cd /Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge
```

Start sidecar:

```bash
cd /Volumes/PixelTable/VW_iTwin_Bridge
make -C "VW_iTwin_Bridge/pixeltable" sidecar-up-tcp
```

Start UI:

```bash
cd /Volumes/PixelTable/VW_iTwin_Bridge
cd "VW_iTwin_Bridge" && bun run dev
```

Smoke endpoint:

```bash
curl -sS -X POST "http://127.0.0.1:7770/v1/harness/models/smoke" \
  -H "Content-Type: application/json" \
  -d '{"model":"prism-ml/Ternary-Bonsai-4B-mlx-2bit","timeout_seconds":90}'
```

Real CWICR query:

```bash
curl -sS -X POST "http://127.0.0.1:7770/v1/erp/cost-search" \
  -H "Content-Type: application/json" \
  -d '{"description":"reinforced concrete slab on grade with vapor barrier","region":"US","top":3}'
```

Direct Bonsai 4B CLI call:

```bash
python3 meta/harness/bin/llm \
  --backend=mlx-lm:prism-ml/Ternary-Bonsai-4B-mlx-2bit \
  --timeout=120 \
  "Reply with exactly: BONSAI_4B_OK"
```

## Suggested Next Steps for Next Agent

1. Add a second smoke action for `bonsai-1.7b` to compare speed/quality in the same UI.
2. Add a "Use-case runner" panel under Benchmarks:
   - run `/v1/erp/cost-search`
   - feed result into Bonsai template
   - store generated operator note as artifact in `meta/harness/docs/sessions/`.
3. Persist Bonsai use-case outputs into runtime evidence tables for replayability.
4. Add a lightweight quality gate:
   - assert budget arithmetic correctness
   - assert top result score above threshold (e.g., >0.5) before BOQ recommendation.

## Key Files Touched This Cycle

- `pixeltable/service/routes/harness.py`
- `src/runtime/pixeltable/sidecar-client.ts`
- `src/server/harness/list-benchmark-reports.ts`
- `src/server/harness/run-bonsai-smoke-test.ts`
- `src/routes/harness/benchmarks.tsx`
- `meta/harness/HANDOFF-2026-05-17-bonsai-usecase.md` (this file)

