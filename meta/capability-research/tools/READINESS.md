# Graph Tool Readiness

Date: 2026-05-13
Status: InfraNodus first pass complete, Graphify and GitNexus bounded proofs complete, repo-wide runs still gated

This document defines the order and prerequisites for using InfraNodus,
Graphify, and GitNexus on the LATTICE capability research corpus.

## Readiness Summary

| Tool | Current stance | Why |
|---|---|---|
| InfraNodus | First curated-doc gap analysis complete | Output exists at `meta/capability-research/tools/infranodus-gap-analysis-2026-05-13.md` |
| Graphify | Bounded proof complete, not ready for repo-wide run | Output exists at `meta/capability-research/inventory/graphify/2026-05-13-bounded-proof.md`; root `graphify-out/` is live, but broader promotion and output relocation are still unsettled |
| GitNexus | Bounded proof complete, not ready for repo-wide run | Output exists at `meta/capability-research/inventory/gitnexus/2026-05-13-bounded-proof.md`; scoped index is real, but query/FTS health still needs follow-up |

See `../inventory/local-graph-tool-audit.md` for the PixelTable-volume audit,
`../inventory/corpus-manifest.yaml` for the first allowed input corpus, and
`output-manifest.md` for allowed output paths.

The local InfraNodus skill source audit is:

```text
meta/capability-research/tools/infranodus-skills-master-audit.md
```

Use it before activating anything under `.claude/skills/skills-master/`.

First gap-analysis output:

```text
meta/capability-research/tools/infranodus-gap-analysis-2026-05-13.md
```

## InfraNodus First Pass

Use InfraNodus to find conceptual and organizational gaps in the curated docs,
not to index every file in the repo.

Inputs:

```text
AGENTS.md
meta/ARCHITECTURE.md
meta/SCHEMA.md
meta/API.md
meta/capability-research/ARCHITECTURE.md
meta/capability-research/INVENTORY.md
meta/capability-research/census/repo-census-001.md
meta/capability-research/census/repo-census-002-ui-transfer.md
meta/capability-research/census/repo-census-003-vectorworks.md
meta/capability-research/census/repo-census-004-odbc.md
meta/harness/golden_path.md
meta/harness/TODO.md
meta/harness/docs/capability-lifecycle.md
meta/DDC_MAPPING.md
meta/ITWIN_MAPPING.md
```

Recommended tools:

| InfraNodus tool | Use |
|---|---|
| `generate_knowledge_graph` or `analyze_text` | Structural overview of the combined corpus |
| `generate_content_gaps` | Find missing bridges between concepts |
| `generate_research_questions` | Produce planning questions from gaps |
| `difference_between_texts` | Compare capability architecture against TODO/harness execution docs |
| `optimize_text_structure` or `develop_text_tool` | Suggest doc reorganization |

Allowed output location:

```text
meta/capability-research/tools/infranodus-gap-analysis-YYYY-MM-DD.md
meta/capability-research/inventory/infranodus-gap-analysis-YYYY-MM-DD.json
```

Do not store API keys, tokens, or `.env*` files in the repo.

## Graphify Readiness

Graphify should wait until these exist:

| Required item | Target |
|---|---|
| Corpus manifest | `meta/capability-research/inventory/corpus-manifest.yaml` |
| Output manifest | `meta/capability-research/tools/output-manifest.md` |
| Ignore rules | Exclude `node_modules`, `dist`, `.git`, runtime caches, screenshots, local assets unless explicitly included |
| First run scope | Docs-only subset under `meta/capability-research/`, `meta/ARCHITECTURE.md`, `meta/SCHEMA.md`, `meta/API.md` |
| Evidence rule | Output path must be cited by a harness proof artifact before any capability promotion |

Proof and output locations:

```text
meta/capability-research/inventory/graphify/
meta/harness/docs/sessions/<date>-graphify-proof.md
```

Do not run Graphify over the full repo until the docs-only run has a clean
artifact and the output path is stable.

Prior local lesson: MARPA 918 Juniper produced a `graphify-out` with 1746 nodes,
3489 edges, and 70 communities from a 386-file, nearly one-million-word corpus.
That was useful but too broad as a first LATTICE step. LATTICE should start with
curated docs and only expand after the output manifest is stable.

## GitNexus Readiness

GitNexus should wait until:

| Required item | Target |
|---|---|
| Code boundary manifest | Defines `pixeltable/service/**`, `src/**`, `scripts/**`, `vw-plugin/**`, and excludes generated/vendor dirs |
| Runtime versus research distinction | Prevents docs-only research from being treated as code dependency graph |
| Existing registry reconciliation | `gitnexus-capability-registry.yaml` no longer claims missing generated paths as active proof |
| First run scope | Small code subset, ideally harness route + UI client + one verifier script |

Proof and output locations:

```text
meta/capability-research/inventory/gitnexus/
meta/harness/docs/sessions/<date>-gitnexus-proof.md
```

Do not use GitNexus output for refactor decisions until a small known subset
has been indexed and verified.

Prior local lesson: MARPA Platform has an existing GitNexus index with 119101
symbols and 136561 edges. That proves GitNexus can handle large repos here, but
it also shows why LATTICE needs explicit include/exclude boundaries before
running `gitnexus analyze`.

## Registry Reconciliation Needed

The existing capability registries for graph tools are useful as harvested
intent, but not all rows are proven-ready in the current repo state.

| Registry | Readiness gap |
|---|---|
| `analysis/capabilities/infranodus-capability-registry.yaml` | Several `wired_at` entries reference `analysis/infranodus/*`, which does not exist yet |
| `analysis/capabilities/gitnexus-capability-registry.yaml` | Repo-local MCP and scoped index are real, but some ACTIVE rows still overclaim search/impact health and older hook shapes |
| `analysis/capabilities/graphify-parisgroup-capability-registry.yaml` | Current installed CLI does not match several harvested rows (`graphify run`, MCP surfaces, generated slash-command paths) |
| `analysis/capabilities/graphify-safishamsi-capability-registry.yaml` | Mentions tutorial ingestion paths that need a deterministic proof fixture |

Do not change these rows to proven until each has a verifier-backed artifact.

## Smallest Next Execution Slice

Run InfraNodus against the curated docs list and write one gap-analysis artifact
to `meta/capability-research/tools/`. The verifier should check:

1. The artifact exists.
2. It includes conceptual gaps.
3. It includes folder/organization gaps.
4. It includes a P0/P1/P2 task list.
5. It does not include secrets.
6. It does not promote any capability row.

That proof makes the first graph-analysis tool real without committing the repo
to a Graphify or GitNexus indexing layout too early.
