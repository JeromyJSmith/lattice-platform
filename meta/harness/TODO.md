# MetaHarness TODO

This is the decisive queue for reaching a functional MetaHarness pre-flight.
Golden Path 001 has proof evidence. The next target is Golden Path 002:

```text
capability row -> run contract -> browser execution -> sidecar/verifier
-> evidence artifact -> row result -> promotion/tracking
```

## P0 — Functional Pre-Flight

| Order | Task | Acceptance |
|---:|---|---|
| 1 | Lock the pre-flight contract in `meta/harness/golden_path.md` and this TODO | A new agent can identify the next path, end state, operator workflow, and not-now boundaries without this chat |
| 2 | Confirm docs entrypoints point to the contract | `meta/harness/README.md` or `meta/harness/library.yaml` links to `golden_path.md`, `TODO.md`, and `docs/capability-lifecycle.md` |
| 3 | Reconcile the body-cell harness with the outer wrapper at `/Volumes/PixelTable/VW_iTWIN_Bridge/meta/` | `body-registry.yaml`, `config.yaml`, `metaharness.lock.yaml`, and body-cell docs agree on active path, phase, and evidence boundary |
| 4 | Define the canonical pre-flight evidence path | The run contract names where filesystem evidence lands now and how wrapper-level `runs/` or `evidence/` receives an artifact or pointer |
| 5 | Normalize capability row states around proof | Rows with no proof are marked or documented as contract-only; no unproven row is described as trusted |
| 6 | Define one bounded pre-flight run contract from `domain_spec.md` | Contract includes goal, inputs, allowed paths, denied paths, timeout, verifier, evidence path, expected output, promotion rule, and scalar pass/defer/fail result |
| 7 | Exercise the operator path through the browser surface | `/harness/capabilities` shows the selected row, proof state, missing wires, run result or pending-browser marker, and troubleshooting guidance |
| 8 | Exercise the sidecar/verifier path for the same contract | Registered sidecar/verifier execution writes stdout, stderr, exit code, verifier status, artifact path, and failure reason when applicable |
| 9 | Write the row result from evidence, not assertion | The row cites the proof artifact for `PASS`, cites a blocker for `DEFER`, or cites a failed verifier result for `FAIL` |
| 10 | Run light verification before handoff, full verification before commit | At minimum, affected docs are reviewed; before commit run `bash scripts/pre-commit-docs-check.sh` and any changed-surface checks required by the actual edits |

## P0 — Guardrails Before Promotion

| Order | Task | Acceptance |
|---:|---|---|
| 1 | Keep activation evidence-gated | Harvest and matrix rows can exist before proof; manifest and registry `ACTIVE` rows require passing proof evidence |
| 2 | Keep metrics proof-gated | Pass rate, runtime, cost, model/provider, input shape, output shape, and failure mode start only after a passing proof run |
| 3 | Keep sidecar execution registered | Browser components never shell out; the server-side client calls the FastAPI sidecar, and the sidecar accepts only registered jobs/contracts |
| 4 | Keep filesystem proof canonical during pre-flight | Pixeltable ingestion may be designed, but pre-flight trust comes from file-backed evidence until evidence tables are live |
| 5 | Keep protected paths untouched | No landed migration edits, no secrets, no branch-protection changes, no unrelated code/routes/capability-YAML edits |

## P1 — Substrate And Coverage

| Order | Task | Acceptance |
|---:|---|---|
| 1 | Validate the docs mirror contract from Amendment 08 | `scripts/doc-mirror-manifest.yaml` has active mirrors, deferred mirrors, local paths, source repos, and categories; stubs clearly point to Issues #23-25 |
| 2 | Confirm Docs MetaHarness stubs are intentional | `score-docs.sh`, `sync-doc-mirrors.sh`, `ingest-docs.py`, and `detect-doc-gaps.py` exit cleanly and state their tracking issue |
| 3 | Define the `0017` Pixeltable migration boundary without writing it | Target tables for capabilities, scripts, jobs, verification runs, evidence, model benchmarks, and task state are listed; no migration exists until the pre-flight evidence shape settles |
| 4 | Populate bootstrap-empty registries | `pixeltable`, `claude-code`, `deck-gl`, and `web-ifc` no longer have `spec-verified: false` with zero useful rows |
| 5 | Add docs substrate coverage checks for trusted rows | ACTIVE rows have doc coverage or explicit docs-gap rows once ingestion is live |
| 6 | Connect Graphify, GitNexus, and InfraNodus outputs to harness docs | Each has a documented invocation, output artifact path, and contract-only/proven state |

## P1 — Uplift After Pre-Flight Works

| Order | Task | Acceptance |
|---:|---|---|
| 1 | Build a Python inventory script | Scripts, modules, tests, migrations, generated files, and obsolete files are classified without changing them |
| 2 | Add docstrings to legacy Python files in scoped batches | `uv run python scripts/check-python-docstrings.py --all` trends toward zero violations without incidental rewrites |
| 3 | Add uv inline metadata to runnable one-shot scripts where appropriate | Each script can run via `uv run path/to/script.py` without hidden repo environment assumptions |
| 4 | Define the portable MetaHarness repo contract | Clear split exists between core harness, adapters, project config, Pixeltable backend, and LATTICE-specific body-cell config |
| 5 | Extract only after one LATTICE pre-flight passes | No portable split occurs before a browser-visible, sidecar-verified, evidence-backed run succeeds |

## Not Now

- Do not edit code, routes, migrations, or capability YAML while this task is
  only a documentation lock.
- Do not edit landed migrations for cleanup.
- Do not write migration `0017` until pre-flight evidence shape is stable.
- Do not promote or trust active-looking capability rows that lack proof.
- Do not migrate all source files into Pixeltable in one jump.
- Do not build custom webhooks before native Linear/GitHub sync gaps are
  measured.
- Do not turn every library module into a uv inline script; reserve inline
  metadata for runnable one-shot scripts.
- Do not replace browser pre-flight with chat-only execution.
