<!-- spec-verified: code.claude.com/docs 2026-05-11 -->
# Phase 4 — Execution Handoff

> **AMENDED 2026-05-11.** Before executing any phase, read [`05-RESEARCH-AMENDMENT.md`](05-RESEARCH-AMENDMENT.md) end-to-end. It carries:
> - The DesireRecord / ImprovementGoal / gold_goals.md verbatim templates from `meta-harness-artifacts.md`
> - 13 new Phase-4 files + 8 new Phase-5 files + 1 new Phase-6 file
> - MARPA-specific findings F1–F10 that constrain Phase 5 section CLAUDE.md authoring
> - 4 additional GitHub follow-up issues (Phase 8 total: 12 → 16)
> - The corrected `GOAL.md` template (below) that integrates InfraNodus + gold_goals + ranked-gap-report reads

This document is the **self-contained handoff** for whichever agent executes the Meta-Harness build. Read top-to-bottom once before doing anything. No external context required.

## You are picking up

A planned-but-not-executed Meta-Harness build for LATTICE. Branch `feature/meta-harness` already exists with the four planning artifacts (`meta/harness/PLAN/00-04.md`). Draft PR may already be open.

Your job: execute **Phases 1–8** from [`02-PLAN.md`](02-PLAN.md). One squash-commit per phase, pushed to `feature/meta-harness`, with the verifiable exit criterion green before moving on.

## Hard prerequisites

Before your first tool call:

1. **You are on `feature/meta-harness`.** Verify with `git branch --show-current`. If not, `git checkout feature/meta-harness && git pull --ff-only`.
2. **Local doc systems are present.** Verify `ls /Users/ojeromyo/.claude-code-docs/docs/ | wc -l` > 100 and `ls /Users/ojeromyo/.vectorworks-docs/docs/` not empty.
3. **No file written from memory.** Every system file (`SKILL.md`, agent `.md`, `.claude/settings.json`, `.claude/rules/*.md`) MUST be spec-verified against the local doc files before creation. The verified frontmatter tables live in [`01-RESEARCH.md`](01-RESEARCH.md).
4. **Pre-commit hook installed.** Run `ln -sf ../../scripts/pre-commit-docs-check.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit` if not already.
5. **Existing CI passes on the branch head.** `gh run list --branch feature/meta-harness --limit 1` should show success.

If any prerequisite is false, STOP and ask the human.

## Execution rules

- **One phase = one commit.** Do not interleave changes from multiple phases.
- **CI must be green before the next phase.** After every push: `gh run list --branch feature/meta-harness --limit 1` — wait for completion, fix failures inline.
- **Never edit a landed migration.** Migration 0014 in Phase 2 is write-once; if you find a bug after it lands, write migration 0015.
- **Never push to `main`.** This branch only. PR merges happen via review.
- **Never disable a CI job to make the build pass.** Fix the root cause.
- **Spec-verified comment on every system file.** First non-frontmatter line: `<!-- spec-verified: code.claude.com/docs 2026-05-11 -->` (update date when re-verified).
- **Forbidden-strings allowlist must be extended in Phase 7**, not earlier. Phase 5/6 commits will fail CI without it — that is acceptable signal; do not bypass with `--no-verify`. Land Phase 7 immediately after Phase 6.
- **No autonomous loops.** The autoresearch loop (`run-autoresearch.sh`) is created in Phase 4 but NOT executed in this PR. Human approves first run.

## Phase-by-phase execution playbook

### Phase 1 — KG Triad install

```bash
# Graphify
curl -fsSL https://raw.githubusercontent.com/parisgroup-ai/graphify/main/install.sh | sh
graphify init                     # creates graphify.toml — overwrite with the LATTICE config from 02-PLAN.md
graphify install-integrations --project-local
graphify run                      # baseline analysis → meta/harness/graph-reports/

# GitNexus
npm install -g gitnexus
gitnexus analyze --skills         # populates .claude/skills/generated/
gitnexus setup

# InfraNodus MCP (no install — adds to .mcp.json)
# Edit .mcp.json to add the infranodus stanza
# Document INFRANODUS_API_KEY in .env.example (do NOT commit a real key)
```

Commit: `feat(harness): install KG Triad — Graphify + GitNexus + InfraNodus MCP`

Verify: `graphify run` produces `meta/harness/graph-reports/analysis.json`; `.mcp.json` contains `infranodus`; CI green.

### Phase 2 — Migration 0014

```bash
# Edit pixeltable/migrations/_helpers.py: add "lattice/harness" to OWNED_PARENTS
# Write pixeltable/migrations/0014_harness_schema.py per the spec in original prompt
# Tables: health_snapshots, harness_proposals, section_events, global_decisions

cd pixeltable
make migrate-dryrun               # MUST be clean
# Inspect output. If clean:
make migrate                      # applies to live Pixeltable
# Verify:
PIXELTABLE_HOME=/Volumes/PixelTable/.pixeltable uv run python -c "import pixeltable as pxt; print(sorted(pxt.list_tables('lattice/harness')))"
# Expected: ['lattice/harness/global_decisions', 'lattice/harness/harness_proposals', 'lattice/harness/health_snapshots', 'lattice/harness/section_events']
```

Edit `meta/SCHEMA.md`, `meta/ARCHITECTURE.md`, root `CLAUDE.md`, parent `CLAUDE.md`, `meta/HANDOFF.md` — bump counts (13→14 migrations, 36→40 tables).

Commit: `feat(harness): migration 0014 — lattice/harness namespace + 4 tables`

Verify: `pxt.list_tables` shows the 4 new tables; docs-sync passes locally; CI green.

### Phase 3 — FastAPI harness routes

Create `pixeltable/service/routes/harness.py` with 7 endpoints (spec in original prompt §STEP 4). Register in `main.py`. Update `meta/API.md` and `meta/ARCHITECTURE.md` (33→40 endpoints).

Commit: `feat(harness): /v1/harness/* — 7 endpoints (health, proposals, events)`

Verify: sidecar restart; `curl 127.0.0.1:8765/v1/harness/health` returns 200 or 501 (stubs OK); CI green.

### Phase 4 — Global Meta-Harness scaffold

Create everything listed in [`02-PLAN.md`](02-PLAN.md) § Phase 4 file inventory. The key files:

- `meta/harness/GLOBAL_HARNESS.md` — spec from original prompt §STEP 2
- `meta/harness/memory/constraint-registry.md` — all 9 rules from amendment §"ADD TO constraint-registry.md"
- `meta/harness/bootstrap/*.sh` and `*.py` — start as runnable stubs that exit 0 and emit valid JSON/text; full implementations are tracked in follow-up issues

Commit: `feat(harness): Global Meta-Harness scaffold (bootstrap + evaluation + memory + 7 sections)`

Verify: `bash meta/harness/bootstrap/health-report.py 2>&1 | python -m json.tool` succeeds; `constraint-registry.md` greppable for all 9 rule IDs.

### Phase 5 — Filesystem refactor (biggest commit)

For each of the 8 section roots in [`02-PLAN.md`](02-PLAN.md) § Phase 5: create the 4-file context stack (`CLAUDE.md` + `AGENTS.md` + `MEMORY.md` + `GOAL.md`). For paired roots (`reality/`, `assets/`, `vw-python/`, `itwin/`), the secondary's `CLAUDE.md` is a one-liner `@../<canonical>/CLAUDE.md`.

Write scoring scripts in `scripts/score-<section>.sh` — pure bash, < 3s, output `score: N/100` plus breakdown. Plus `scripts/score-global.sh` (weighted average).

Initialize each `<section>/iterations.jsonl` as an empty file.

Update `AGENTS.md` (root) with the Section Ownership Map. Update root `CLAUDE.md` with the Meta-Harness section (architecture pointer + 8-section table + activation line).

Commit: `feat(harness): per-section context stacks (32 MD files + 9 scoring scripts)`

Verify: every section root has 4 MD files; `bash scripts/score-global.sh` returns a composite (baseline likely 0–20); CI may fail on no-forbidden-strings (expected — Phase 7 fixes).

### Phase 6 — `.claude/` architecture

Per [`02-PLAN.md`](02-PLAN.md) § Phase 6 + [`01-RESEARCH.md`](01-RESEARCH.md) §A–F. Every SKILL.md gets YAML frontmatter (at minimum `description`). Every agent file gets YAML frontmatter with `name` + `description` minimum. CLAUDE.md files in `.claude/` itself are plain markdown (no frontmatter).

`.claude/settings.json` carries the 5 hooks from amendment §"The LATTICE-specific hooks":
1. `Bash(git commit*)` → `bash scripts/pre-commit-docs-check.sh`
2. `Write` (PreToolUse) → `bash scripts/check-forbidden-strings.sh "$CLAUDE_TOOL_INPUT_FILE_PATH"`
3. `Write` (PostToolUse) → `bash meta/harness/bootstrap/detect-section.sh "$CLAUDE_TOOL_INPUT_FILE_PATH"`
4. `Stop` → `bash meta/harness/bootstrap/update-session-memory.sh`
5. `InstructionsLoaded` → log to `meta/harness/memory/session-log.md`

Hook scripts (`check-forbidden-strings.sh`, `detect-section.sh`, `update-session-memory.sh`) must be created in `scripts/` and made executable.

Commit: `feat(harness): .claude/ system files — 11 skills + 9 agents + 6 rules + settings.json`

Verify: `find .claude/skills -name SKILL.md | head | xargs -I{} head -1 {}` shows `---` for every file; `find .claude/agents -name '*.md' -exec grep -L '^name:' {} +` returns nothing.

### Phase 7 — docs-sync-check expansion

Add Jobs 7, 8, 9 to `.github/workflows/docs-sync-check.yml`. Extend allowlist regex in the `no-forbidden-strings` job to cover the new section CLAUDE.md / AGENTS.md / MEMORY.md / GOAL.md paths, `meta/harness/**`, `.claude/rules/**`, `.claude/skills/**/SKILL.md`, `.claude/agents/**`.

Commit: `ci(harness): docs-sync-check — add Jobs 7-9 (harness-schema, spec-compliance, goal-md)`

Verify: all 8 jobs green on PR head.

### Phase 8 — PR finalization

```bash
gh pr ready
gh label create meta-harness --color "8B5CF6" --description "Meta-Harness work"
# Create the 12 issues from 02-PLAN.md § Phase 8 list, add to project board 4
```

Update PR description with: file count, diffstat, list of new GitHub issues, link to `meta/harness/PLAN/`.

## Failure modes to expect

| Symptom | Diagnosis | Action |
|---|---|---|
| `make migrate-dryrun` shows unexpected drops | Migration script touches a non-owned namespace | Re-check `_helpers.py::OWNED_PARENTS`; never let dryrun pass with drops |
| docs-sync-check fails on Phase 5 | Allowlist regex doesn't cover new file paths | Land Phase 7 immediately; do NOT bypass |
| Graphify install hangs | Network or permissions | Stop; ask human |
| GitNexus `analyze` OOMs | Repo too large for default | Use `gitnexus analyze --exclude pixeltable/.pixeltable --exclude node_modules` |
| InfraNodus MCP returns 401 | Missing `INFRANODUS_API_KEY` in env | Confirm `.env` has the real key (gitignored); never commit |
| Subagent file rejected at session restart | Missing `name` or `description` frontmatter field | Fix file; restart |
| SKILL.md not loading | No frontmatter or directory shape wrong | Verify against `01-RESEARCH.md` §A |

## What to NOT do (footguns)

- Do NOT enable autoresearch loops in this PR. The script exists; activation is a separate decision.
- Do NOT modify branch protection on `main` from this PR. Branch protection edits are out of scope.
- Do NOT add new MCP servers beyond Graphify + GitNexus + InfraNodus without a separate issue.
- Do NOT commit any API key, even in templates. `.env.example` is the only place secrets-shaped strings appear (as empty values).
- Do NOT delete existing migrations or rename existing tables. Write 0014; everything else is additive.
- Do NOT skip the pre-commit hook with `--no-verify`. If it fails, fix the docs.

## Amended GOAL.md template (replaces the version implied by prior prompts)

Use this template verbatim when creating every section `GOAL.md` in Phase 5. The header sections (`## Fitness Function`, `## Improvement Loop`, `## Action Catalog`, `## Operating Mode`) are required by `docs-sync-check.yml` Job 9.

```markdown
# GOAL — <section name>

<!-- spec-verified: code.claude.com/docs 2026-05-11 -->

## Fitness Function
- Primary metric: output of scripts/score-<section>.sh
- Baseline: <N>/100
- Target plateau: <N>/100
- Composite formula: weighted average of section-specific components (see scoring script)

## Required guardrails
- Must-not-regress constraints from meta/harness/memory/constraint-registry.md
- CONSTRAINT_ID_1: <description>

## Improvement Loop
1. Read <section-root>/gold_goals.md for current winning criteria
2. Read analysis/infranodus/goals.graph.json for structural gaps (optimize=gaps mode first)
3. Consult analysis/gaps/<section>-gap-report.md for ranked improvement candidates
4. Propose ONE harness change (prompting, memory, tool wiring, retrieval logic)
5. Run scoring script — accept only if score improves AND no guardrail fails
6. Write result to <section-root>/iterations.jsonl
7. If stuck for 3+ iterations → switch InfraNodus mode to optimize=reinforce

## Action Catalog
- Modify own CLAUDE.md / MEMORY.md context
- Propose schema migrations (draft only — human approves before make migrate)
- Update gold_goals.md when a new plateau is reached
- Create GitHub issues for improvements requiring human decision
- Append to analysis/gaps/<section>-gap-report.md

## Operating Mode
infranodus_mode: gaps
last_score: 0
last_run: never
iterations_completed: 0
plateau_detected: false
```

## Amended Phase 8 issue list (12 → 16)

The original 12 + these 4:

13. **Implement DesireRecord intake pipeline** — `analysis/desires/` + intake script mining from GitHub issues, MEMORY.md files, session logs. Labels: `meta-harness`, `schema`
14. **Run InfraNodus gap analysis on initial desire corpus** — populate `analysis/infranodus/desires.graph.json`. Labels: `meta-harness`, `infranodus`
15. **Implement AGORA ImprovementGoal decomposition for schema section** — model first 3 ImprovementGoals from desires using AGORA 3-layer. Labels: `meta-harness`, `schema`
16. **Build gap analysis tool (`build-gap-analysis.py`)** — full impl of dependency-integrated gap ranking. Labels: `meta-harness`

Plus new label: `infranodus` (color `#10B981`) alongside `meta-harness` (color `#8B5CF6`).

## When you finish

1. PR description finalised
2. All 8 phases committed, CI green
3. 12 follow-up issues created and on board
4. `meta/harness/PLAN/05-EXECUTION-NOTES.md` written: one paragraph per phase covering "what actually happened vs the plan", deviations, surprises, and what the next executor (autoresearch loop human reviewer) needs to know.
5. Comment on PR: `@<reviewer> ready for review`

Then stop. The autoresearch loop is a separate decision the human makes after reviewing the PR.
