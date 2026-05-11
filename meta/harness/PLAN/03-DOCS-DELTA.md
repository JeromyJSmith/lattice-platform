<!-- spec-verified: code.claude.com/docs 2026-05-11 -->
# Phase 3 — Docs Delta

> **AMENDED 2026-05-11** — see [`05-RESEARCH-AMENDMENT.md`](05-RESEARCH-AMENDMENT.md) § "Updated file count" (93 → 109 files). The new files listed in the amendment append to the inventories below.

Existing documentation that requires update + new documentation to be created during execution. This is a delta map, not the edits themselves — execution writes the edits.

## Existing docs requiring edits

### Root-level

| File | Phase | Edit summary |
|---|---|---|
| `CLAUDE.md` (repo root) | 2 | Bump LIVE STATE: migrations `0001-0014`, tables `40`. Add "Meta-Harness Architecture" section: what it is + the 8-section ownership table + `bash meta/harness/bootstrap/graph-snapshot.sh` activation line + 3-line evolution loop summary. |
| `CLAUDE.md` (parent dir) | 2 | Same LIVE STATE bump. |
| `AGENTS.md` | 5 | Append "Section Ownership Map" table mapping each section root to its owning agent and conflict-resolution rule. |
| `CONTRIBUTING.md` | 6 | Add "Section context stacks" subsection explaining the `CLAUDE.md` + `AGENTS.md` + `MEMORY.md` + `GOAL.md` pattern; add "Autoresearch loop" subsection with the invocation. |
| `.cursorrules` | 6 | Add reference to `.claude/rules/` system; list Meta-Harness section roots. |

### `meta/` docs

| File | Phase | Edit summary |
|---|---|---|
| `meta/SCHEMA.md` | 2 | Tables 36→40; migration trail 0001–0014; add `lattice/harness/*` subsection (4 tables: `health_snapshots`, `harness_proposals`, `section_events`, `global_decisions`). |
| `meta/ARCHITECTURE.md` | 2, 3 | Tables count 36→40; endpoint count 33→40; last-verified line; add `lattice/harness/*` to schema tree; add `/v1/harness/*` to FastAPI surface; add a new §7b "Meta-Harness Layer" referencing `meta/harness/`. |
| `meta/API.md` | 3 | Endpoint count 33→40; add `/v1/harness` router section (7 endpoints). |
| `meta/HANDOFF.md` | 2, 5 | Live-state header bump; add SCHEMA/API doc links to harness sections; add new "Per-section context stacks" subsection. |
| `meta/AGENT_ONBOARDING.md` | 4, 5 | Add "Knowledge Graph Triad" section (Graphify / GitNexus / InfraNodus — what each does, when to use, MCP tool names); add "Section context stack" pattern explanation; bump 33→40 endpoint count; add §10 "Meta-Harness activation" with bootstrap command. |
| `meta/ROADMAP.md` | 2, 5 | Phase 1 DoD: add "Meta-Harness scaffold complete" item; Phase 2 DoD: add "Per-section autoresearch loops baseline-scored" item. |
| `meta/FEATURE_BACKLOG.md` | 8 | Add new section header `## META-HARNESS` with the 12 follow-up issues listed under it. |

### CI workflows

| File | Phase | Edit summary |
|---|---|---|
| `.github/workflows/docs-sync-check.yml` | 7 | Add Job 7 (harness-schema-check), Job 8 (spec-compliance), Job 9 (goal-md-completeness). All gated by `workflow_call` so `ci.yml` continues to depend on them. |
| `.github/workflows/ci.yml` | 7 | No edit if `needs: [docs-sync-check]` already covers the new jobs via reusable workflow call. |

## New docs to be created

### Planning artifacts (this PR — Phase 0)

- `meta/harness/PLAN/00-OVERVIEW.md` ✅
- `meta/harness/PLAN/01-RESEARCH.md` ✅
- `meta/harness/PLAN/02-PLAN.md` ✅
- `meta/harness/PLAN/03-DOCS-DELTA.md` ← this file ✅
- `meta/harness/PLAN/04-EXECUTION-HANDOFF.md` ← next

### Global Meta-Harness (Phase 4)

| File | Purpose |
|---|---|
| `meta/harness/GLOBAL_HARNESS.md` | Master instruction file for the Global Meta-Harness proposer agent |
| `meta/harness/domain_spec.md` | Stanford ONBOARDING-format domain spec |
| `meta/harness/evaluation/acceptance-criteria.md` | What "good" means per section |
| `meta/harness/memory/constraint-registry.md` | All 9+ cardinal rules in machine-readable YAML form |
| `meta/harness/memory/session-log.md` | Append-only header |

### Section harnesses (Phase 4 — `meta/harness/sections/`)

7 sections × 2 docs = 14 files: `HARNESS.md` + `skill.md` per section. (`eval.py` and `graph-config.json` are code/JSON, not docs.)

### Per-section filesystem stacks (Phase 5)

8 sections × 4 files = **32 new MD files**:

| Section root | Files |
|---|---|
| `pixeltable/` | `CLAUDE.md` `AGENTS.md` `MEMORY.md` `GOAL.md` |
| `pixeltable/service/` | same 4 |
| `src/` | same 4 |
| `georef/` | same 4 (`reality/CLAUDE.md` = one-line import) |
| `genai/` | same 4 (`assets/CLAUDE.md` = one-line import) |
| `vw-plugin/` | same 4 (`vw-python/CLAUDE.md`, `itwin/CLAUDE.md` = one-line imports) |
| `ddc/` | same 4 |
| `.github/` | same 4 |

Plus the import-pointer files: `reality/CLAUDE.md`, `assets/CLAUDE.md`, `vw-python/CLAUDE.md`, `itwin/CLAUDE.md` (4 files).

### `.claude/` system files (Phase 6)

Per `02-PLAN.md` § Phase 6 file inventory:

- 6 rule files in `.claude/rules/`
- 11 SKILL.md files in `.claude/skills/lattice-*/`
- 9 subagent files in `.claude/agents/`
- 1 `.claude/settings.json` (JSON, not MD; with hooks)

## Forbidden-strings allowlist additions

When the per-section context stacks land (Phase 5), several files will reference forbidden strings as guardrail text (e.g. `pixeltable/CLAUDE.md` will mention "never use `pxt.Geometry`"). The current allowlist in `docs-sync-check.yml` covers `meta/`, `.github/workflows/docs-sync-check.yml`, `scripts/pre-commit-docs-check.sh`, `CLAUDE.md`, `AGENTS.md`, `README.md`, `CONTRIBUTING.md`, `.cursorrules`.

**Phase 7 will extend the allowlist** to cover:
- `**/CLAUDE.md` (all section CLAUDE.md files, not just root)
- `**/AGENTS.md`
- `**/MEMORY.md`
- `**/GOAL.md`
- `meta/harness/**`
- `.claude/rules/**`
- `.claude/skills/**/SKILL.md`
- `.claude/agents/**`

Without this allowlist extension, Phase 5/6 commits will fail CI.

## Amendment additions (per `05-RESEARCH-AMENDMENT.md`)

| File | Action | Phase |
|---|---|---|
| `schemas/desire-record.schema.yaml` | CREATE | 4 |
| `schemas/improvement-goal.schema.yaml` | CREATE | 4 |
| `analysis/desires/.gitkeep` | CREATE | 4 |
| `analysis/infranodus/README.md` | CREATE | 4 |
| `analysis/infranodus/desires.graph.json` | CREATE (`{}`) | 4 |
| `analysis/infranodus/goals.graph.json` | CREATE (`{}`) | 4 |
| `analysis/infranodus/failures.graph.json` | CREATE (`{}`) | 4 |
| `analysis/infranodus/goal-vs-implementation.diff.json` | CREATE (`{}`) | 4 |
| `analysis/gaps/README.md` | CREATE | 4 |
| `analysis/gaps/<section>-gap-report.md` × 8 | CREATE (stub) | 4 |
| `meta/harness/bootstrap/build-gap-analysis.py` | CREATE (stub) | 4 |
| `gold_goals.md` (repo root) | CREATE | 4 |
| `<section-root>/gold_goals.md` × 8 | CREATE | 5 |
| `.claude/rules/infranodus-corpus.md` | CREATE | 6 |

Plus: MARPA-specific findings F1–F10 (per `05-RESEARCH-AMENDMENT.md`) are folded into:
- Phase 5 GenAI/Assets section CLAUDE.md (Landscape Semantic Sidecar + CityGML 3.0 ADE alignment)
- Phase 5 Frontend section CLAUDE.md (DrawAPI mandatory abstraction; deck.gl Tile3DLayer/TerrainExtension preferred path)
- Phase 5 VW-iTwin section CLAUDE.md (Cesium acquisition risk; generic CameraState; web-ifc for Prototype 1)
- Phase 5 DDC section GOAL.md action catalog (12 adaptable skills + 3 new modules: LA-ETL/LA-ECO/LA-IRR)
- Phase 5 vw-plugin section CLAUDE.md (VS 2022 v17.12 + Xcode 16.2 prerequisites; satellite credentials note; `ObjectExample` starting point)

## Spec-verified comment convention

Every new system file (SKILL.md, agent file, rule file) carries this comment as the first non-frontmatter line:

```html
<!-- spec-verified: code.claude.com/docs 2026-05-11 -->
```

JSON files (`settings.json`) can't host HTML comments; instead add a `"_spec_source"` key at the top level (to be stripped before any production hardening pass).

This is a LATTICE-internal convention (not a Claude Code spec requirement). It exists so reviewers can grep for un-verified files: `grep -rL "spec-verified:" .claude/skills/`.
