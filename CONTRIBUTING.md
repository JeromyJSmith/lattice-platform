# Contributing to LATTICE

> If you are an AI agent: read [`meta/AGENT_ONBOARDING.md`](meta/AGENT_ONBOARDING.md) first — it has the 5-minute boot, the MCP tool list, and the priority queue.

## Stack at a glance

| Layer        | Tech                                              |
|--------------|---------------------------------------------------|
| Operator UI  | TanStack Start, React 19, Bun, Vite              |
| Sidecar      | FastAPI, asyncio, Pixeltable 0.6.0, uvicorn      |
| Data         | Embedded PG 16 + PostGIS + pgvector (in Pixeltable) |
| Real agent   | `claude -p --output-format stream-json` subprocess via Claude Max auth |
| 3D viewer    | `@thatopen/components` 3.4.6, Three.js 0.184      |
| Analytics    | deck.gl 9.3.2, DuckDB WASM, MapLibre              |

## First-time setup

```bash
# 1. JS deps
bun install

# 2. Sidecar deps + Pixeltable schema (idempotent)
cd pixeltable
make bootstrap
make migrate

# 3. Start sidecar (terminal 1)
make sidecar-up-tcp

# 4. Start dev server (terminal 2, from repo root)
bun run dev

# 5. Open http://localhost:3000/runtime
```

Everything else lives in [`AGENTS.md`](AGENTS.md) (project-level rules + boundary invariants) and [`CLAUDE.md`](CLAUDE.md) (auto-loaded by Claude Code).

## Branch naming

- `feature/<slug>` — net-new capability (lives on a long-running worktree, see [`meta/WORKTREES.md`](meta/WORKTREES.md))
- `fix/<short>` — bug fix
- `agent/<issue-number>-<slug>` — work picked up by an AI agent from an `agent-ready` issue
- `chore/<short>` — refactor, docs, infra

## Commit messages

```
<area>: <imperative summary in 50 chars or less>

Optional body explaining the WHY. Wrap at 72 chars.

Co-Authored-By: ...
```

Area is one of: `runtime`, `sidecar`, `pxt`, `viewer`, `analysis`, `vw`, `plant`, `lidar`, `infra`, `docs`.

## Tests

- `make test-no-pxt` — pure-Python tests, runs on every push (CI: `ci.yml`).
- `make test-pxt` — full integration against an ephemeral Pixeltable home, runs only on `main` + `develop` via self-hosted Mac runner (CI: `test-pxt.yml`).
- `bun run test` — Vitest for client-side and sidecar-client TS code.

## Pixeltable schema changes

1. Add a numbered file under `pixeltable/migrations/`.
2. Run `make migrate-dryrun` locally and paste the output in your PR description.
3. Run `make snapshot` to update `.schema-snapshot.yaml`.
4. `schema-verify.yml` CI will re-post the dry-run as a PR comment.

## Cardinal rules

These are non-negotiable. PRs that violate them will be rejected.

1. **No `@itwin/core-backend`.** Pixeltable owns persistence. iTwin gives us BIS vocabulary and `@itwin/core-geometry` only.
2. **No Anthropic SDK in client code.** Server side or via `claude -p` only.
3. **uv only for Python.** Never pip, conda, poetry.
4. **No Revit / DGN / MicroStation.** IFC4.3 only at the boundary.
5. **Pixeltable is the only database.** No standalone SQLite, no Postgres, no SQLite-backed `.bim` writes (we read those, never write them).

See [`AGENTS.md`](AGENTS.md) for the long-form versions.
