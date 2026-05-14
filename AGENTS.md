# LATTICE Platform — Agent Instructions
# Read by: Codex CLI (every session), GitHub Copilot, Cursor, any AI agent
# Keep under 32 KiB — Codex truncates silently above project_doc_max_bytes

---

## Project identity

LATTICE is an AI-native landscape-architecture digital twin:

**Pipeline:** Vectorworks 2026 → IFC4.3 → iTwin OSS BIS/geometry (self-hosted) →
deck.gl + Cesium 3D Tiles → Pixeltable knowledge substrate

**Repo:** https://github.com/JeromyJSmith/lattice-platform
**Active branch:** `feature/phase-c-linear` (integration branch — PRs target this, not main)
**Linear board:** https://linear.app/00-command-center/project/lattice-fa64d0d31078
**Issue prefix:** `MARPA-XX` (all platform and engagement issues use MARPA team)

Any capable coding agent can pick up any open issue. Attribution is by Linear
comment and PR author, not by file-path jurisdiction.

---

## Hard prohibitions (apply to every agent, no exceptions)

Any capable coding agent can pick up any open issue in any part of the codebase.
No model has exclusive ownership of any file or directory — every agent is
responsible for everything. Attribution is by Linear comment and PR author.

The only things no agent — human or AI — may do without an explicit, separate
human decision:

1. **Edit a landed migration.** Migrations `pixeltable/migrations/0001`–`0016`
   are immutable. To change schema, add the next sequential file (next = `0017`).
2. **Touch secrets, `.env*`, or OAuth credentials.** Always human.
3. **Modify branch protection rules.** Always human.
4. **Merge to `main`.** Always human.
5. **Delete migrations, branches, or Linear issues.** Always human.
6. **Change `.claude/rules/` doctrine files as a side-effect.** Doctrine changes
   are the explicit point of a PR or they don't happen.

Everything else — any file, any directory — is in scope for any agent that
picks up the issue. Migrations are write-once, secrets and `.env*` are human-only,
branch protection and merges to `main` are human-only, deletions are human-only.
Changes under `.claude/rules/` must be the explicit purpose of the PR.

---

## Non-negotiable code rules

### 1. Pixeltable geometry

```python
# CORRECT
centroid = pxt.String   # stores "POINT(-105.2705 40.0150)"

# WRONG — pxt.Geometry does not exist in Pixeltable 0.6.x — runtime crash
centroid = pxt.Geometry
```

### 2. Write-once migrations

- Migrations `0001`–`0016` are immutable.
- **Next migration number: `0017`**
- File format: `pixeltable/migrations/0017_<description>.py`
- Always use the helpers — never raw `pxt.create_*`:

```python
from pixeltable.migrations._helpers import (
    ensure_namespace, ensure_table, ensure_column, OWNED_PARENTS
)
# New top-level namespace? Add it to OWNED_PARENTS first.
```

### 3. When you add a migration — update all four files in the same commit

- `meta/SCHEMA.md` — table reference + migration trail entry
- `meta/ARCHITECTURE.md` — schema overview + verified-state header
- `CLAUDE.md` (repo root) — LIVE STATE block migration count
- `meta/HANDOFF.md` — current-state header

`docs-sync-check.yml` will block the PR if these drift.

### 4. When you add an endpoint — update both files in the same commit

- `meta/API.md` — endpoint table (current count: 33)
- `meta/ARCHITECTURE.md` — FastAPI surface table + endpoint count

### 5. Python: uv only

```bash
uv run python script.py
uv add package
uv sync

# NEVER: pip / pip3 / conda / poetry / pipenv
```

### 6. iTwin: OSS only

```ts
// ALLOWED
import { Point3d, Transform } from "@itwin/core-geometry";
import { Code, ElementProps } from "@itwin/core-common";

// FORBIDDEN — pulls in the SQLite persistence layer
import { IModelHost, SnapshotDb, BriefcaseDb } from "@itwin/core-backend";
```

Commercial Bentley tiers (BDN, iTwin Activate, Partner Program) are gated under
`meta/harness/docs/research/_gated/bentley-commercial/` and dormant by default.

### 7. No Anthropic SDK in client code

```ts
// WRONG — never in .ts/.tsx client files
import Anthropic from "@anthropic-ai/sdk";

// RIGHT — TanStack AI adapters or server functions only
import { useAIStream } from "@tanstack/ai";
```

### 8. All coordinates EPSG-normalised before Pixeltable write

Never write raw Vectorworks internal coordinates. Normalize through
`ifcopenshell.util.placement` or PDAL reprojection first.

### 9. No comments unless the WHY is non-obvious

Default: write zero comments. Add one only when there is a hidden constraint,
a workaround for a specific external bug, or behavior that would surprise a
reader. Never explain WHAT the code does.

---

## Mandatory pre-commit check

Before **every** `git commit`:

```bash
bash scripts/pre-commit-docs-check.sh
```

If it fails, fix the docs/counts first. `docs-sync-check.yml` CI enforces the
same check and will block the PR.

---

## Branch and PR format

**Branch:** `<type>/marpa-<NNN>-<2-4-word-slug>`
where `<type>` is `feat`, `fix`, `chore`, `refactor`, or `test`.
Example: `feat/marpa-47-0017-scene-graph-embeddings`

**PR title:** `[MARPA-NNN] type(scope): description`
- type: `feat` | `fix` | `chore` | `refactor` | `test`
- scope: `migration` | `service` | `routes` | `scripts` | `docs` | `ci`
- Example: `[MARPA-47] feat(migration): 0017_scene_graph_embeddings`

**PR base branch:** `feature/phase-c-linear` (never `main`)

**Magic Words in PR body:**
- `Closes MARPA-NNN` → closes the Linear issue on merge
- `Refs MARPA-NNN` → links without closing

**PR template:** `.github/PULL_REQUEST_TEMPLATE.md` auto-populates. Fill in the
Linear issue number.

**CI that must pass before marking Done:**
- `docs-sync-check` — migration/endpoint counts, forbidden strings
- `linear-sync-check` — PR title format `[MARPA-NNN]`

---

## Linear workpad pattern

When working an issue, maintain exactly **one** persistent comment on the
Linear issue throughout your work session.

- **Create** it with `commentCreate` on your first turn
- **Update** it with `commentUpdate` on every subsequent turn — never create
  additional comments

Required sections:

```
## Plan
[What you are doing and why]

## Acceptance Criteria
[How you will verify completion]

## Progress
[Current step — what's done, what's next]

## Confusions / Blockers
[Anything needing human input — surface immediately, don't bury]
```

---

## Canonical reference files — read before writing any code

| File | Contents |
|---|---|
| `meta/ARCHITECTURE.md` | System overview, namespace map, FastAPI surface, iTwin tier map |
| `meta/SCHEMA.md` | Pixeltable table reference and migration trail (source of truth for migration numbers) |
| `meta/API.md` | FastAPI endpoint table (update when adding routes) |
| `meta/sync-contract.md` | Linear ↔ GitHub field directions, Magic Words, PR title convention |
| `.github/copilot-instructions.md` | Full cardinal rules (authoritative) |
| `.github/agent-context.md` | Flat snapshot of locked stack + cardinal rules (use when meta/ tree is unavailable) |

If the task requires an architectural decision not covered by these files,
post a blocker comment on the Linear issue and move it back to Todo. Do not
invent architecture.

---

## What LATTICE is NOT

Do not propose or implement any of the following:

- Revit, MicroStation, DGN, or `.rvt` file handling
- `@itwin/core-backend`, `SnapshotDb`, `BriefcaseDb`, `IModelHost`
- `pxt.Geometry` anywhere in migration files
- Any Bentley cloud-hosted API (iTwin SaaS, BDN, Activate cohort) unless a gate has fired
- Cesium ion paid endpoints unless Gate E has fired
- `pip install` / `conda install` / `poetry add` for Python deps
- SQLite, PostgreSQL, or Redis as a primary store — Pixeltable only
- Raw Vectorworks internal coordinates written to Pixeltable
- Anthropic SDK imported in `.ts` or `.tsx` client files
- Editing an existing migration file

---

## Session start checklist

Before substantive work, verify:

```bash
curl -s http://localhost:8001/health    # FastAPI sidecar
git status                              # clean tree
git fetch origin                        # sync remote
```

If the sidecar is not running:

```bash
cd pixeltable/service
PIXELTABLE_HOME=/Volumes/PixelTable/.pixeltable \
PYTHONPATH=/Volumes/PixelTable/schemas \
uv run python main.py &
```

---

## Tech stack quick reference

| Layer | Choice | Version |
|---|---|---|
| JS runtime | Bun | latest |
| Frontend | TanStack Start + React 19 + Vite 8 | — |
| State/data | TanStack Query + TanStack DB | — |
| Sidecar | FastAPI + uvicorn + asyncio | pixeltable==0.6.x |
| Python env | uv | only tool allowed |
| 3D engine | @thatopen/components + Three.js | 3.4.6 / 0.184 |
| Analytics | deck.gl + DuckDB WASM + MapLibre | 9.3.2 / 1.33.1 / 5 |
| iTwin | @itwin/core-geometry + @itwin/core-common | 5.9.2 |
| Point cloud | Laspy + PDAL + Open3D + PotreeConverter | — |
| IFC | IfcOpenShell | — |
| Agent runtime | claude -p CLI subprocess (Claude Max) | — |
| Orchestration | Symphony + Codex CLI (codex app-server) | 0.130.0 |
| Issue tracker | Linear / MARPA team | MARPA-XX prefix |

---

## graphify

This repo uses the `graphifyy` package, which installs the `graphify` CLI.

- `graphify update .` refreshes the local AST graph in `graphify-out/`
- `graphify extract .` runs the full semantic pass when the required API key is present
- `.mcp.json` launches the stdio MCP server through `scripts/run-graphify-mcp.sh`
- After code changes in this session, refresh `graphify-out/` before relying on graph answers

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **lattice-platform-scoped** (9468 symbols, 11983 relationships, 110 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/lattice-platform-scoped/context` | Codebase overview, check index freshness |
| `gitnexus://repo/lattice-platform-scoped/clusters` | All functional areas |
| `gitnexus://repo/lattice-platform-scoped/processes` | All execution flows |
| `gitnexus://repo/lattice-platform-scoped/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
