# OpenAI Codex — agent instructions for LATTICE

> **First action on every new task**: read `AGENTS.md`, `CLAUDE.md`, and `meta/AGENT_ONBOARDING.md`.

## Locked stack

| Layer | Choice |
|---|---|
| JS runtime | Bun |
| Frontend | TanStack Start + React 19 + Vite 8 |
| Sidecar | FastAPI + asyncio + `pixeltable==0.6.0` (pinned) |
| Python deps | **uv only** |
| 3D engine | `@thatopen/components` 3.4.6 + Three.js 0.184 |
| Analytics | deck.gl 9.3.2 + DuckDB WASM + MapLibre |
| iTwin | `core-geometry` + `core-common` only (never `core-backend`) |
| Agent runtime | model-routed via `meta/harness/bin/llm` (see [`meta/harness/MODELS.md`](meta/harness/MODELS.md)) |

## Cardinal rules (zero-tolerance)

1. No `@itwin/core-backend`. Pixeltable owns persistence.
2. No LLM SDK imports in client code (Anthropic, OpenAI, etc.). All LLM calls go through `meta/harness/bin/llm` — backend is config-driven.
3. No pip / conda / poetry. uv only.
4. No writes to `marpa/*` or `lattice/source` / `lattice/qa` / `lattice/budget` / `lattice/worksheet` Pixeltable trees — those belong to other bodies.
5. No Revit, DGN, MicroStation. IFC4.3 at the authoring boundary.
6. Plant geometry is owned by Plant Style Manager — never hardcoded per-instance.

## Code style

- No comments unless the WHY is non-obvious.
- No multi-paragraph docstrings; one short line max.
- Edit existing files; don't create new ones unless required.
- Match the conventions of neighbouring files.
- Use `resolveSidecarClient()` for sidecar HTTP, not raw fetch.

## Verify before submitting

- `make test-no-pxt` (always)
- `bun run build` (if `src/` changed)
- `make test-pxt` (if `pixeltable/` changed)
- Visual smoke test at `/runtime` for any UI change

## When uncertain

Stop and ask. Don't guess at an invariant — read `AGENTS.md`. The full file map and rules are there.
