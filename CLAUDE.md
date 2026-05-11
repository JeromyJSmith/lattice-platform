# CLAUDE.md — repository root

This file is the primary instruction surface for any AI agent opening this repository (Claude Code, Copilot, Codex, Cursor, etc.). The fuller operational document lives at `../CLAUDE.md` (parent directory, machine-local); this in-repo file carries the rules that travel with the code.

> Agents: read [`meta/AGENT_ONBOARDING.md`](meta/AGENT_ONBOARDING.md) for the 5-minute boot and [`meta/HANDOFF.md`](meta/HANDOFF.md) for the multi-platform handoff.

---

## LIVE STATE (2026-05-11)

- **Migrations applied: 0001–0013** (13 total, write-once). **Planning artifacts on `feature/meta-harness`: 0014 (harness schema), 0015 (knowledge substrate)** — not yet applied to live Pixeltable; Phase 2 of the Meta-Harness build applies them.
- **Pixeltable tables: 36** applied across 4 owned namespaces (`lattice/{execution,bridge,genai,reality}`); post-Phase-2 = 45 across 6 namespaces (adds `lattice/harness`, `lattice/knowledge`)
- **FastAPI endpoints: 33** across 10 routers
- **Migration path:** `pixeltable/migrations/` (NOT `pixeltable/service/migrations/`)
- **Canonical schema reference:** [`meta/SCHEMA.md`](meta/SCHEMA.md)
- **Canonical API reference:** [`meta/API.md`](meta/API.md)
- **Authoritative architecture:** [`meta/ARCHITECTURE.md`](meta/ARCHITECTURE.md)

## MANDATORY SCHEMA + MIGRATION RULES

1. **`pxt.String` for geometry.** Pixeltable 0.6.x has NO `pxt.Geometry` type. All geometry columns are `pxt.String` storing WKT (`POINT(lon lat)`) or GeoJSON. PostGIS spatial queries layer on at the DuckDB WASM query layer downstream. **Never write `pxt.Geometry` in a migration — it will fail.**
2. **Write-once migrations.** Never edit a landed migration in `pixeltable/migrations/`. Always increment the number. Migrations 0001–0013 are immutable; the next one is `0014`.
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

## CARDINAL CODE RULES

- **No `@itwin/core-backend`** — Pixeltable owns persistence. Use `@itwin/core-geometry`, `@itwin/core-common`, `@itwin/core-quantity` only.
- **No Anthropic SDK in client code** — server functions via `@tanstack/ai` only, or via the `claude -p` subprocess in `pixeltable/service/worker.py`.
- **uv only for Python** — never pip / conda / poetry / pipenv.
- **No Revit / MicroStation / DGN** at the boundary — IFC4.3 only.
- **Pixeltable is the only database.** `.bim` files are read-only sources via `@pxt.udf` (sqlite3 implementation detail only).
- **Plant Style Manager controls all VW plant instances** — never hardcode geometry per-instance.
- **All coordinates EPSG-normalized before Pixeltable write** — never raw VW internal coordinates.

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
