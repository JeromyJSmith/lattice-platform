# Meta-Harness Next Session Handoff

Date: 2026-05-12
Branch: `feature/meta-harness`
Repo root: `/Volumes/PixelTable/VW_iTWIN_Bridge/VW_iTwin_Bridge`

## Start Here

Read these files in order:

1. `AGENTS.md`
2. `meta/harness/README.md`
3. `meta/harness/CURRENT-STATE.md`
4. `meta/harness/golden_path.md`
5. `meta/harness/TODO.md`
6. `meta/harness/docs/capability-lifecycle.md`
7. `meta/DDC_MAPPING.md`

The current goal is to turn the Meta-Harness capability matrix from a passive
inventory into an operator pre-flight surface:

```text
capability row
-> run contract
-> browser Run button
-> FastAPI sidecar execution
-> verifier
-> evidence artifact
-> row result
-> promotion/tracking
```

## Current Working State

The capability matrix works in the browser:

```text
http://127.0.0.1:3000/harness/capabilities
```

Current matrix summary:

| Status | Count | Meaning |
|---|---:|---|
| Proven | 1 | Has contract wires and proof evidence |
| Needs proof / deferred | 145 | Includes contract-only rows and deferred rows |
| Fail / blocked | 48 | Missing wires, blocked rows, or invalid rows |
| Total | 194 | Across 22 capability registries |

One capability is runnable today:

```text
single-file-agents / codebase-context-ripgrep
```

It can be run from the browser through:

```text
POST /v1/harness/capabilities/runs
```

Latest browser proof artifact:

```text
meta/harness/docs/sessions/2026-05-12T13-15-32-115Z-codebase-context-ripgrep-browser-run.json
```

Additional integrated run-contract artifact:

```text
meta/harness/docs/sessions/2026-05-12-integrated-run-contract-proof.json
```

## Servers

If the session starts cold, run:

```bash
cd /Volumes/PixelTable/VW_iTWIN_Bridge/VW_iTwin_Bridge/pixeltable
PIXELTABLE_HOME=/Volumes/PixelTable/.pixeltable uv run uvicorn service.main:app --host 127.0.0.1 --port 7770
```

In another terminal:

```bash
cd /Volumes/PixelTable/VW_iTWIN_Bridge/VW_iTwin_Bridge
bun run dev --host 127.0.0.1
```

Then open:

```text
http://127.0.0.1:3000/harness/capabilities
```

## What Just Landed

### Backend

File: `pixeltable/service/routes/harness.py`

- Added the generic allowlisted capability execution endpoint:

```text
POST /v1/harness/capabilities/runs
```

- Matrix rows now include:
  - `serves`
  - `run_action`
  - `run_contract`
  - status diagnostics
  - missing wire/proof details

- Execution remains allowlisted. There is no arbitrary shell or arbitrary
  Python execution endpoint.

### Frontend

File: `src/routes/harness/capabilities.tsx`

- Added responsive expandable capability rows.
- Added filters:
  - All
  - Proven
  - Needs Proof
  - Failing/Blocked
  - Deferred
  - Runnable
- Added search over id, name, description, surface, and tool.
- Runnable rows show an action button and inline result.
- Non-runnable rows explain that the run contract is missing.

File: `src/styles.css`

- Added `--warning` tokens for amber status in light and dark themes.

### Server Client

Files:

- `src/runtime/pixeltable/sidecar-client.ts`
- `src/runtime/pixeltable/sidecar-client.test.ts`
- `src/server/harness/run-codebase-context-proof.ts`
- `src/server/harness/list-capability-matrix.ts`

The TanStack server side now calls the generic capability run endpoint while
preserving the old benchmark page compatibility wrapper.

### Docs

Files:

- `meta/harness/golden_path.md`
- `meta/harness/TODO.md`
- `meta/harness/docs/capability-lifecycle.md`
- `meta/API.md`
- `meta/ARCHITECTURE.md`

The endpoint count is now 39 and `/v1/harness` has 6 endpoints.

## Verification Already Run

These passed after integration:

```bash
uv run python -m py_compile pixeltable/service/routes/harness.py
bunx biome check src/routes/harness/capabilities.tsx src/runtime/pixeltable/sidecar-client.ts src/runtime/pixeltable/sidecar-client.test.ts src/server/harness/run-codebase-context-proof.ts
bun test src/runtime/pixeltable/sidecar-client.test.ts
bun run build
bash scripts/pre-commit-docs-check.sh
bash scripts/lattice-verify.sh HEAD
git diff --check
```

Browser smoke test also passed:

1. Opened `/harness/capabilities`.
2. Selected `single-file-agents`.
3. Selected `Runnable`.
4. Expanded `codebase-context-ripgrep`.
5. Clicked `Run proof`.
6. Saw `Proof passed.` and a session artifact path.

## Hard Rules

Do not violate these in the next session:

- Do not edit landed migrations `0001` through `0016`.
- Do not touch secrets, `.env*`, OAuth credentials, or provider tokens.
- Do not change branch protection or merge to `main`.
- Do not delete migrations, branches, or issues.
- Do not make incidental doctrine changes.
- Do not expose arbitrary shell execution from the sidecar.
- Do not make DuckDB or SQLite durable storage. Pixeltable is the substrate;
  DuckDB WASM is browser analytics over exported Arrow/Parquet.

## Next Golden Path

Golden Path 002 is now defined:

```text
Capability Pre-Flight Run Contract
```

Definition of success:

1. A capability row declares a run contract.
2. The console shows it as runnable.
3. The operator can run it from the browser.
4. The sidecar executes only the allowlisted contract.
5. A verifier runs.
6. Evidence lands under `meta/harness/docs/sessions/`.
7. The row shows pass/fail inline.
8. The capability can be promoted from `contract-only` to `proven`.

## Immediate Task List

### P0 — Make More Capabilities Runnable

Add run contracts for the next 3 to 5 contract-only capabilities. Start with
capabilities that already have deterministic local checks.

Suggested candidates:

| Capability | Why |
|---|---|
| `python-docstring-rule` | Already backed by `scripts/check-python-docstrings.py` |
| `reports-as-evidence` | Can verify benchmark/session JSON shape |
| `benchmark-yaml-configs` | Can validate Benchy-compatible report/config shape |
| `executable-install-docs` | Can check install docs and scripts exist |
| `hook-json-logging` | Can validate expected event envelope once hook artifacts exist |

Acceptance:

- Each row has a `run_contract`.
- Each row appears under the `Runnable` filter.
- Browser `Run proof` produces an artifact.
- Verifier passes or fails with a clear message.
- Passing rows cite proof evidence before being treated as proven.

### P0 — Normalize Run Contract Shape

Move run contract declarations out of ad hoc Python constants once 3 or more
capabilities are runnable.

Recommended next shape:

```yaml
run_contract:
  kind: script
  command:
    - uv
    - run
    - python
    - scripts/check-python-docstrings.py
  timeout_seconds: 60
  evidence_output: meta/harness/docs/sessions/<timestamp>-python-docstrings.json
  verifier:
    kind: exit_code
    expected: 0
```

Keep the backend allowlist. The registry may declare intent, but the sidecar
must still resolve the id against trusted executable definitions.

### P0 — Keep Evidence File Shape Stable

Before writing Pixeltable migration `0017`, settle this JSON shape:

```json
{
  "capability_id": "...",
  "tool": "...",
  "run_id": "...",
  "started_at": "...",
  "completed_at": "...",
  "ok": true,
  "command": ["..."],
  "artifact": "...",
  "verification": {
    "status": "passed",
    "message": "...",
    "returncode": 0
  },
  "metrics": {
    "latency_ms": 0,
    "cost_usd": 0,
    "model": "deterministic"
  }
}
```

### P1 — Pixeltable Migration 0017

Only after the evidence shape survives the browser loop, add migration `0017`.
Do not edit `0001` through `0016`.

Likely tables:

- `lattice/harness/capabilities`
- `lattice/harness/run_contracts`
- `lattice/harness/proof_runs`
- `lattice/harness/evidence_artifacts`
- `lattice/harness/model_benchmarks`
- `lattice/harness/section_events`

### P1 — Browser Console Improvements

- Add a global summary filter across all registries, not just the active tab.
- Add a saved “next runnable queue.”
- Add an “open contract file” affordance for paths.
- Add a result history panel per capability.
- Add a “promote to proven” affordance after proof passes. This should create
  a suggested registry patch, not silently mutate doctrine.

## DDC Capability Installation Plan

DDC should be installed as LATTICE-native capability surfaces, not as a vendor
dump and not as a parallel system. The existing repo structure is already right:

```text
ddc/
  skills/
  cwicr/
  erp/
  n8n/
  converters/
  admin/
skills/ddc/
analysis/capabilities/
pixeltable/service/routes/
meta/DDC_MAPPING.md
```

### DDC Installation Order

#### 1. DDC Skills First

Source:

```text
github.com/datadrivenconstruction/DDC_Skills_for_AI_Agents_in_Construction
```

Install strategy:

- Clone or sync upstream into a temporary directory or local cache.
- Copy/adapt the relevant subset into `ddc/skills/`.
- Keep `skills/ddc/README.md` as the operator-facing description.
- Add a sync script later:

```text
scripts/sync-ddc-skills.py
```

Priority skill groups:

- IFC quantity takeoff
- cost estimation
- schedule phase extraction
- element classification and validation
- BIM report generation
- specification writing
- procurement/package breakdown

Organization:

```text
ddc/skills/
  quantity-takeoff/
    SKILL.md
  cost-estimation/
    SKILL.md
  scheduling/
    SKILL.md
  element-validation/
    SKILL.md
  reporting/
    SKILL.md
  specifications/
    SKILL.md
```

Each adapted skill should eventually get a capability registry row:

```text
analysis/capabilities/ddc-skills-capability-registry.yaml
```

Each row should include:

- original upstream path
- LATTICE adapted path
- served surface
- expected input
- expected output
- run contract when executable
- proof evidence after first successful run

#### 2. CWICR Cost Search Second

Source:

```text
github.com/datadrivenconstruction/OpenConstructionEstimate-DDC-CWICR
```

LATTICE home:

```text
ddc/cwicr/
```

Runtime:

```text
OrbStack Ubuntu VM
Qdrant on localhost:6333
ddc/cwicr/seed-qdrant.sh
ddc/cwicr/cost-search.py
```

Install strategy:

1. Keep Qdrant outside Pixeltable as the CWICR search engine for now.
2. Treat CWICR as a cost lookup service, not the system of record.
3. Write selected results back into Pixeltable once `0017+` DDC schema lands.
4. Add sidecar endpoint:

```text
POST /v1/erp/cost-search
```

Capability rows:

```text
analysis/capabilities/ddc-cwicr-capability-registry.yaml
```

Initial runnable proof:

```text
Input: "proposed 24 inch box tree installation"
Expected: ranked cost items with region, unit, and unit cost
Verifier: JSON shape + non-empty ranked results
Evidence: meta/harness/docs/sessions/<timestamp>-ddc-cwicr-cost-search.json
```

#### 3. OpenConstructionERP Third

Source:

```text
github.com/datadrivenconstruction/OpenConstructionERP
```

LATTICE home:

```text
ddc/erp/
```

Current adapter files:

- `ddc/erp/boq-adapter.py`
- `ddc/erp/cost-export.py`
- `ddc/erp/phase-adapter.py`

Install strategy:

1. Install/run OpenConstructionERP as an external local service.
2. Do not fork it into this repo.
3. Add LATTICE adapters in `ddc/erp/`.
4. Add FastAPI routes in:

```text
pixeltable/service/routes/erp.py
```

Planned endpoints:

```text
POST /v1/erp/boq
GET  /v1/erp/boq/{project_id}
GET  /v1/erp/export/{project_id}
POST /v1/erp/phases
```

Pixeltable writeback should wait for a DDC migration. Likely columns on IFC
element rows:

- `erp_item_id`
- `unit_cost`
- `unit_cost_region`
- `quantity`
- `quantity_unit`
- `boq_phase`
- `cost_last_updated`

Capability rows:

```text
analysis/capabilities/ddc-erp-capability-registry.yaml
```

Initial runnable proof:

```text
Input: tiny fixture element list
Expected: BOQ response or adapter dry-run output
Verifier: project id, item count, cost fields present
Evidence: meta/harness/docs/sessions/<timestamp>-ddc-erp-boq-proof.json
```

#### 4. n8n Workflow Patterns Fourth

Sources:

- `CAD-BIM-to-Code-Automation-Pipeline-DDC-Workflow-with-LLM-ChatGPT`
- `Project-management-n8n-with-task-management-and-photo-reports`

LATTICE home:

```text
ddc/n8n/workflows/
ddc/n8n/pipeline-templates/
```

Install strategy:

- Store upstream workflow JSON as reference artifacts.
- Translate useful workflow DAGs into LATTICE FastAPI pipelines.
- Do not run n8n as a production runtime.

Translation map:

| n8n concept | LATTICE equivalent |
|---|---|
| HTTP node | `httpx` call in FastAPI |
| Function node | Python function |
| OpenAI node | `claude -p` or model router through LATTICE |
| Spreadsheet | Pixeltable export + DuckDB WASM |
| Webhook | FastAPI route with idempotency |
| Schedule | GitHub Actions cron or sidecar scheduler |

Capability rows:

```text
analysis/capabilities/ddc-n8n-capability-registry.yaml
```

#### 5. Converters Last, Fallback Only

Source:

```text
github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN
```

LATTICE home:

```text
ddc/converters/
```

Install strategy:

- Use only `ddc-ifcconverter` and `ddc-dwgconverter`.
- Run only in OrbStack Ubuntu VM.
- Do not install or call `ddc-rvtconverter`.
- Do not install or call `ddc-dgnconverter`.
- Do not use Wine.

Use condition:

```text
Only after IfcOpenShell or ezdxf fails and writes a schema_drift/event record.
```

Capability rows:

```text
analysis/capabilities/ddc-converters-capability-registry.yaml
```

Most converter rows should start as `DEFERRED` or `BLOCKED` until a real failed
file justifies setup.

## DDC Codebase Organization

Keep DDC organized by purpose:

```text
ddc/
  README.md
  skills/              # adapted SKILL.md patterns
  cwicr/               # cost search setup and wrappers
  erp/                 # OpenConstructionERP adapters
  n8n/                 # workflow JSON references and translated templates
  converters/          # fallback Linux converter docs/scripts only
  admin/               # SQL/report/dashboard support files

analysis/capabilities/
  ddc-skills-capability-registry.yaml
  ddc-cwicr-capability-registry.yaml
  ddc-erp-capability-registry.yaml
  ddc-n8n-capability-registry.yaml
  ddc-converters-capability-registry.yaml

pixeltable/service/routes/
  erp.py               # BOQ, cost search, ERP adapter endpoints

meta/harness/docs/sessions/
  <timestamp>-ddc-*.json
```

Do not put DDC runtime state into Git. Git stores adapters, docs, capability
registries, and proof fixtures. Pixeltable stores durable evidence and selected
results once the schema exists.

## DDC First Runnable Proof

The first DDC golden-path proof should be small:

```text
Capability: ddc-skill-quantity-takeoff-fixture
Input: a tiny fixture of IFC-like element records
Runner: adapted DDC skill or deterministic local script
Output: quantity rows with element id, quantity, unit, and method
Verifier: JSON schema + expected item count
Evidence: meta/harness/docs/sessions/<timestamp>-ddc-quantity-takeoff-proof.json
```

This should not depend on OpenConstructionERP or Qdrant. Prove the skill pattern
first, then add CWICR and ERP.

## Recommended Next Session Plan

1. Re-run the verification baseline:

```bash
bash scripts/lattice-verify.sh HEAD
```

2. Open `/harness/capabilities` and confirm the browser still shows:

```text
single-file-agents -> Runnable -> codebase-context-ripgrep -> Run proof
```

3. Add one new deterministic run contract:

```text
python-docstring-rule
```

4. Add the first DDC capability registry:

```text
analysis/capabilities/ddc-skills-capability-registry.yaml
```

5. Add the first DDC proof fixture and runner:

```text
meta/harness/tools/ddc-quantity-takeoff-fixture.py
```

6. Wire it into:

```text
POST /v1/harness/capabilities/runs
```

7. Run it from the browser and capture proof evidence.

8. Only after this works, decide whether migration `0017` is ready.

## Do Not Start With

- Full OpenConstructionERP installation.
- Full CWICR/Qdrant seed.
- DDC converter installation.
- Pixeltable migration `0017`.
- Bulk copying all 221 DDC skills.

Those come after one DDC proof run proves the adapted skill shape.

