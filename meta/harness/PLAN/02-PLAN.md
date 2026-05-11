<!-- spec-verified: code.claude.com/docs 2026-05-11 -->
# Phase 2 — Plan

## Strategic shape

The Meta-Harness build is **eight discrete execution phases**, each landing as one squash-merge-able commit on `feature/meta-harness`. Every phase has a verifiable exit criterion. Phases run in order; later phases depend on earlier ones.

| # | Phase | Lands | Verifiable exit |
|---|---|---|---|
| 0 | Planning artifacts (this PR) | `meta/harness/PLAN/00-04.md` | All 5 planning docs committed; draft PR opened |
| 1 | KG Triad install + config | `graphify.toml`, `.mcp.json` additions, `.env.example` update, `.claude/skills/generated/.gitkeep` | `graphify run` produces `meta/harness/graph-reports/`; InfraNodus MCP registered in `.mcp.json`; GitNexus indexes the repo |
| 2 | Migration 0014 (harness schema) | `pixeltable/migrations/0014_harness_schema.py`, `_helpers.py` adds `lattice/harness` to `OWNED_PARENTS`, `meta/SCHEMA.md` + `meta/ARCHITECTURE.md` + root `CLAUDE.md` count bump 13→14, 36→40 | `make migrate-dryrun` clean; `make migrate` applied; `pxt.list_tables('lattice/harness')` returns 4 |
| 3 | FastAPI harness routes | `pixeltable/service/routes/harness.py` (7 endpoints), `main.py` registers, `meta/API.md` count 33→40 | `curl /healthz` 200; new endpoints discoverable via `/openapi.json` |
| 4 | Global Meta-Harness scaffold | `meta/harness/GLOBAL_HARNESS.md`, `domain_spec.md`, `evaluation/`, `evolution/`, `memory/`, `bootstrap/` (incl. `env-snapshot.py`, `graph-snapshot.sh`, `health-report.py`, `run-autoresearch.sh`), `memory/constraint-registry.md` | Files exist; `constraint-registry.md` lists all 9+ rule IDs; `bash meta/harness/bootstrap/health-report.py` returns valid JSON (scores may be 0) |
| 5 | Per-section filesystem refactor (the big one) | 8 sections × 4 files = 32 new MD files (`CLAUDE.md` / `AGENTS.md` / `MEMORY.md` / `GOAL.md`) + 8 scoring scripts + 8 `iterations.jsonl` (empty arrays) | All 32 MD files committed; `bash scripts/score-global.sh` returns composite baseline; new docs-sync Job 7 passes |
| 6 | `.claude/` system files (spec-compliant) | `.claude/settings.json` (hooks), `.claude/rules/*.md`, `.claude/skills/lattice-*/SKILL.md` (11 skills), `.claude/agents/*-harness.md` (9 agents incl. global), `.claude/skills/generated/.gitkeep` | All SKILL.md files have valid frontmatter; all agent files have `name`+`description`; new docs-sync Job 8 (spec-compliance) passes |
| 7 | docs-sync-check.yml expansion | New Jobs 7 (harness-schema-check), 8 (spec-compliance), 9 (goal-md-completeness) | All 9 jobs pass on the PR HEAD |
| 8 | PR finalization | Update PR description with file count + diffstat; mark ready for review; create the 12 follow-up GitHub issues from the original prompt; add to project board | PR ready; 12 issues created on `meta-harness` label |

## File inventory (by phase)

### Phase 1 — KG Triad

| File | Action | Reason |
|---|---|---|
| `graphify.toml` | new | Per-section project config from amendment |
| `.mcp.json` | edit | Add `infranodus`, `gitnexus`, `graphify` MCP servers |
| `.env.example` | edit | Add `INFRANODUS_API_KEY=` (commented placeholder) |
| `meta/harness/graph-reports/.gitkeep` | new | Output directory for Graphify runs |
| `.claude/skills/generated/.gitkeep` | new | Output directory for GitNexus auto-generated skills |
| `meta/harness/bootstrap/graph-snapshot.sh` | new (placeholder) | Will be fleshed out in Phase 4 |

### Phase 2 — Migration 0014

| File | Action |
|---|---|
| `pixeltable/migrations/0014_harness_schema.py` | new (write-once) |
| `pixeltable/migrations/_helpers.py` | edit (add `lattice/harness` to `OWNED_PARENTS`) |
| `meta/SCHEMA.md` | edit (table count 36→40; add `lattice/harness/*` block; migration trail 0001–0014) |
| `meta/ARCHITECTURE.md` | edit (table count, schema overview, last-verified line) |
| `CLAUDE.md` (repo root) | edit (LIVE STATE block: 0001–0014, 40 tables) |
| `../CLAUDE.md` (parent dir) | edit (same LIVE STATE block) |
| `meta/HANDOFF.md` | edit (current-state header) |

### Phase 3 — FastAPI surface

| File | Action |
|---|---|
| `pixeltable/service/routes/harness.py` | new (7 endpoints) |
| `pixeltable/service/main.py` | edit (register router) |
| `meta/API.md` | edit (endpoint count 33→40; new section) |
| `meta/ARCHITECTURE.md` | edit (endpoint count, routes block) |

### Phase 4 — Global Meta-Harness scaffold

| File | Action |
|---|---|
| `meta/harness/GLOBAL_HARNESS.md` | new |
| `meta/harness/domain_spec.md` | new |
| `meta/harness/bootstrap/env-snapshot.py` | new |
| `meta/harness/bootstrap/graph-snapshot.sh` | flesh out |
| `meta/harness/bootstrap/health-report.py` | new |
| `meta/harness/bootstrap/run-autoresearch.sh` | new |
| `meta/harness/bootstrap/update-memory.sh` | new (called by `Stop` hook) |
| `meta/harness/bootstrap/update-session-memory.sh` | new (same) |
| `meta/harness/bootstrap/detect-section.sh` | new (called by `PostToolUse` hook) |
| `meta/harness/evaluation/eval-suite.py` | new |
| `meta/harness/evaluation/acceptance-criteria.md` | new |
| `meta/harness/evolution/proposal-ledger.json` | new (`[]`) |
| `meta/harness/evolution/candidate-store/.gitkeep` | new |
| `meta/harness/evolution/evidence/.gitkeep` | new |
| `meta/harness/memory/constraint-registry.md` | new |
| `meta/harness/memory/global-graph.json` | new (`{}` placeholder) |
| `meta/harness/memory/session-log.md` | new (header only) |
| `meta/harness/sections/{schema,api,frontend,georef-reality,genai,vw-itwin,ddc-infra}/HARNESS.md` | new (7 files) |
| `meta/harness/sections/<section>/eval.py` | new (7 files) |
| `meta/harness/sections/<section>/skill.md` | new (7 files; pointer to `.claude/skills/lattice-<section>/SKILL.md`) |
| `meta/harness/sections/<section>/graph-config.json` | new (7 files) |

### Phase 5 — Filesystem refactor (per-section context stacks)

8 sections, each gets `CLAUDE.md` + `AGENTS.md` + `MEMORY.md` + `GOAL.md`:

| Section root | Notes |
|---|---|
| `pixeltable/` | Schema |
| `pixeltable/service/` | API |
| `src/` | Frontend |
| `georef/` + `reality/` (paired) | Georef/Reality — one stack at `georef/`, `reality/CLAUDE.md` imports it |
| `genai/` + `assets/` (paired) | GenAI/Assets |
| `vw-plugin/` + `vw-python/` + `itwin/` (triad) | VW Bridge — one stack at `vw-plugin/`, others import it |
| `ddc/` | DDC |
| `.github/` | CI/Infra |

**Pairing rule:** when two adjacent dirs belong to one section, the canonical stack lives in the alphabetically-first dir; the others' `CLAUDE.md` is a one-liner `@../<canonical>/CLAUDE.md`. This avoids 4× duplication.

Scoring scripts: `scripts/score-{schema,api,frontend,georef,genai,vw-itwin,ddc,ci,global}.sh` — 9 total.

Iterations logs: `<section-root>/iterations.jsonl` — 8 total, each starts as empty file.

### Phase 6 — `.claude/` architecture

Per the spec-verified structure in `01-RESEARCH.md`:

```
.claude/
├── settings.json                ← project hooks + permissions (committed)
├── rules/
│   ├── global-cardinal-rules.md (no paths: → loads at launch)
│   ├── migrations.md            (paths: pixeltable/migrations/*.py)
│   ├── frontend.md              (paths: src/**/*.{ts,tsx})
│   ├── vw-plugin.md             (paths: vw-plugin/**/*.{cpp,h,py})
│   ├── georef.md                (paths: georef/**/*.py, reality/**/*.py)
│   └── ci-workflows.md          (paths: .github/workflows/*.yml)
├── skills/
│   ├── lattice-global/SKILL.md
│   ├── lattice-schema/SKILL.md
│   ├── lattice-api/SKILL.md
│   ├── lattice-frontend/SKILL.md
│   ├── lattice-georef/SKILL.md
│   ├── lattice-genai/SKILL.md
│   ├── lattice-vw-itwin/SKILL.md
│   ├── lattice-ddc/SKILL.md
│   ├── lattice-ci/SKILL.md
│   ├── lattice-autoresearch/SKILL.md   (disable-model-invocation: true)
│   ├── lattice-goal-md/SKILL.md
│   └── generated/.gitkeep
└── agents/
    ├── global-meta-harness.md
    ├── schema-harness.md
    ├── api-harness.md
    ├── frontend-harness.md
    ├── georef-harness.md
    ├── genai-harness.md
    ├── vw-itwin-harness.md
    ├── ddc-harness.md
    └── ci-harness.md
```

All 11 SKILL.md and all 9 agent files MUST carry valid YAML frontmatter per `01-RESEARCH.md` §A/§B.

### Phase 7 — docs-sync-check expansion

| Job | Adds |
|---|---|
| Job 7 (harness-schema-check) | Verify `meta/harness/{GLOBAL_HARNESS,domain_spec}.md` exist; all 7 sections present under `sections/`; `constraint-registry.md` lists 9+ rule IDs |
| Job 8 (spec-compliance) | Verify SKILL.md frontmatter present; verify agent files have `name` + `description`; verify CLAUDE.md files do NOT have frontmatter; verify hooks NOT in prose .md outside agent/skill files; verify skill directory structure |
| Job 9 (goal-md-completeness) | Verify GOAL.md exists in all 8 section roots; verify required headers (`## Fitness Function`, `## Improvement Loop`, `## Action Catalog`, `## Operating Mode`); verify referenced scoring script exists; verify MEMORY.md required headers |

### Phase 8 — PR finalization

12 issues to create (per amendment + original prompt):

1. Install and configure Graphify — `infra`, `meta-harness`
2. Install and configure GitNexus — `infra`, `meta-harness`
3. Configure InfraNodus MCP — `infra`, `meta-harness`
4. Implement `health-report.py` — `meta-harness`
5. Implement `eval-suite.py` — `meta-harness`
6. Wire harness health endpoint to Runtime Console UI — `meta-harness`, `frontend`
7. Run first Meta-Harness evolution loop (schema section) — `meta-harness`, `schema`
8. Write scoring scripts for all 8 sections — `meta-harness`
9. Establish baseline scores — `meta-harness`
10. Run first autoresearch loop on API section — `meta-harness`, `api`
11. Run first autoresearch loop on DDC section — `meta-harness`, `ddc`
12. Get InfraNodus API key + add to local `.env` — `infra`, `meta-harness`

Plus new label: `meta-harness` (color `#8B5CF6`).

## Dependency graph

```
Phase 0 (this PR)
    ↓
Phase 1 (KG Triad — installable, no internal deps)
    ↓
Phase 2 (Migration 0014) ───┐
    ↓                       │
Phase 3 (FastAPI routes)    │
    ↓                       │
Phase 4 (Global scaffold)   │
    ↓                       │
Phase 5 (Filesystem refactor) ← biggest commit
    ↓
Phase 6 (.claude/ architecture)
    ↓
Phase 7 (docs-sync expansion)
    ↓
Phase 8 (PR finalization)
```

Each phase is one squash-able commit. CI runs on every push.

## Time + risk estimate

| Phase | Risk | Files | Notes |
|---|---|---|---|
| 1 | Low | ~5 | External tool installs may need user approval (Graphify install.sh) |
| 2 | Medium | ~6 | Migration applied to live Pixeltable — `make migrate-dryrun` first |
| 3 | Low | ~3 | Stub endpoints, standard pattern |
| 4 | Medium | ~18 | Lots of scaffolding; mostly stubs |
| 5 | **High** | ~40 | Largest commit. Bulk of writing. |
| 6 | Medium | ~20 | Every file must pass spec validation |
| 7 | Low | 1 | YAML edits to existing workflow |
| 8 | Low | 0 (just GH ops) | gh issue create + PR ready |

Total new + edited files across all phases: **~93**.

## Rollback strategy

Per phase: `git reset --hard <prev-commit>` (we are on a feature branch).
Full rollback: delete branch (`git branch -D feature/meta-harness && git push origin --delete feature/meta-harness`).
Migration 0014 rollback: never edit a landed migration; if Phase 2 lands and we need to undo, add migration 0015 to drop the new tables and update docs.

## Checkpoints requiring user input

| When | Decision |
|---|---|
| End of Phase 0 (now) | Approve plan; proceed to Phase 1 or revise |
| Before Phase 1 | Confirm willingness to install Graphify + GitNexus + InfraNodus MCP |
| Before Phase 2 | Confirm Pixeltable backup state; OK to run `make migrate` |
| Before Phase 5 | Approve the per-section file pattern (lots of new MDs) |
| After Phase 8 | Review PR; merge or request changes |
