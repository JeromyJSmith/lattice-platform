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
**Issue prefix:** `MARPA-XX` (all platform and engagement issues use MARPA team, free-plan constraint)

---

## Agent lanes — who does what

Lane labels dispatch work to the best-fit agent and identify stewardship. They
do not create exclusive file-path jurisdiction, except for the hard prohibitions
listed below.

| Agent | Branch prefix | What it stewards |
|---|---|---|
| **Codex CLI** | `codex/` | `pixeltable/migrations/` (new only), `pixeltable/service/`, `src/server/runtime/`, `src/routes/`, `scripts/*.py` |
| **Claude Code** | `claude/` | Multi-file refactors ≥3 dirs, `.claude/rules/`, `.claude/skills/`, `analysis/capabilities/`, `CLAUDE.md`, `AGENTS.md` |
| **GitHub Copilot** | `copilot/` | `.github/`, `scripts/*.sh`, `meta/*.md` (single-file) |
| **Warp PI** | `warp-pi/` | Shell scripts, `uv` ops, Phase B M3 Max bootstrap |
| **Hermes** | `hermes/` | `meta/harness/docs/`, `analysis/`, research/synthesis |
| **Human only** | `human/` | Secrets, OAuth, merges to main, deletions, Linear milestone changes |

Before picking up a Linear issue, confirm it has your lane label. If another lane's label is set, stop.

Hard prohibitions survive the stewardship model: migrations are write-once
(`pixeltable/migrations/0001`-`0016` cannot be edited), secrets and `.env*`
files are human-only, branch protection and merges to `main` are human-only,
and deletions of migrations, issues, or branches are human-only. Changes under
`.claude/rules/` must be the explicit purpose of the PR, not incidental drift.

---

## If you are Codex — read this section carefully

### Your stewardship

**Stewarded paths:**
- `pixeltable/migrations/*.py` — **new files only** (write-once rule — see below)
- `pixeltable/service/**` — FastAPI sidecar services, workers, ingest
- `src/server/runtime/**` — TanStack server functions
- `src/routes/**` — new route files only
- `scripts/*.py` — Python utility scripts

**Prohibited (stop immediately if the task requires these):**
- Editing any file in `pixeltable/migrations/` that already exists
- Touching `.claude/rules/`, `.claude/skills/` unless the PR is explicitly a doctrine/skill change
- Touching `.github/workflows/` (Copilot lane)
- Architectural decisions not already in `meta/ARCHITECTURE.md`

### Label guard — run this check first

Check your Linear issue's labels. If `codex` is not present:
1. Post a workpad comment: "Skipping — not labeled `codex`. Returning to Todo."
2. Move issue back to **Todo** via `linear_graphql`.
3. Stop. Make no file changes.

---

## Non-negotiable code rules

### 1. Pixeltable geometry — no exceptions

```python
# CORRECT — always pxt.String with WKT or GeoJSON
centroid = pxt.String   # stores "POINT(-105.2705 40.0150)"

# WRONG — pxt.Geometry does not exist in Pixeltable 0.6.x — runtime crash
centroid = pxt.Geometry  # ← NEVER write this
```

### 2. Write-once migrations

- Migrations 0001–0016 are **immutable**. Never edit, rename, or delete them.
- **Next migration number: 0017**
- File format: `pixeltable/migrations/0017_<description>.py`
- Always use helpers, never raw Pixeltable create calls:

```python
from pixeltable.migrations._helpers import (
    ensure_namespace, ensure_table, ensure_column, OWNED_PARENTS
)
# If creating a new top-level namespace, add it to OWNED_PARENTS first
```

### 3. When you add a migration — update all four files in the same commit

- `meta/SCHEMA.md` — table reference + migration trail entry
- `meta/ARCHITECTURE.md` — schema overview + verified-state header
- `CLAUDE.md` (repo root) — LIVE STATE block migration count
- `meta/HANDOFF.md` — current-state header

CI (`docs-sync-check.yml`) will block the PR if these drift.

### 4. When you add an endpoint — update both files in the same commit

- `meta/API.md` — endpoint table (current count: 33)
- `meta/ARCHITECTURE.md` — FastAPI surface table + endpoint count

### 5. Python: uv only

```bash
uv run python script.py    # run scripts
uv add package             # add dependency
uv sync                    # sync environment

# NEVER: pip install / pip3 / conda / poetry / pipenv
```

### 6. iTwin: OSS only

```ts
// ALLOWED — open-source iTwin geometry and BIS vocabulary
import { Point3d, Transform } from "@itwin/core-geometry";
import { Code, ElementProps } from "@itwin/core-common";

// FORBIDDEN — these pull in the SQLite persistence layer
import { IModelHost } from "@itwin/core-backend";  // ← NEVER
import { SnapshotDb } from "@itwin/core-backend";   // ← NEVER
import { BriefcaseDb } from "@itwin/core-backend";  // ← NEVER
```

Commercial Bentley tiers (BDN, iTwin Activate, Partner Program) are gated under
`meta/harness/docs/research/_gated/bentley-commercial/` and dormant by default.
Never architect against them.

### 7. No Anthropic SDK in client code

```ts
// WRONG — never import Anthropic SDK in .ts/.tsx client files
import Anthropic from "@anthropic-ai/sdk";

// RIGHT — use TanStack AI adapters or server functions only
import { useAIStream } from "@tanstack/ai";
```

### 8. All coordinates EPSG-normalised before Pixeltable write

Never write raw Vectorworks internal coordinates to any Pixeltable table.
Always normalize through `ifcopenshell.util.placement` or PDAL reprojection first.

### 9. No comments unless the WHY is non-obvious

Default: write zero comments. Add one line only when there is a hidden constraint,
a workaround for a specific external bug, or behavior that would surprise a reader.
Never explain WHAT the code does — well-named identifiers do that.

---

## Mandatory pre-commit check

Before **every** `git commit`, run:

```bash
bash scripts/pre-commit-docs-check.sh
```

If it fails, fix the docs/counts first. Do not commit until it passes.
`docs-sync-check.yml` CI enforces the same check and will block your PR if skipped.

---

## Branch and PR format

**Branch:** `codex/marpa-<NNN>-<2-4-word-slug>`
Example: `codex/marpa-47-0017-scene-graph-embeddings`

**PR title:** `[MARPA-NNN] type(scope): description`
- type: `feat` | `fix` | `chore` | `refactor` | `test`
- scope: `migration` | `service` | `routes` | `scripts`
- Example: `[MARPA-47] feat(migration): 0017_scene_graph_embeddings`

**PR base branch:** `feature/phase-c-linear` (not main — never main)

**Magic Words in PR body:**
- `Closes MARPA-NNN` → closes the Linear issue on merge
- `Refs MARPA-NNN` → links without closing

**PR template:** `.github/PULL_REQUEST_TEMPLATE.md` — it auto-populates.
Fill in the Linear issue field and check `codex` in the Agent Lane section.

**CI that must pass before marking Done:**
- `docs-sync-check` — migration/endpoint counts, forbidden strings
- `linear-sync-check` — PR title format `[MARPA-NNN]`

---

## Linear workpad pattern (Symphony mode)

When running under Symphony orchestration, maintain exactly **one** persistent
comment on the issue throughout your entire work session.

- **Create** it with `commentCreate` on your first turn
- **Update** it with `commentUpdate` (never create additional comments)

Required sections in the workpad comment:

```
## Plan
[What you are doing and why]

## Acceptance Criteria
[How you will verify completion]

## Progress
[Current step — what's done, what's next]

## Confusions / Blockers
[Anything needing human input — stop and surface these immediately]
```

---

## Canonical reference files — read before writing any code

| File | Contents |
|---|---|
| `meta/ARCHITECTURE.md` | System overview, namespace map, FastAPI surface, iTwin tier map |
| `meta/SCHEMA.md` | Pixeltable table reference and migration trail (source of truth for migration numbers) |
| `meta/API.md` | FastAPI endpoint table (update when adding routes) |
| `meta/agent-lanes.md` | Full lane definitions, collision prevention, quality gates |
| `meta/sync-contract.md` | Linear ↔ GitHub field directions, Magic Words, PR title convention |
| `.github/copilot-instructions.md` | Full cardinal rules 1–24 (authoritative for all agents) |
| `.github/agent-context.md` | Flat snapshot of locked stack + cardinal rules (use when meta/ tree is unavailable) |

If the task requires an architectural decision not covered by these files,
post a blocker comment on the Linear issue and move it back to Todo.
Do not invent architecture.

---

## What LATTICE is NOT

Do not propose or implement any of the following — they violate cardinal rules:

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
curl -s http://localhost:8001/health    # FastAPI sidecar (start if not running)
git status                              # confirm clean working tree
git fetch origin                        # sync with remote
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
