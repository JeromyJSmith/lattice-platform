# Schema Section Harness — GOAL.md

## Fitness Function

A schema section is healthy when:

1. **Completeness.** Every table declared in `pixeltable/migrations/*.py` (0001–0014 and beyond) appears in `meta/SCHEMA.md` with correct migration number, column count, and purpose statement.
2. **No geometry type errors.** Zero occurrences of `pxt.Geometry` in any migration file. All geometry columns are `pxt.String` storing WKT or GeoJSON.
3. **Migration path correct.** Every reference in `meta/SCHEMA.md`, `CLAUDE.md`, `ARCHITECTURE.md`, and `HANDOFF.md` points to `pixeltable/migrations/` — never `pixeltable/service/migrations/`.
4. **Ownership enforced.** Every namespace touched by a migration is listed in `OWNED_PARENTS` in `pixeltable/migrations/_helpers.py`. The list at line 17 contains exactly the top-level namespaces created by that section's migrations.
5. **Write-once integrity.** No migration file numbered 0001–0013 has ever been edited post-landing. All new work creates migration 0014 or higher.
6. **Operational signal.** The score from `scripts/score-schema.sh` (output: `score: N/100`) increases or holds across ratchet cycles. Score is computed as: table count + validation of ownership + path correctness + geometry type scan + docs drift.

## Improvement Loop

The autoresearch harness:

1. Samples the live schema state (table count, owned namespaces, migration count, drift flags).
2. Proposes a single atomic change (one of: add table, fix docs drift, refactor helpers, add namespace to ownership list).
3. Applies the proposal in a `git worktree add /tmp/harness-sandbox` sandbox with clean Pixeltable state.
4. Runs `scripts/score-schema.sh` before and after.
5. Accepts the proposal only if `score_after > score_before` or if the score is stable and the change reduces documentation debt.
6. Writes the proposal outcome to `lattice/harness/harness_proposals` with fields: timestamp, proposal_id, section (pixeltable), accepted (bool), score_before, score_after, diff, rationale, error_log (if rejected).
7. Every cycle appends an event to `lattice/execution/section_events` with: section=pixeltable, event_type (proposed|accepted|rejected), timestamp, cycle_id.
8. Concurrency: single-writer via `flock /tmp/harness-loop.lock` — only one proposal-apply-score cycle runs at a time across all sections.

## Action Catalog

Concrete things an agent or harness can do in this section:

- **Add a new migration.** Create `pixeltable/migrations/00NN_<topic>.py` where NN is one higher than the last landed number (currently 0013, so next is 0014). Must use `ensure_namespace()`, `ensure_table()`, `ensure_column()` helpers from `_helpers.py`. Must not use raw `pxt.create_*` calls.
- **Update `OWNED_PARENTS`.** Edit `pixeltable/migrations/_helpers.py` line 17 to add a new top-level namespace string (e.g., `"lattice/harness"`) if a migration introduces tables in a new namespace. Must call `assert_ownership()` in the migration to guard against accidental writes.
- **Sync `meta/SCHEMA.md`.** Update the migration trail table (add one row), update the namespace map (add new dir/tables if needed), update the table reference section (list the new tables with migration number and purpose). Must increment the declared table count at the top.
- **Edit `pixeltable/GOAL.md` itself.** Refine the fitness function, improve the loop description, add action examples, clarify operating mode — this file is editable and improves with use.
- **Refactor `_helpers.py` helpers.** If a cleaner pattern emerges for `ensure_namespace`, `ensure_table`, or `ensure_column`, refactor in place (with tests) to strengthen the idempotency guarantees.
- **NOT allowed:** Never edit a landed migration (write-once — land and archive). Never remove tables from production. Never change the `pxt.String` geometry pattern without breaking change coordination across the platform. Never add namespaces to migrations without updating `OWNED_PARENTS`.

## Operating Mode

- **Read-only by default.** The harness proposes, it does not commit. Humans or a meta-harness layer accept/reject proposals.
- **Every proposal includes:** unified diff of all changed files, migration number (if applicable), rationale (max 2 sentences), and predicted score delta.
- **Failed proposals are kept for postmortem.** Logged with the same structure as accepted proposals, tagged outcome=rejected, with error_log showing why the ratchet rejected it.
- **Health snapshots.** Before every proposal cycle, capture: current migration count, table count, owned namespace count, docs drift flags, last schema modification timestamp. Store in `/tmp/harness-health-pixeltable.json`.
- **Quiet by default.** No logs unless score changes or an error is detected. Errors are fatal — stop the cycle, log to `section_events`, resume on next harness trigger.
