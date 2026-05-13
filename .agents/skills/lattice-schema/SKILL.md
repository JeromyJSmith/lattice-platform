---
description: Author Pixeltable schema migrations, enforce write-once rules, run docs-drift checks, and maintain SCHEMA.md and _helpers.py for the LATTICE platform.
---

# LATTICE Schema Migration Authoring

The schema section owns all Pixeltable migration files in `pixeltable/migrations/`,
the `_helpers.py` idempotency layer, and the canonical table reference in
`meta/SCHEMA.md`. Migrations are write-once once landed; every new table or column
arrives as a new numbered migration file. The scoring script `scripts/score-schema.sh`
measures completeness, geometry correctness, path correctness, and docs drift.

## When this skill applies

- Adding a new Pixeltable table to any `lattice/*` namespace
- Adding columns to existing tables via `ensure_column()`
- Fixing docs drift between `meta/SCHEMA.md` and the actual migration files
- Updating `OWNED_PARENTS` in `_helpers.py` for a new top-level namespace
- Running the schema section cycle: `bash meta/harness/bootstrap/run-autoresearch.sh schema`
- Responding to a `score-schema.sh` output below 70/100

## How it works

1. Determine the next migration number:
   ```bash
   ls pixeltable/migrations/0*.py | sort | tail -1
   ```
   Increment by 1 (currently 0014 is landed; next is 0015).

2. Create `pixeltable/migrations/00NN_<topic>.py` using only helper calls:
   ```python
   from pixeltable.migrations._helpers import ensure_namespace, ensure_table, ensure_column, assert_ownership
   ensure_namespace("lattice/harness")
   ensure_table("lattice/harness/my_table", {"id": pxt.String, "payload": pxt.Json})
   ```
   Never call `pxt.create_table()` directly. Never write `pxt.Geometry` — use # allow-forbidden
   `pxt.String` for all geometry columns (WKT or GeoJSON strings only).

3. Add the new top-level namespace to `OWNED_PARENTS` at line 17 of `_helpers.py`
   if the namespace is new (e.g., `"lattice/harness"`).

4. Update `meta/SCHEMA.md` in the same commit:
   - Increment the declared table count at the top.
   - Add one row to the migration trail table.
   - Add new tables to the namespace map and table reference sections.

5. Also update `meta/ARCHITECTURE.md` and this `AGENTS.md` LIVE STATE block to
   reflect the new migration number and table count.

6. Run the pre-commit check to confirm no drift:
   ```bash
   bash scripts/pre-commit-docs-check.sh
   ```
   Exit 0 required before any commit.

7. Score the section:
   ```bash
   bash scripts/score-schema.sh
   ```
   Output format: `score: N/100`. Ratchet accepts if N increases.

## Files used

- `pixeltable/migrations/00NN_<topic>.py` — new migration (write once)
- `pixeltable/migrations/_helpers.py` — `OWNED_PARENTS`, `ensure_*`, `assert_ownership`
- `pixeltable/GOAL.md` — schema section fitness function
- `meta/SCHEMA.md` — canonical table reference (must sync with every migration)
- `meta/ARCHITECTURE.md` — schema overview table + verified-state header
- `meta/HANDOFF.md` — current-state header
- `AGENTS.md` (repo root) — LIVE STATE block migration count
- `scripts/score-schema.sh` — section scoring script
- `scripts/pre-commit-docs-check.sh` — docs-drift validator

## Constraints

- Migrations 0001–0014 are immutable. Never edit them. Create 0015+ instead.
- Never write `pxt.Geometry` in any migration file — the CI docs-sync-check blocks it. # allow-forbidden
- Never call raw `pxt.create_table()` or `pxt.create_dir()` — always use helpers.
- Never add a namespace to a migration without updating `OWNED_PARENTS` in `_helpers.py`.
- All four mandatory rules from the repo `AGENTS.md` must remain present after any edit.
- The wrong migration path `pixeltable/service/migrations/` does not exist; always use # allow-forbidden
  `pixeltable/migrations/`.
- The pre-commit check (`scripts/pre-commit-docs-check.sh`) must exit 0 before commit.
- Tables must not be removed from production namespaces.
