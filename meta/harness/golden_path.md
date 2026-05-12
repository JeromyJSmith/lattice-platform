# Golden Path 001 — Promote a Single-File Harness Agent

This is the first LATTICE Meta-Harness golden path. It defines what success
means for incorporating an external single-file agent pattern into LATTICE
without turning the repository into a vendor dump or exposing arbitrary scripts
as callable tools.

## End Goal

Promote one Disler-style uv single-file agent into a LATTICE-owned harness job
that can be discovered through the FastAPI sidecar, executed as a bounded job,
verified by deterministic checks, visualized in the Benchmarks console, and
recorded as evidence for capability promotion.

The first candidate is:

| Field | Value |
|---|---|
| Source repo | `https://github.com/disler/single-file-agents` |
| Source capability | `sfa_codebase_context_agent_w_ripgrep_v3.py` pattern |
| LATTICE target | `meta/harness/tools/codebase-context-agent.py` |
| Sidecar surface | `POST /v1/harness/single-file-agents/runs` |
| Console surface | `/harness/benchmarks` |
| Evidence class | capability proof-run report |

## Definition Of Success

This golden path is successful when all of the following are true:

1. Source provenance is recorded.
   - The upstream repo URL and commit SHA are written in the capability harvest,
     matrix, manifest, registry row, and promoted script header.
   - The source mirror policy is explicit: reference source may live under
     `meta/harness/references/`, but runnable code lives in LATTICE-owned paths.

2. The promoted script is a proper LATTICE harness job.
   - It runs with `uv run meta/harness/tools/codebase-context-agent.py`.
   - It uses uv inline script metadata when it has Python dependencies.
   - It has a module docstring and public-symbol docstrings.
   - It accepts explicit CLI input and emits one bounded JSON artifact.
   - It does not read secrets unless the job registration names the allowed env
     vars.

3. The sidecar controls execution.
   - The script is not exposed as a free-form tool.
   - `GET /v1/harness/single-file-agents/catalog` lists the script as a
     registered candidate or active job.
   - `POST /v1/harness/single-file-agents/runs` accepts only registered script
     IDs, input JSON, timeout, sandbox/workdir policy, and evidence path.
   - Run status, stdout, stderr, exit code, artifact path, and verifier result
     are captured.

4. The first proof run passes.
   - The job runs against a small fixture or bounded repo slice.
   - The output artifact contains selected files, rationale, command evidence,
     and a clear pass/fail status.
   - A verifier command confirms the artifact shape and expected outcome.
   - The proof report is written under `meta/harness/docs/sessions/` until
     Pixeltable evidence tables are live.

5. Capability promotion is evidence-gated.
   - Harvest and matrix rows may exist before the proof run, but metrics start
     at zero.
   - The manifest row is created only after the first passing proof run.
   - The registry row can become `ACTIVE` only when it cites that proof evidence.
   - After promotion, metrics track pass rate, runtime, cost, model/provider,
     input shape, output shape, and failure mode.

6. The Benchmarks console can show the result.
   - A Benchy-compatible report is produced or transformed from the proof run.
   - `/harness/benchmarks` can load the report JSON.
   - The report includes model/provider, task, score or pass signal, latency,
     cost when known, and failure mode when applicable.

7. Repo verification passes.
   - `uv run python scripts/check-python-docstrings.py`
   - `bash scripts/audit-dead-dna.sh`
   - `bash scripts/pre-commit-docs-check.sh`
   - `bash scripts/lattice-verify.sh HEAD`
   - `bun run build` if the console or route tree changed

## Non-Goals

- Do not vendor upstream `.git` directories.
- Do not import upstream `.env*`, OAuth files, local caches, or secrets.
- Do not promote every example script at once.
- Do not make DuckDB or SQLite durable storage; DuckDB is analysis over exported
  Pixeltable data.
- Do not write migration `0017` until the evidence shape has survived this path.
- Do not expose arbitrary shell or Python execution over the sidecar.

## Hard Prohibitions

These rules survive every harness workflow:

- Do not edit landed migrations `0001` through `0016`.
- Do not touch secrets, `.env*`, OAuth credentials, or provider tokens.
- Do not change branch protection or merge to `main`.
- Do not delete migrations, branches, or issues.
- Do not make incidental doctrine changes; doctrine changes must be the explicit
  point of the PR.

## Execution Steps

| Step | Artifact | Success check |
|---|---|---|
| 1. Mirror source reference | `meta/harness/references/single-file-agents/` or provenance doc | No `.git`, `.env*`, caches, or generated junk copied |
| 2. Harvest capability | `analysis/capabilities/single-file-agents-capability-harvest.md` | Source surfaces inventoried |
| 3. Matrix decision | `analysis/capabilities/single-file-agents-capability-matrix.md` | First candidate has proof target |
| 4. Promote script | `meta/harness/tools/codebase-context-agent.py` | `uv run ... --help` works |
| 5. Register sidecar job | `pixeltable/service/routes/harness.py` | Catalog includes registered script ID |
| 6. Run proof | `meta/harness/docs/sessions/<date>-codebase-context-proof-run.json` | Verifier passes |
| 7. Emit benchmark report | `meta/harness/docs/sessions/<date>-codebase-context-benchmark.json` | Console can load JSON |
| 8. Create manifest | `analysis/capabilities/single-file-agents-capability-manifest.yaml` | Manifest cites proof evidence |
| 9. Activate registry row | `analysis/capabilities/single-file-agents-capability-registry.yaml` | ACTIVE row cites proof evidence |
| 10. Verify repo | scripts listed above | All required checks pass |

## First Proof Fixture

Use a tiny bounded fixture before pointing the job at the full repo:

```text
Goal: identify the files relevant to adding or changing a FastAPI sidecar route
Input: task text plus an allowlisted repo root
Expected output: JSON listing relevant files, why each file matters, and one
verification command
Verifier: JSON schema check plus file-exists check for every selected path
```

This is deliberately small. The point is to prove the harness path works before
scaling to larger codebase-context jobs.

## TanStack, FastAPI, uv Method

The LATTICE application boundary is explicit:

```text
TanStack Start UI
  -> server-side SidecarClient
  -> Python FastAPI sidecar
  -> registered uv single-file script
  -> JSON evidence artifact
  -> Benchmarks console / Pixeltable evidence later
```

Rules:

- TanStack owns operator interaction, routing, visual state, and report display.
- TanStack server code calls `SidecarClient`; browser components do not execute
  Python and do not shell out.
- `SidecarClient` uses a UNIX domain socket by default and TCP only when
  `PIXELTABLE_SERVICE_URL` is set.
- The FastAPI sidecar is the execution boundary for harness jobs.
- The sidecar runs only registered script IDs and resolves all paths inside the
  repository root.
- Python dependencies live in the `pixeltable/` uv project for the sidecar.
- One-shot harness scripts use uv inline metadata and can also run directly via
  `uv run meta/harness/tools/<script>.py` for deterministic proof/debug runs.
- The console consumes benchmark/report JSON; it does not become a Python
  runtime.

## Exit Criteria

Once this golden path passes, LATTICE has a repeatable pattern for every other
single-file harness agent:

```text
source reference -> promoted LATTICE script -> sidecar job -> proof run
-> benchmark report -> manifest -> ACTIVE registry row -> tracked metrics
```

That is the minimum viable Meta-Harness loop.

## Execution 001 Status

Status: PASS on 2026-05-12.

Evidence:

- `meta/harness/docs/sessions/2026-05-12-codebase-context-proof-run.json`
- `meta/harness/docs/sessions/2026-05-12-codebase-context-sidecar-run.json`
- `meta/harness/docs/sessions/2026-05-12-codebase-context-benchmark.json`
- `meta/harness/docs/sessions/2026-05-12-golden-path-001-execution.md`

## Diagnostic Surface

Golden-path capabilities should be visible before they run. The pre-flight
diagnostic page is:

```text
/harness/capabilities
```

It reads:

```text
GET /v1/harness/capabilities/matrix
```

The page groups capability registry rows by source tool/repository and shows:

- pass/deferred/fail status
- capability contract paths
- proof evidence paths
- missing wires or missing proof artifacts
- troubleshooting guidance

## Golden Path 002 — Functional MetaHarness Pre-Flight

Golden Path 001 proved that one promoted script can run and leave evidence. The
next path locks the pre-flight loop that decides whether a capability is ready
to be trusted by an operator.

The path is:

```text
capability row
  -> run contract
  -> browser execution
  -> sidecar/verifier
  -> evidence artifact
  -> row result
  -> promotion/tracking
```

This is still a pre-flight path. It proves that the harness can see, run,
verify, and classify a capability before the capability is promoted into routine
use.

### End State

A functional MetaHarness pre-flight exists when a new agent can open the harness
docs, select one candidate capability row, execute the bounded pre-flight path,
and determine one of three outcomes without asking for missing context:

- `PASS`: the capability has a run contract, browser-visible execution result,
  sidecar/verifier result, evidence artifact, and row-level proof reference.
- `DEFER`: the capability contract is clear, but proof is missing, blocked, or
  intentionally scheduled later.
- `FAIL`: the capability contract, execution, verification, evidence, or
  promotion rule is broken and must not be trusted.

The successful end state is not "many ACTIVE rows." It is one reliable operator
workflow that prevents unproven rows from being treated as working capabilities.

### Definition Of Success

MetaHarness pre-flight is functional when all of the following are true:

1. Capability rows are contract-first.
   - Every candidate row names the source, intended harness surface, invocation
     shape, verifier expectation, evidence path, and owner or next action.
   - Rows without proof are explicit contracts only. They may guide work, but
     they are not trusted execution surfaces.

2. Run contracts are bounded.
   - A pre-flight contract names input, expected output, timeout, working
     directory, allowed files, denied files, evidence destination, and verifier.
   - The contract is specific enough that the browser and sidecar can execute
     the same job without chat-only interpretation.

3. Browser execution is visible to the operator.
   - `/harness/capabilities` or the active harness browser surface shows the
     selected row, status, proof state, missing wires, and troubleshooting
     guidance.
   - Browser execution never shells out directly. It calls the server-side
     client, which calls the FastAPI sidecar.

4. The sidecar and verifier decide the result.
   - The FastAPI sidecar accepts only registered jobs or registered capability
     run contracts.
   - The verifier returns a deterministic pass/defer/fail result with stdout,
     stderr, exit code, artifact path, and failure reason where applicable.

5. Evidence is file-backed before it is trusted.
   - Each pre-flight run writes a durable artifact under the documented harness
     evidence/session path.
   - Until Pixeltable evidence tables are live, filesystem evidence is the
     canonical proof record for pre-flight.
   - Later Pixeltable ingestion must preserve the same run ID, source path,
     verifier result, and artifact path.

6. Row results feed promotion and tracking.
   - A row can move toward manifest or registry activation only when it cites a
     passing proof artifact.
   - Metrics start only after proof: pass rate, runtime, cost when known,
     model/provider, input shape, output shape, and failure mode.
   - Rows that are useful but unproven remain `DEFER` or contract-only; they do
     not receive dispatch weight.

### Operator Workflow

1. Open `meta/harness/TODO.md` and choose the first incomplete P0 task.
2. Open `/harness/capabilities` to inspect current capability rows and proof
   state.
3. Select one row with a clear contract and no trusted proof.
4. Confirm the run contract: goal, inputs, allowed paths, denied paths, timeout,
   verifier, evidence path, and promotion rule.
5. Run the pre-flight through the browser surface when available; otherwise run
   the registered sidecar/verifier command and record that browser execution is
   still pending.
6. Inspect the evidence artifact and verifier result.
7. Update only the row result and tracking fields supported by the current
   contract. Do not promote by hand if proof is missing.
8. Record follow-up as a P0/P1 TODO item if the row is deferred or failed.

### Not-Now Boundaries

- Do not edit code, routes, migrations, or capability YAML as part of this docs
  lock unless a later task explicitly grants that scope.
- Do not write migration `0017` until the pre-flight evidence shape is stable.
- Do not treat existing ACTIVE rows as trusted if they lack proof artifacts.
- Do not replace the browser operator surface with chat-only execution.
- Do not route arbitrary shell or Python commands through the sidecar.
- Do not use Pixeltable, DuckDB, or wrapper-level evidence as a reason to skip
  filesystem evidence during pre-flight.
- Do not broaden doctrine beyond the MetaHarness pre-flight path described here.
