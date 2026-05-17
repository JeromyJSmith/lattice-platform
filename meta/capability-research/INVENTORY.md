# Capability Research Inventory

Date: 2026-05-13
Status: current organization audit

This inventory answers three questions:

1. Where is the capability research material right now?
2. What is misplaced or missing?
3. What should be organized before running InfraNodus, Graphify, or GitNexus?

## Current State

The repo already has the beginnings of a capability research system:

| Artifact class | Current location | Status |
|---|---|---|
| System architecture | `meta/capability-research/ARCHITECTURE.md` | Good home after reorganization |
| Human research sweeps | `meta/capability-research/census/` | Good home after reorganization |
| Capability registries | `analysis/capabilities/` | Good home for matrix-consumed YAML |
| Proof/execution docs | `meta/harness/` | Good home for Golden Path and verifier policy |
| Runtime API surface | `pixeltable/service/routes/harness.py` | Good current sidecar location |
| Operator UI | `/harness/capabilities`, `/harness/benchmarks` | Good current browser location |
| Research source mappings | `meta/DDC_MAPPING.md`, `meta/ITWIN_MAPPING.md` | Good top-level integration docs |
| Future schema candidates | `meta/capability-research/ARCHITECTURE.md` | Documented only; no migration yet |

The main correction made by this audit: repo-census documents moved out of
`meta/harness/docs/` and into `meta/capability-research/census/`. They are
research artifacts, not harness execution instructions.

## Directory Boundary

Use this boundary going forward:

| Belongs in | Content |
|---|---|
| `meta/capability-research/` | Research architecture, source inventory, corpus manifests, tool readiness, census notes |
| `meta/capability-research/census/` | One markdown file per source-family sweep |
| `meta/capability-research/tools/` | InfraNodus, Graphify, GitNexus readiness, inputs, outputs, and invocation notes |
| `analysis/capabilities/` | Matrix-readable capability registry YAML only |
| `meta/harness/` | Proof contracts, verifier policy, Golden Path, evidence rules, current harness handoff |
| `meta/harness/docs/sessions/` | Proof evidence and session artifacts, not architecture |
| `meta/` | Whole-system architecture, schema, API, integration maps, roadmap |
| `pixeltable/service/**` | Runtime sidecar code after proof |
| `src/routes/**` | Operator UI after proof |

## What Exists

### Research/Census Docs

| File | Purpose |
|---|---|
| `meta/capability-research/census/repo-census-001.md` | iTwin, BIS, DDC, and construction intelligence source sweep |
| `meta/capability-research/census/repo-census-002-ui-transfer.md` | DDC UI transfer into iTwin/TanStack element panels |
| `meta/capability-research/census/repo-census-003-vectorworks.md` | Vectorworks scripts, SDK, MCP, plugin, worksheet, ODBC references |
| `meta/capability-research/census/repo-census-004-odbc.md` | ODBC and database-link opportunity sweep |

### Registry YAML

| File | Purpose |
|---|---|
| `analysis/capabilities/repo-census-001-capability-registry.yaml` | Contract-only rows for first iTwin/BIS/DDC corpus |
| `analysis/capabilities/repo-census-002-ui-transfer-capability-registry.yaml` | Contract-only rows for DDC UI and panel transfer |
| `analysis/capabilities/repo-census-003-vectorworks-capability-registry.yaml` | Contract-only rows for Vectorworks source material |
| `analysis/capabilities/repo-census-004-odbc-capability-registry.yaml` | Contract-only rows for ODBC/database-link material |
| `analysis/capabilities/infranodus-capability-registry.yaml` | Existing InfraNodus capability harvest, needs readiness reconciliation |
| `analysis/capabilities/gitnexus-capability-registry.yaml` | Existing GitNexus capability harvest, needs readiness reconciliation |
| `analysis/capabilities/graphify-capability-registry.yaml` | Graphify CLI capability harvest for the current local graph workflow |
| `analysis/capabilities/graphify-safishamsi-capability-registry.yaml` | Existing graphifyy capability harvest, likely stale until install/path proof |

### InfraNodus Skills Source

The repo currently has a local vendored skill source at:

```text
.claude/skills/skills-master/
```

Audit:

```text
meta/capability-research/tools/infranodus-skills-master-audit.md
```

Treat it as source material, not active LATTICE doctrine. The most relevant
skills are `infranodus-cli`, `ontology-generator`, `shifting-perspective`,
`critical-perspective`, `cognitive-variability`, and `actionize`.

### Local Prior Tool History

The PixelTable volume and user-local config already contain Graphify and
GitNexus history. See:

```text
meta/capability-research/inventory/local-graph-tool-audit.md
```

Summary:

- `graphify` is installed at `/Users/ojeromyo/.local/bin/graphify`.
- `gitnexus` is installed at `/opt/homebrew/bin/gitnexus`, version `1.6.3`.
- InfraNodus is connected in Claude MCP.
- MARPA Platform has a large existing `.gitnexus` index.
- MARPA 918 Juniper has existing `graphify-out` artifacts and a useful
  `.graphifyignore` pattern.
- The current LATTICE repo is not indexed in GitNexus and should not reuse old
  graph outputs as if they describe this codebase.

## Misplaced Or Stale Items

| Item | Current issue | Target handling |
|---|---|---|
| Repo-census markdown under `meta/harness/docs/` | Research artifacts were mixed with harness execution docs | Moved to `meta/capability-research/census/` |
| `analysis/capabilities/infranodus-capability-registry.yaml` | Some `wired_at` paths point to non-existent `analysis/infranodus/*` files | Reconcile in a future registry cleanup after tool docs land |
| `analysis/capabilities/gitnexus-capability-registry.yaml` | Claims `.mcp.json`, generated skills, hooks, and graph outputs that may not exist in current repo state | Treat as harvested intent, not proven readiness |
| `analysis/capabilities/graphify-capability-registry.yaml` | Tracks the current Graphify CLI surface and repo-local wrapper; broader semantic and repo-wide runs are still deferred | Keep Graphify scoped to bounded proof and explicit output paths |
| `analysis/capabilities/graphify-safishamsi-capability-registry.yaml` | References tutorial ingestion scripts and future substrate intake | Keep contract-only until proof fixture exists |
| `3d_assets/` | Untracked local work appears in git status | Leave untouched; out of scope for capability research organization |

## Missing Organization Pieces

These should exist before Graphify or GitNexus runs over the repo:

| Missing piece | Why it matters | Suggested home |
|---|---|---|
| Corpus manifest | Prevents tools from indexing `node_modules`, `dist`, runtime dust, or unrelated assets | `meta/capability-research/inventory/corpus-manifest.yaml` |
| Tool output manifest | Defines where InfraNodus/Graphify/GitNexus outputs are allowed to land | `meta/capability-research/tools/output-manifest.md` |
| InfraNodus run contract | Makes gap analysis repeatable and evidence-backed | `meta/capability-research/tools/infranodus-runbook.md` |
| Graphify config decision | Prevents graph outputs from scattering across the repo | `meta/capability-research/tools/graphify-runbook.md` |
| GitNexus config decision | Prevents accidental full-repo indexing before folder boundaries settle | `meta/capability-research/tools/gitnexus-runbook.md` |
| Registry readiness reconciliation | Aligns ACTIVE rows with actual files and installed tools | `meta/capability-research/tools/READINESS.md` |
| Future schema design note | Converts doc inventory into possible `lattice/knowledge/*` tables | `meta/capability-research/schema-0017-candidates.md` |

## Recommended Tool Order

1. InfraNodus over curated docs only.
2. Fix docs and folder gaps found by InfraNodus.
3. Define corpus/output manifests.
4. Run Graphify over curated doc/code subsets, not the whole repo.
5. Run GitNexus only after code boundaries and ignored paths are explicit.
6. Convert stable outputs into registry rows and future Pixeltable schema
   candidates.

## Immediate Next Actions

P0:

1. Keep this folder structure.
2. Keep `tools/READINESS.md`, `tools/output-manifest.md`, and
   `inventory/corpus-manifest.yaml` current.
3. Run InfraNodus only against the curated document list.

P1:

1. Reconcile stale Graphify/GitNexus/InfraNodus registry `wired_at` fields.
2. Add small deterministic run contracts for InfraNodus gap analysis and one
   Graphify doc-corpus pass.
3. Define where outputs land and how evidence artifacts cite them.

P2:

1. Design `lattice/knowledge/*` and `lattice/harness/*` migration candidates.
2. Only then consider migration `0017`.

## Do Not Move Yet

- Do not move `analysis/capabilities/*.yaml`; the matrix endpoint reads that
  directory today.
- Do not move `meta/harness/golden_path.md`, `TODO.md`, or
  `HANDOFF-NEXT-SESSION.md`; they are active proof execution docs.
- Do not move `meta/DDC_MAPPING.md` or `meta/ITWIN_MAPPING.md`; they are
  top-level integration maps referenced by the whole system.
- Do not move untracked `3d_assets/` in this pass; it is outside the current
  capability-research boundary.
