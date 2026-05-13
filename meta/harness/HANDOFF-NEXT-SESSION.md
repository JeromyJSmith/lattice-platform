# Meta-Harness Next Session Handoff

Date: 2026-05-12
Branch: `feature/meta-harness`
Repo root: `/Volumes/PixelTable/VW_iTWIN_Bridge/VW_iTwin_Bridge`
Baseline commit: `c83c8b4 feat(meta-harness): land capability matrix operator surface`

## Start Here

Read these files in order:

1. `AGENTS.md`
2. `meta/capability-research/ARCHITECTURE.md`
3. `meta/ARCHITECTURE.md`
4. `meta/harness/README.md`
5. `meta/harness/CURRENT-STATE.md`
6. `meta/harness/golden_path.md`
7. `meta/harness/TODO.md`
8. `meta/harness/docs/capability-lifecycle.md`
9. `meta/DDC_MAPPING.md`
10. `meta/ITWIN_MAPPING.md`
11. `meta/capability-research/census/repo-census-001.md`
12. `meta/capability-research/census/repo-census-002-ui-transfer.md`
13. `meta/capability-research/census/repo-census-003-vectorworks.md`
14. `meta/capability-research/census/repo-census-004-odbc.md`

Also skim the research packet that explains why this capability proof loop
exists:

- `/Volumes/PixelTable/VW_iTWIN_Bridge/Vectorworks_Bentley_iTwin_MARPA_Research_20260508/RESEARCH_PROPOSAL.md`
- `/Volumes/PixelTable/VW_iTWIN_Bridge/Vectorworks_Bentley_iTwin_MARPA_Research_20260508/BIS-BIM-iTWIN-DDC.md`
- `/Volumes/PixelTable/VW_iTWIN_Bridge/Vectorworks_Bentley_iTwin_MARPA_Research_20260508/BIS-DATA-research-content.md`
- `/Volumes/PixelTable/VW_iTWIN_Bridge/Vectorworks_Bentley_iTwin_MARPA_Research_20260508/marpa_live_agent_research_teams.html`

The current goal is still Golden Path 002:

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

The important operational change is that the previous dirty tree is now landed.
Do not rediscover or re-stage that work; start from commit `c83c8b4`.

## Purpose Clarification From Research

The capability matrix is a gate, not the destination. The long-term path is:

```text
harvest repository capability
-> write a bounded run contract
-> prove it through browser -> sidecar -> verifier
-> attach evidence to the row
-> use proven rows inside the Vectorworks/Pixeltable/iTwin/DDC workflow
```

The architecture source of truth for this research/capability layer is now:

```text
meta/capability-research/ARCHITECTURE.md
```

Use that file to understand what lives outside the harness, what remains in the
harness, where research artifacts are saved, where future Pixeltable tables may
live, and how a row moves from discovered -> contract-only -> runnable ->
proven -> adopted.

The research packet reframes the future operator workflow as an element-driven
data bus:

```text
Vectorworks exports and plugin data
-> Pixeltable as the aggregation and compute substrate
-> BIS/IFC/iTwin normalization for geometry, identity, and grouping
-> DDC/CWICR/OpenConstructionERP for cost, BOQ, schedule, LCA, and reporting
-> iTwin/TanStack surfaces for click-to-inspect and evidence-backed action
```

So the near-term harness work should continue exactly as scoped, but the proof
slices should be chosen because they validate pieces of that stack. After
`python-docstring-rule`, the DDC admin SQL proof is still the right next slice:
it is the smallest local proof toward the cost/reporting layer without Qdrant,
OpenConstructionERP, OrbStack, or migration `0017`.

## Capability Mapping Lens

When continuing the capability harvest, map every row to the eventual operator
interaction, even if the row is still contract-only:

```text
select or group an element
-> resolve element identity, geometry, material, and quantity
-> call a proven capability for cost, BOQ, schedule, LCA, reporting, or action
-> render the result in an iTwin/TanStack panel
-> preserve verifier output and evidence for replay
```

The Spark prototype discussed on 2026-05-12 is only an example, not a source of
truth. Its useful shape is:

```text
BIMViewer selection -> selected element state -> DDC cost engine -> CostPanel
```

For registry rows, use the existing fields to preserve that mapping:

- `description`: what the capability actually does.
- `wired_at`: where the current contract, adapter, script, or docs live.
- `invoked_by`: the future run surface or operator action that would call it.
- `serves`: the workflow layer it supports, such as viewer selection, element
  identity, geometry/quantity, material normalization, price source, CWICR
  lookup, BOQ, schedule, LCA, reporting, evidence, or actuation.
- `proof_evidence`: empty until a verifier-backed artifact exists.

Do not make rows green because they fit the vision. The vision guides
classification; proof still controls promotion.

## Repo Census Track

Before assuming the capability matrix is complete, run Repo Census 001:

```text
meta/capability-research/census/repo-census-001.md
```

The seed corpus includes iTwin viewer/UI/BIS repos, adjacent digital-twin AI and
knowledge-graph repos, DDC runtime/cost/skills repos, and DDC curated index
repos. The census should verify URLs, discover missing `iTwin/*` and
`datadrivenconstruction/*` repositories, harvest dependency and schema
vocabulary, then create contract-only capability rows. Do not bulk install the
dependencies and do not write migration `0017` during this census.

Initial live metadata harvest on 2026-05-13 created:

```text
analysis/capabilities/repo-census-001-capability-registry.yaml
```

It adds ten contract-only rows for the first high-value iTwin/BIS/DDC source
repositories. These rows are mapping targets only. Their `proof_evidence` fields
must remain empty until a Golden Path 002 proof fixture exists.

Repo Census 002 adds the UI-transfer lens:

```text
analysis/capabilities/repo-census-002-ui-transfer-capability-registry.yaml
meta/capability-research/census/repo-census-002-ui-transfer.md
```

It captures the stronger thesis that DDC's web UI modules should be rehosted as
iTwin/TanStack element panels: selected BIM element -> BIM/BOQ linkage ->
quantity rules -> CWICR/cost match -> formula recalculation -> evidence. Treat
OpenConstructionERP UI code as pattern/source-contract material because of the
AGPL surface; do not copy it directly without legal review.

Repo Census 003 adds the Vectorworks source corpus:

```text
analysis/capabilities/repo-census-003-vectorworks-capability-registry.yaml
meta/capability-research/census/repo-census-003-vectorworks.md
```

It maps official scripting, worksheet, SDK, SDKExamples, MCP bridge, Python
helper, C++ quantity plugin, ODBC/data-link, and community scripting sources.
Use this track to build the Vectorworks -> Pixeltable data spine: worksheet or
script extraction first, C++ SDK plugin later, all evidence-gated.

Repo Census 004 adds the ODBC/database-link sweep:

```text
analysis/capabilities/repo-census-004-odbc-capability-registry.yaml
meta/capability-research/census/repo-census-004-odbc.md
```

It maps Vectorworks-native ODBC/database docs, worksheet database semantics,
Data Manager mapping, old Postgres/MySQL community references, driver managers,
Python/Arrow/Parquet ODBC export adapters, and current vendor driver candidates.
ODBC is an ingest/sync bridge only; Pixeltable remains the substrate, and no
connection strings or credentials belong in the repo.

## Committed Baseline

Commit `c83c8b4` landed the coherent Meta-Harness slice:

- `analysis/capabilities/` now has 23 registries and 200 capability rows.
- `analysis/capabilities/ddc-capability-registry.yaml` exists with six DDC contract-only rows.
- `pixeltable/service/routes/harness.py` exposes `/v1/harness/*`.
- `pixeltable/service/main.py` wires the harness router.
- `/harness/benchmarks` and `/harness/capabilities` exist in TanStack.
- `scripts/check-python-docstrings.py`, `scripts/audit-dead-dna.sh`, and `scripts/lattice-verify.sh` are active.
- Benchy reference material is incorporated under `meta/harness/references/benchy/`.
- Nested `.vite/`, pycache, `dist/`, env files, and runtime dust are ignored.

The worktree was clean immediately after the commit.

## Post-Cleanup Review Addendum

Codex re-read this handoff after the other agent cleaned and committed the
previous dirty tree. The current handoff is the active continuation source and
already includes the work completed across both sessions:

- Golden Path 002 is still the current execution path.
- `c83c8b4` is the clean committed baseline to start from.
- `python-docstring-rule` is allowlisted as a runnable `script_exit_code`
  capability and has direct plus browser proof artifacts.
- DDC is represented as registry data in
  `analysis/capabilities/ddc-capability-registry.yaml`; it is not installed or
  runtime-proven.
- No dirty-tree recovery, restaging, or cleanup should be repeated in the next
  session.

Use the next slice below as written: inspect the `python-docstring-rule` browser
proof artifact, then make the smallest registry promotion commit if the evidence
is acceptable.

## Current Matrix State

Latest live matrix response observed before this handoff:

| Status | Count |
|---|---:|
| Green / proven | 1 |
| Amber / needs proof or deferred | 151 |
| Red / failing, blocked, or invalid | 48 |
| Total | 200 |

Registry audit output from the committed tree:

```text
registries=23
active=153
deferred=44
blocked=3
bootstrap_empty=4
```

Known nuance: the running sidecar process may be stale. Restart it after pulling
or resuming so it loads the committed `python-docstring-rule` runner in
`pixeltable/service/routes/harness.py`.

## Servers

If the session starts cold or the sidecar is stale, restart both surfaces.

Sidecar:

```bash
cd /Volumes/PixelTable/VW_iTWIN_Bridge/VW_iTwin_Bridge/pixeltable
PIXELTABLE_HOME=/Volumes/PixelTable/.pixeltable uv run uvicorn service.main:app --host 127.0.0.1 --port 7770
```

Console:

```bash
cd /Volumes/PixelTable/VW_iTWIN_Bridge/VW_iTwin_Bridge
bun run dev --host 127.0.0.1
```

Open:

```text
http://127.0.0.1:3000/harness/capabilities
```

## What Is Runnable Now

Backend allowlist in `pixeltable/service/routes/harness.py` includes:

| Capability | Runner kind | Command / path |
|---|---|---|
| `codebase-context-ripgrep` | `single_file_agent` | `uv run meta/harness/tools/codebase-context-agent.py ...` |
| `python-docstring-rule` | `script_exit_code` | `uv run python scripts/check-python-docstrings.py` |

The sidecar must execute only allowlisted contracts. There is no arbitrary shell
or arbitrary Python endpoint.

## DDC State

DDC is registered, not proven.

File:

```text
analysis/capabilities/ddc-capability-registry.yaml
```

Rows:

- `ddc-skills-process-patterns`
- `openconstructionerp-boq-adapter`
- `cwicr-qdrant-cost-search`
- `ddc-n8n-workflow-pattern-extraction`
- `ddc-converter-fallback-policy`
- `ddc-admin-sql-reporting-stubs`

All six are contract-only amber rows because `proof_evidence` is empty. This is
correct. Do not install DDC services or write migrations just to make them green.

## Proof Artifacts Already Present

Codebase context proof:

```text
meta/harness/docs/sessions/2026-05-12-codebase-context-proof-run.json
meta/harness/docs/sessions/2026-05-12-codebase-context-sidecar-run.json
meta/harness/docs/sessions/2026-05-12-codebase-context-benchmark.json
meta/harness/docs/sessions/2026-05-12T13-15-32-115Z-codebase-context-ripgrep-browser-run.json
```

Python docstring proof:

```text
meta/harness/docs/sessions/2026-05-12-python-docstring-rule-direct-run.json
meta/harness/docs/sessions/2026-05-12T18-02-26-539Z-python-docstring-rule-browser-run.json
```

The `python-docstring-rule` registry row is runnable but still needs an explicit
registry `proof_evidence` decision before it should be treated as green/proven.

## Verification Passed For `c83c8b4`

These checks passed before the commit:

```bash
bash scripts/audit-dead-dna.sh
uv run python scripts/check-python-docstrings.py
uv run --extra dev pytest tests/no_pxt/test_harness_capability_runs.py
bun test src/runtime/pixeltable/sidecar-client.test.ts
bunx biome check src/components/Header.tsx src/runtime/pixeltable/sidecar-client.ts src/runtime/pixeltable/sidecar-client.test.ts src/routes/harness src/server/harness
bash scripts/pre-commit-docs-check.sh
bash scripts/lattice-verify.sh HEAD
bun run build
git diff --check
```

Notes:

- `src/routeTree.gen.ts` is generated by TanStack and noisy under Biome.
- `meta/harness/references/benchy/` is reference material; do not lint it as
  LATTICE-authored source.
- `bun run build` emits Vite externalization warnings for Node modules in the
  server-side sidecar client path, but the build completed.

## Hard Rules

Do not violate these:

- Do not edit landed migrations `0001` through `0016`.
- Do not touch secrets, `.env*`, OAuth credentials, or provider tokens.
- Do not change branch protection or merge to `main`.
- Do not delete migrations, branches, or issues.
- Do not make incidental doctrine changes.
- Do not expose arbitrary shell execution from the sidecar.
- Do not make DuckDB or SQLite durable storage. Pixeltable is the substrate;
  DuckDB WASM is browser analytics over exported Arrow/Parquet.

## Immediate Next Slice

Do this next:

1. Restart sidecar and console.
2. Open `/harness/capabilities`.
3. Confirm both `codebase-context-ripgrep` and `python-docstring-rule` appear
   under the `Runnable` filter.
4. Run `python-docstring-rule` from the browser.
5. Inspect the evidence artifact.
6. If the artifact is good, update
   `analysis/capabilities/single-file-agents-capability-registry.yaml` so
   `python-docstring-rule` cites its proof evidence.
7. Re-run verification and commit that small promotion.

Acceptance:

- Browser Run button executes through TanStack -> FastAPI sidecar -> allowlisted
  command.
- Evidence includes `capability_id`, `run_id`, `ok`, `command`, `artifact`,
  `verification`, stdout/stderr, return code, and timing.
- Registry cites proof only after evidence has been inspected.
- Matrix count remains 200 and green increases only if the row is legitimately
  proof-backed.

## Next DDC Slice

After `python-docstring-rule` is correctly proof-backed, promote one DDC row from
contract-only to proof-backed.

Start with:

```text
ddc-admin-sql-reporting-stubs
```

Why:

- Local only.
- No Qdrant.
- No OpenConstructionERP runtime.
- No OrbStack.
- No migration.

Likely task:

- Add `scripts/check-ddc-admin-sql.py`.
- Validate `ddc/admin/project-summary.sql`, `ddc/admin/element-counts.sql`, and
  `ddc/admin/boq-status.sql` exist and satisfy the current lightweight contract.
- Register an allowlisted `script_exit_code` runner.
- Run it from `/harness/capabilities`.
- Write proof under `meta/harness/docs/sessions/`.
- Add proof evidence to `ddc-admin-sql-reporting-stubs`.

## Not Now

- Do not write migration `0017` until the pre-flight evidence shape is stable.
- Do not install OpenConstructionERP, Qdrant/CWICR, or converters as part of the
  first DDC proof.
- Do not promote all DDC rows at once.
- Do not build webhooks before native Linear/GitHub sync gaps are measured.
- Do not move the Meta-Harness into its own repository until at least one
  browser-visible, sidecar-verified, evidence-backed pre-flight path is stable.
