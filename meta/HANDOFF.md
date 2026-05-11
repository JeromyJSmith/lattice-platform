# LATTICE Agent Handoff

This document is the **one place** every AI agent platform working on LATTICE should start. Read it top-to-bottom once; afterwards you can jump to the platform-specific section you need.

---

## What LATTICE is

LATTICE is a local-first AEC digital-twin platform for landscape architecture: **Vectorworks → IFC4.3 → Pixeltable → operator console (TanStack Start) → three rendering contexts (ThatOpen 3D + deck.gl analytical + Cesium globe) → Cinema 4D handoff.** Real agents (Claude via `claude -p` subprocess) write back into Pixeltable as runs stream.

The whole platform fits on one Apple Silicon Mac. There is no cloud database, no Bentley iModelHub, no hosted GenAI for the default agent path. Costs are bounded by the operator's Claude Max subscription and electricity.

See [`AGENTS.md`](../AGENTS.md) for the project-level invariants, [`meta/ROADMAP.md`](ROADMAP.md) for the phased build order, [`meta/ARCHITECTURE.md`](ARCHITECTURE.md) for the data flow + stack table.

---

## The 30-second universal handoff

Every agent, regardless of platform, follows this loop:

1. **Boot the stack locally.**
   ```bash
   cd pixeltable && make sidecar-up-tcp   # terminal 1
   bun run dev                            # terminal 2 (repo root)
   curl http://127.0.0.1:7770/healthz     # should return {"ok":true,...}
   curl -I http://localhost:3000/runtime  # should return 200
   ```

2. **Find work.** Filter open issues by `is:open label:agent-ready` plus the area label that matches your specialty (`data-layer`, `3d-viewer`, `genai`, `vw-bridge`, `cesium`, `ddc`, `postgis`, `3d-assets`, `agent-runtime`, `operator-console`, etc.).

3. **Pick up the issue.** Read the acceptance criteria. Create a branch:
   ```bash
   git checkout -b agent/<issue-number>-<short-slug>
   ```

4. **Do the work.** Match the conventions in neighbouring files. Run `make test-no-pxt` before pushing. If you touched `pixeltable/`, also run `make test-pxt`. If you touched `src/`, run `bun run build`.

5. **Open a PR.** The `agent-pr-review.yml` workflow auto-comments with a classification: files changed, affected areas, suggested checks.

6. **Respect the cardinal rules** ([§ Cardinal rules](#cardinal-rules) below). PRs that violate them don't merge.

---

## Where to read first

| Document | Why |
|---|---|
| [`AGENTS.md`](../AGENTS.md) (root) | Project-level rules, locked stack versions, MetaHarness boundaries |
| [`CLAUDE.md`](../CLAUDE.md) (root) | User-level conventions (uv, no-optional, security guardrails) |
| [`meta/AGENT_ONBOARDING.md`](AGENT_ONBOARDING.md) | The 5-minute boot + current priority queue |
| [`meta/ROADMAP.md`](ROADMAP.md) | What phase we're in, what's gating what |
| [`meta/ARCHITECTURE.md`](ARCHITECTURE.md) | Stack table, data flow, MCP topology, Pixeltable schema overview |
| [`meta/FEATURE_BACKLOG.md`](FEATURE_BACKLOG.md) | Single source of truth for queued work |
| [`meta/ITWIN_MAPPING.md`](ITWIN_MAPPING.md) | Which iTwin packages we use (and which we never install) |
| [`meta/DDC_MAPPING.md`](DDC_MAPPING.md) | DDC integration plan (cost, BOQ, n8n patterns) |
| [`meta/CESIUM_SETUP.md`](CESIUM_SETUP.md) | Cesium ion vs self-hosted; coordinate bridge contract |
| [`meta/WORKTREES.md`](WORKTREES.md) | The 6 long-lived feature worktrees and how to switch between them |
| [`CONTRIBUTING.md`](../CONTRIBUTING.md) | Branch naming, commit format, test workflow |

---

## Platform-specific handoffs

The general handoff above applies to everyone. Below is the additional context each platform needs.

### Claude Code (`claude` CLI in this repo)

Claude Code is the canonical interactive agent for LATTICE — it's the runtime the worker uses, and it's what the operator uses for ad-hoc tasks at the terminal.

- **Auto-loaded instructions:** [`CLAUDE.md`](../CLAUDE.md) (user-global) plus the project-level `CLAUDE.md` files in `meta/`, `pixeltable/`, and inside specific worktrees.
- **Persistent memory:** lives at `~/.claude/projects/-Volumes-PixelTable-VW-iTWIN-Bridge/memory/` — relevant patterns (sidecar wiring, streaming pipeline, SSE, TanStack quirks) are already saved there.
- **Worktree usage:** see [`meta/WORKTREES.md`](WORKTREES.md). Open a separate Claude Code session per worktree if you want isolation. Branches like `feature/3d-viewer` live at `../lattice-worktrees/feature-3d-viewer`.
- **Tooling:** `Bash`, `Read`, `Write`, `Edit` are the day-to-day workhorses. Use `Agent` (with `subagent_type: "Explore"`) for broad codebase search rather than firing multiple `grep`s.
- **Skills:** invoke `/<skill-name>` to load a project skill (see [`skills/`](../skills/) and `~/.claude/skills/`).
- **What you must never touch from the CLI:** the `marpa/*` Pixeltable tree (other body owns it); files under `.git/objects/`; `pixeltable/.pixeltable/` runtime state.

### `claude -p` (non-interactive, used by the worker)

The LATTICE worker (`pixeltable/service/worker.py::_claude_cli_chunks`) shells out to:

```bash
claude -p --output-format stream-json --verbose --include-partial-messages \
  --system-prompt "<LATTICE prompt>" "<task>"
```

Three flags are mandatory and non-obvious:
- `--output-format stream-json` — JSONL output instead of plain text
- `--verbose` — required by the CLI when stream-json is set under `-p`
- `--include-partial-messages` — the actual token-streaming switch

If you're scripting LATTICE from outside the worker, use the same shape. Don't reach for the Anthropic SDK — it's deliberately not a dependency.

### GitHub Copilot

[`.github/copilot-instructions.md`](../.github/copilot-instructions.md) is the workspace instruction file. It lists the locked stack, the cardinal rules, and the style preferences. Copilot reads it automatically when you open the workspace.

Key Copilot-specific notes:
- Don't propose `@itwin/core-backend` or any Anthropic SDK import — Copilot's defaults will sometimes suggest these.
- Code style: no comments unless WHY is non-obvious; prefer edits over new files.
- Test-first: if Copilot proposes a feature, the matching test under `pixeltable/tests/` or `src/**/*.test.ts` is part of the same change.

### OpenAI Codex / Codex CLI

[`codex.md`](../codex.md) at the repo root is the canonical Codex instruction file. Same locked stack, same cardinal rules as Copilot, formatted for Codex.

Useful Codex patterns for LATTICE:
- Independent diff review: `codex review` against a feature branch before opening a PR.
- Challenge mode: pose Codex an adversarial question about a design (e.g., "what's wrong with this geometry bridge?") — useful for catching subtle bugs in `itwin/geometry/geo-transform.ts`.

### Cloudflare Workers agents

[`cloudflare-agent.md`](../cloudflare-agent.md) at the repo root describes the boundary precisely. Quick summary:

| Worker can handle | Worker cannot handle |
|---|---|
| Edge API routes (webhooks, relay) | Pixeltable writes |
| Linear ↔ GitHub sync (`linear-sync.yml`-style) | `claude -p` (local CLI auth) |
| Auth proxy / token rotation | IfcOpenShell parsing |
| R2-served Parquet + Potree tiles | VW C++ plugin / `vwx-mcp` |
| Cron-scheduled digest emails | LiDAR / point-cloud / `PotreeConverter` |

**Rule of thumb:** if it touches a row in `lattice/*`, a file on the Mac, or a desktop app, it's not a Cloudflare Worker — it's a LATTICE sidecar endpoint.

### Generic agent (any platform)

The 30-second handoff at the top of this doc applies. The additional reading order:

1. `AGENTS.md` (root) → invariants
2. `meta/AGENT_ONBOARDING.md` → 5-minute boot
3. `meta/ARCHITECTURE.md` → mental model
4. `meta/ROADMAP.md` → "what phase are we in?"
5. Filter [`agent-ready` issues](https://github.com/JeromyJSmith/lattice-platform/issues?q=is%3Aopen+label%3Aagent-ready) by your area label

Branch naming for non-human agents:
- `agent/<issue-number>-<slug>` off `main` (or off the relevant feature branch if it's a sub-task)
- One issue per branch
- Open PR when done; don't sit on a branch.

---

## How LATTICE talks to itself

The data flow that connects everything (see [`meta/ARCHITECTURE.md`](ARCHITECTURE.md) for the full diagram):

```
   ┌── operator browser (TanStack Start) ──┐
   │  /runtime  /viewer  /analysis /globe   │
   │  /admin    /notebooks                  │
   └────────────────┬────────────────────────┘
                    │ HTTPS + SSE
                    ▼
   ┌──── TanStack Start server functions ───┐
   │  dispatchRun, listRuns, listStream...   │
   └────────────────┬────────────────────────┘
                    │ HTTP (SidecarClient)
                    ▼
   ┌────── FastAPI sidecar (127.0.0.1:7770) ─┐
   │  /v1/runtime/*  /v1/vw/*  /v1/itwin/*    │
   │  /v1/marpa/*    /v1/erp/* /v1/genai/*    │
   │  worker_loop polling agent_runs         │
   └────────────────┬────────────────────────┘
                    │ Pixeltable client
                    ▼
   ┌──────── Pixeltable (PG 16 + PostGIS + pgvector) ───┐
   │  lattice/execution/*  lattice/bridge/*              │
   │  lattice/genai/*                                     │
   └────────────────────┬────────────────────────────────┘
                        │
                        ├─→ claude -p subprocess (Claude Max)
                        ├─→ Ollama @ :11434 (local LLMs)
                        ├─→ ComfyUI @ :8188 (local image/3D)
                        └─→ Qdrant @ :6333 in OrbStack (CWICR cost data)
```

---

## How to submit a PR

1. Branch from `main` or the matching feature branch (`feature/3d-viewer`, `feature/vw-bridge`, etc. — see [`meta/WORKTREES.md`](WORKTREES.md)).
2. Run the relevant tests:
   ```bash
   make test-no-pxt      # always
   make test-pxt         # if pixeltable/ changed (requires local PG 16)
   bun run build         # if src/ changed
   bun run test          # if .test.ts files changed
   ```
3. Push and `gh pr create`. The PR template in `.github/PULL_REQUEST_TEMPLATE.md` is auto-attached.
4. `agent-pr-review.yml` will comment with files changed + area classification.
5. If your PR touched `pixeltable/migrations/` or `pixeltable/contracts/`, `schema-verify.yml` will run `make migrate-dryrun` against an ephemeral PXT_HOME and post the plan as a PR comment.
6. CODEOWNERS pings the right team (currently all `@JeromyJSmith` — adjust as collaborators land).
7. Squash-merge into `main`. `release.yml` cuts a date-based tag (`v2026.MM.DD`) and a GitHub Release with auto-generated notes.

---

## Cardinal rules

These hold for every agent on every platform. PRs that violate them don't merge.

1. **No `@itwin/core-backend`.** Pixeltable owns persistence. iTwin gives us BIS vocabulary and `@itwin/core-geometry` only. See [`meta/ITWIN_MAPPING.md`](ITWIN_MAPPING.md) Tier 4 for the full skip list.
2. **No Anthropic SDK in client code.** Server side or via `claude -p` subprocess only. The CLI uses Claude Max auth — no API key.
3. **uv only for Python.** Never pip, conda, poetry.
4. **No Revit / DGN / MicroStation.** IFC4.3 only at the boundary. DDC's Linux .deb converters are fallbacks; `ddc-rvtconverter` and `ddc-dgnconverter` are never installed.
5. **Pixeltable is the only database.** No standalone SQLite, no Postgres, no SQLite-backed `.bim` writes (we read those, never write them).
6. **All coordinates EPSG-normalized before Pixeltable.** Store WKT (POINT/POLYGON in WGS84) plus separate `longitude`/`latitude`/`elevation_m` floats. Never raw VW internal coordinates.
7. **Plant Style Manager controls all instances.** Never hardcode plant geometry per-instance — always via Plant Style.
8. **The `marpa/*`, `lattice/source`, `lattice/qa`, `lattice/budget`, `lattice/worksheet` Pixeltable trees are read-only here.** Those belong to other bodies (see `pixeltable/migrations/_helpers.py::FORBIDDEN_PREFIXES`).
9. **Ownership invariant is enforced at migration time.** Adding a new top-level namespace requires extending `OWNED_PARENTS` in `_helpers.py` and a peer-review.
10. **Every agent run is auditable.** Every long-running operation writes evidence to `lattice/execution/evidence`. No silent side effects.

When in doubt: stop and ask. Better to clarify than to roll back an invariant violation.

---

## Quick reference: where each agent platform's instruction file lives

| Platform | File |
|---|---|
| Claude Code (project-level) | `~/.claude/CLAUDE.md` (user) + `CLAUDE.md` files in `meta/`, `pixeltable/`, etc. |
| GitHub Copilot | [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) |
| OpenAI Codex | [`codex.md`](../codex.md) |
| Cloudflare Workers | [`cloudflare-agent.md`](../cloudflare-agent.md) |
| Generic agent | This file + [`meta/AGENT_ONBOARDING.md`](AGENT_ONBOARDING.md) |

If your platform isn't here yet, copy the closest match and adapt — then add an entry to this table in your first PR.
