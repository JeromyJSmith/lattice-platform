<!-- spec-verified: code.claude.com/docs + docs.github.com 2026-05-11 -->
# LATTICE Agent Lanes

Agent lanes prevent collision and make agent output attributable. Each agent
owns a branch prefix, a Linear label, a file-path scope, and a strength profile.
An agent MUST NOT push to a branch outside its prefix or touch files outside its
scope without an explicit human override recorded in the PR body.

Reference: `meta/sync-contract.md` for branch naming and PR title conventions.

---

## Lane table

| Agent | Branch prefix | Linear label | File-path scope | Strength profile |
|---|---|---|---|---|
| GitHub Copilot | `copilot/` | `copilot` | `.github/`, `scripts/`, `meta/`, workflow YAML | Web-task completion, GitHub API, CodeQL self-fix, PR descriptions, issue triage, single-file edits |
| Claude Code | `claude/` | `claude-code` | `pixeltable/`, `.claude/rules/`, `.claude/skills/`, `analysis/capabilities/`, multi-file refactors touching ≥3 files | Long-context reasoning, doctrine implementation, capability registries, CLAUDE.md / AGENTS.md maintenance, TanStack + sidecar integration |
| Codex CLI | `codex/` | `codex` | `pixeltable/migrations/`, `pixeltable/service/`, `src/server/`, Python module scaffolding | Heavy code generation, migration authoring, Python-heavy tasks, schema-first implementations |
| Warp Terminal PI | `warp-pi/` | `warp-pi` | `scripts/`, bootstrap shell scripts, Phase B M3 Max ops | Terminal-bound ops, `uv` runs, embeddings pipelines, shell-level diagnostics, Phase B M3 Max bootstrap |
| Hermes | `hermes/` | `hermes` | `meta/harness/docs/`, `analysis/`, `ddc/`, capability harvests | Research and analysis, doc-mirror sync, InfraNodus graph analysis, DDC skills indexing, knowledge-substrate harvest |
| Human only | `human/` | `human-only` | Secrets, `.env*`, OAuth flows, branch protection, merge to `main`, milestone changes, any deletion | Any action requiring credentials, irreversibility, or cross-team coordination |

---

## Lane definitions

### GitHub Copilot (`copilot/`)

**Strength:** GitHub-native tasks. Copilot excels at tasks that live entirely in
the GitHub surface — PR descriptions, issue triage, `.github/workflows/*.yml`
edits, CODEOWNERS, single-file script edits, CodeQL auto-fix suggestions.

**Allowed paths:**
- `.github/**`
- `scripts/*.sh`, `scripts/*.py`, `scripts/*.ts` (single-file edits only)
- `meta/*.md` (single-file updates)
- `meta/harness/PLAN/*.md` (amendments — single file)

**Branch prefix:** `copilot/LAT-XX-slug`

**Prohibited:**
- Multi-file refactors spanning more than one directory
- Anything touching `pixeltable/migrations/` (schema is Codex lane)
- Anything touching `.claude/rules/` (doctrine is Claude Code lane)
- Merges to `main` or `feature/meta-harness`

**Quality gate:** PR must pass `linear-sync-check` + `docs-sync-check`.

---

### Claude Code (`claude/`)

**Strength:** Multi-file reasoning, doctrine implementation, long-context
architectural work. Claude Code owns anything that requires understanding the
full system state across files.

**Allowed paths:**
- `pixeltable/**` (except `pixeltable/migrations/` — Codex lane)
- `.claude/rules/**`
- `.claude/skills/**`
- `analysis/capabilities/**`
- `src/**` (full frontend + server)
- Any multi-file refactor touching ≥3 files in different directories
- `CLAUDE.md`, `AGENTS.md`, `meta/AGENT_ONBOARDING.md`

**Branch prefix:** `claude/LAT-XX-slug`

**Prohibited:**
- Writing raw VW internal coordinates to any file
- Importing `@itwin/core-backend` anywhere
- Using `pip`, `conda`, `poetry`, `pipenv` in any script

**Quality gate:** Must run `bash scripts/pre-commit-docs-check.sh` before every
commit. PR must pass `docs-sync-check` + `linear-sync-check`.

---

### Codex CLI (`codex/`)

**Strength:** Code generation from spec. Codex is fastest at producing new Python
modules, migrations, and server routes from a precise spec. It does not have
long conversational memory — every Codex task must be self-contained.

**Allowed paths:**
- `pixeltable/migrations/*.py` (new files only; never edit existing)
- `pixeltable/service/**`
- `src/server/runtime/**`
- `src/routes/**` (new route files)
- Python utility scripts in `scripts/`

**Branch prefix:** `codex/LAT-XX-slug`

**Prohibited:**
- Editing existing migrations (write-once rule)
- Touching `.claude/rules/` or `.claude/skills/`
- Any architectural decision that is not already spec'd in `meta/ARCHITECTURE.md`

**Quality gate:** `pixeltable.yml` CI must pass. `schema-verify.yml` must pass.

---

### Warp Terminal PI (`warp-pi/`)

**Strength:** Terminal-native operations. PI agent runs inside Warp's terminal
and excels at shell-level work — `uv` syncs, embeddings batch jobs, PDAL
pipelines, bootstrap sequences, and anything that needs to be observed live
in a terminal.

**Allowed paths:**
- `scripts/**` (shell scripts, Python scripts, TS scripts)
- Phase B M3 Max bootstrap operations (no code write — ops only)
- `runtime-runs/<run-id>/` (write-only; never read other agents' run dirs)

**Branch prefix:** `warp-pi/LAT-XX-slug`

**Prohibited:**
- Writing to `pixeltable/migrations/` (schema is Codex lane)
- Touching `.claude/` (doctrine is Claude Code lane)
- Any action that requires GitHub API access (use Copilot lane)

**Quality gate:** `test-pxt.yml` must pass after any Pixeltable-touching op.

---

### Hermes (`hermes/`)

**Strength:** Research, synthesis, and knowledge graph construction. Hermes runs
InfraNodus, aggregates doc-mirror content, synthesises capability harvests, and
maintains the knowledge substrate in `meta/harness/docs/`.

**Allowed paths:**
- `meta/harness/docs/**`
- `analysis/**`
- `ddc/**`
- `scripts/ingest-*.py`, `scripts/sync-doc-mirrors.sh`, `scripts/detect-doc-gaps.py`

**Branch prefix:** `hermes/LAT-XX-slug`

**Prohibited:**
- Writing code to `src/` or `pixeltable/` (implementation is other lanes)
- Touching `.claude/rules/` (doctrine is Claude Code lane)
- Any destructive file operation

**Quality gate:** `docs-sync-check.yml` nine-section-meta-harness job must pass.

---

### Human Only (`human/`)

Some actions cannot and must not be delegated to agents. These require human
hands on keyboard with full credential access and deliberate intent.

**Actions:**
- Merging any PR to `main` or `feature/meta-harness`
- Enabling or modifying branch protection rules
- Creating or rotating secrets (`gh secret set …`)
- Approving OAuth application access
- Activating any `_gated/` vendor gate
- Deleting files, branches, or issues
- Changing Linear milestone dates or reordering milestones
- Any action inside `.env.local` or other credential files
- Approving agent PRs (a human must click Merge)
- Triggering the Linear bulk import (Stage 5a)
- Reviewing the reconciliation CSV before committing label/milestone changes (Stage 5b)

**Branch prefix:** `human/LAT-XX-slug` (rare; used for human-authored commits that
don't fit an agent lane, e.g., credential rotation documentation)

**Linear label:** `human-only` — no agent may self-assign an issue with this label.

---

## Collision prevention

1. **One issue, one lane.** Before picking up a Linear issue, the agent sets its
   lane label and moves the issue to In Progress. If the issue already has a
   lane label from another agent, stop and ping `#lattice-sync`.

2. **Branch isolation.** Each agent works on its own branch. Branches are merged
   to `feature/phase-c-linear` (or the active integration branch) via PR, never
   by direct push.

3. **File-path scope is hard.** If a task genuinely requires touching files in
   two different lanes, the human assigns two sub-issues — one per lane — and
   the PRs are merged in dependency order.

4. **`linear-sync-check.yml` enforces prefix.** Every PR's branch name is
   validated against the lane table. A PR from `copilot/` that touches
   `pixeltable/migrations/` fails CI.

---

## Agent quality scoreboard (Phase C+)

The GitHub Insights view **Agent Activity** (built in Stage 8) tracks per-lane:
- PRs opened / merged / closed-unmerged
- Average time in review
- `docs-sync-check` pass rate
- `linear-sync-check` pass rate

This is visible to all contributors and is the primary signal for lane calibration.

---

_Last updated: 2026-05-11. Owned by: LATTICE team lead. Mirrors: Linear › Lattice project › Description._
