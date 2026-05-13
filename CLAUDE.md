# CLAUDE.md — repository root

This file is the primary instruction surface for any AI agent opening this repository (Claude Code, Copilot, Codex, Cursor, etc.). The fuller operational document lives at `../CLAUDE.md` (parent directory, machine-local); this in-repo file carries the rules that travel with the code.

> Agents: read [`meta/AGENT_ONBOARDING.md`](meta/AGENT_ONBOARDING.md) for the 5-minute boot and [`meta/HANDOFF.md`](meta/HANDOFF.md) for the multi-platform handoff.

---

## LIVE STATE (2026-05-13)

- **Migrations applied: 0001–0014** (14 total, write-once). **Planning artifacts: 0015 (knowledge substrate), 0016 (docs substrate)** — committed but not yet applied to live Pixeltable; Phase 2 of the Meta-Harness build applies them. Also `_0014_harness_schema.py` parked as an alternate analytics-flavor schema (underscore prefix excludes it from the runner).
- **Pixeltable tables: 40** applied across 5 owned namespaces (`lattice/{execution,bridge,genai,reality,harness}`); post-Phase-2 = 48 across 6 namespaces (adds `lattice/knowledge`)
- **FastAPI endpoints: 33** across 10 routers
- **Migration path:** `pixeltable/migrations/` (NOT `pixeltable/service/migrations/`)
- **Canonical schema reference:** [`meta/SCHEMA.md`](meta/SCHEMA.md)
- **Canonical API reference:** [`meta/API.md`](meta/API.md)
- **Authoritative architecture:** [`meta/ARCHITECTURE.md`](meta/ARCHITECTURE.md)

## MANDATORY SCHEMA + MIGRATION RULES

1. **`pxt.String` for geometry.** Pixeltable 0.6.x has NO `pxt.Geometry` type. All geometry columns are `pxt.String` storing WKT (`POINT(lon lat)`) or GeoJSON. PostGIS spatial queries layer on at the DuckDB WASM query layer downstream. **Never write `pxt.Geometry` in a migration — it will fail.**
2. **Write-once migrations.** Never edit a landed migration in `pixeltable/migrations/`. Always increment the number. Migrations 0001–0016 are immutable (0001–0014 applied; 0015–0016 committed planning artifacts); the next one is `0017`. `_0014_harness_schema.py` is a parked alternate schema — the leading underscore excludes it from the runner.
3. **Migration path is `pixeltable/migrations/`.** Not `pixeltable/service/migrations/` — that path does not exist. The `docs-sync-check` CI workflow will block any PR that references the wrong path.
4. **Owned-parents rule.** Before creating tables in a new namespace (e.g. `lattice/reality`), `pxt.create_dir()` every ancestor first AND add the new top-level namespace to `OWNED_PARENTS` in `pixeltable/migrations/_helpers.py`. Always use the `ensure_namespace()` / `ensure_table()` / `ensure_column()` helpers — never raw `create_*` calls.

## MANDATORY WORKFLOW CONTRACT

Every agent MUST follow this sequence before any commit:

1. Do your work
2. Run the docs-sync check: `bash scripts/pre-commit-docs-check.sh`
3. If it fails → fix the docs first, then commit
4. Commit and push

The `docs-sync-check.yml` CI workflow enforces the same checks. It will block merge if any of these drift:
- Migration counts in `meta/SCHEMA.md`, `meta/ARCHITECTURE.md`, and this file
- Endpoint counts in `meta/API.md` and `meta/ARCHITECTURE.md`
- All 4 mandatory rules above remain present in this file
- Required section headers in `meta/FEATURE_BACKLOG.md`
- No forbidden strings (Revit, MicroStation, `@itwin/core-backend`, `pxt.Geometry`, `pixeltable/service/migrations`, bare `import Anthropic` in `.ts`/`.tsx`) outside the allow-listed docs files

See [`meta/AGENT_ONBOARDING.md` § 9 Mandatory workflow contract](meta/AGENT_ONBOARDING.md) for the contract.

## MODEL ROUTING

LLM calls go through the model router at [`meta/harness/bin/llm`](meta/harness/bin/llm). The router reads [`meta/harness/config/models.json`](meta/harness/config/models.json) to decide which backend (Claude / Codex / Copilot / Ollama) handles each task, with automatic fallback. No backend is privileged — swap any for any by editing the JSON. Full docs: [`meta/harness/MODELS.md`](meta/harness/MODELS.md).

Pin a single model for one harness run:
```bash
HARNESS_BACKEND=ollama:qwen2.5-coder:7b bash meta/harness/bootstrap/run-autoresearch.sh schema
```

## CARDINAL CODE RULES

- **No `@itwin/core-backend`** — Pixeltable owns persistence. Use `@itwin/core-geometry`, `@itwin/core-common`, `@itwin/core-quantity` only.
- **No LLM SDK imports in client code** — never `import Anthropic` / `import openai` / similar in `.ts`/`.tsx`/client `.py`. All LLM calls go through `meta/harness/bin/llm` (router) or `@tanstack/ai` adapters. The router decides which backend runs — config, not code.
- **uv only for Python** — never pip / conda / poetry / pipenv.
- **No Revit / MicroStation / DGN** at the boundary — IFC4.3 only.
- **Pixeltable is the only database.** `.bim` files are read-only sources via `@pxt.udf` (sqlite3 implementation detail only).
- **Plant Style Manager controls all VW plant instances** — never hardcode geometry per-instance.
- **All coordinates EPSG-normalized before Pixeltable write** — never raw VW internal coordinates.
- **Vendored = plain-copy, no nested `.git/`** — any external repo you bring in (especially `github.com/disler/*` / IndyDevDan repos: `single-file-agents`, `benchy`, `agentic-drop-zones`, `claude-code-hooks-mastery`, `the-library`, etc.) gets its `.git/` directory stripped before commit. `git clone` → `rm -rf <path>/.git` → `git add <path>/`. If you forget, `git add` emits an "embedded git repository" warning and creates a broken gitlink instead of vendoring the content. See [`.claude/rules/vendored-skills.md`](.claude/rules/vendored-skills.md) for the full procedure.

## When you add a migration

Update all of these in the SAME commit as the migration file:
- [`meta/SCHEMA.md`](meta/SCHEMA.md) — table reference + trail
- [`meta/ARCHITECTURE.md`](meta/ARCHITECTURE.md) — schema overview + verified-state header
- [`meta/HANDOFF.md`](meta/HANDOFF.md) — current-state header
- This file — `LIVE STATE` block

## When you add an endpoint

Update both files in the SAME commit as the route file:
- [`meta/API.md`](meta/API.md) — endpoint table
- [`meta/ARCHITECTURE.md`](meta/ARCHITECTURE.md) — FastAPI surface table + endpoint count

---

For deeper context (MCP topology, agent role map, iTwin tier map, DDC integration, the mirror invariant) see [`meta/ARCHITECTURE.md`](meta/ARCHITECTURE.md).
