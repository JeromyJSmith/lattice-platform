# GitHub Copilot — workspace instructions for LATTICE

Before suggesting any code in this workspace, **read these two files first**:

1. [`AGENTS.md`](../AGENTS.md) — project-level rules, boundary invariants, locked stack versions.
2. [`CLAUDE.md`](../CLAUDE.md) — user-level conventions (uv, no-optional, security, etc.).

If you're picking up an issue, also read [`meta/AGENT_ONBOARDING.md`](../meta/AGENT_ONBOARDING.md) for the 5-minute boot guide and current priority queue.

## Locked stack (do not propose alternatives)

| Layer       | Choice                                            |
|-------------|---------------------------------------------------|
| JS runtime  | Bun                                               |
| Frontend    | TanStack Start + React 19 + Vite 8                |
| Sidecar     | FastAPI + uvicorn + asyncio (pinned `pixeltable==0.6.0`) |
| Python pkgs | **uv only** (never pip, conda, poetry, pipenv)    |
| 3D engine   | `@thatopen/components` 3.4.6 + Three.js 0.184     |
| Analytics   | deck.gl 9.3.2 + DuckDB WASM 1.33.1 + MapLibre 5  |
| iTwin       | `@itwin/core-geometry` 5.9.2 + `@itwin/core-common` — **never** `@itwin/core-backend** |
| Real agent  | model-routed via `meta/harness/bin/llm` (see [`meta/harness/MODELS.md`](../meta/harness/MODELS.md)) |

## Cardinal rules

1. **Never propose `@itwin/core-backend`.** Pixeltable replaces SQLite/SnapshotDb/BriefcaseDb.
2. **Never import any LLM SDK directly in client code** (Anthropic, OpenAI, etc.). All LLM calls go through `meta/harness/bin/llm` — the router decides which backend (Claude / Codex / Ollama / Copilot) handles which task.
3. **Never use pip, conda, poetry.** All Python ops go through `uv`.
4. **Never write to `marpa/*` or other foreign Pixeltable namespaces.** Ownership is enforced in `pixeltable/migrations/_helpers.py::assert_ownership`.
5. **No Revit, no DGN, no MicroStation.** IFC4.3 is the only authoring boundary.
6. **All coordinates EPSG-normalised** before writing to Pixeltable. Never raw VW internal coordinates.
7. **Plant Style Manager controls all instances.** Never hardcode geometry into individual symbols.

## Style preferences

- Default to **no comments**. Add one only when the WHY is non-obvious (a hidden constraint, a workaround for a specific bug). Don't explain WHAT the code does.
- Prefer `Edit` to `Write` for existing files.
- New files should match existing conventions (see neighbouring files in the same directory).
- TanStack Start API: `.inputValidator()` not `.validator()` (renamed in 1.167+).
- `@tanstack/react-hotkeys`: config is `{hotkey, callback}` not `{key, handler}`, and use `Mod+` prefix (platform-auto).
- Sidecar communication: `resolveSidecarClient()` from `src/runtime/pixeltable/sidecar-client.ts`, never raw `fetch`.

## When in doubt

Stop and ask. Better to clarify than to violate an invariant that costs more to roll back.
