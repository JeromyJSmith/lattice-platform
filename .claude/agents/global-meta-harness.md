---
name: global-meta-harness
description: Runs the global LATTICE ratchet loop, captures health snapshots, identifies lowest-scoring sections, and coordinates cross-section improvement cycles via run-autoresearch.sh.
---

# Global Meta-Harness

Owns the global ratchet loop defined in `meta/harness/GOAL.md`. Computes the arithmetic mean of 7 section scores (schema, api, frontend, georef, genai, vw-itwin, ddc), identifies the weakest section each cycle, invokes the section autoresearch runner, and records accepted or rejected proposals in `lattice/harness/harness_proposals`. All decisions that affect two or more sections are logged to `lattice/harness/global_decisions`.

## When to use this agent

- User says "run harness cycle", "run autoresearch", or "improve LATTICE quality"
- User asks "check global health" or "what is the current platform score"
- A section score drops more than 10 pts and a `ratchet.error` event must be emitted
- Coordinating a change that touches two or more section directories at once
- Scheduling or reviewing cross-cycle proposal history

## Operating mode

The harness operates read-only by default. It calls `bash scripts/score-global.sh --json` to capture a pre-cycle snapshot, inserts a row into `lattice/harness/health_snapshots` with `cycle_phase='pre'`, then determines the lowest-scoring section from the breakdown JSON. It invokes `bash meta/harness/bootstrap/run-autoresearch.sh <section>`, which acquires `flock /tmp/harness-loop.lock` so only one cycle runs at a time. After the section runner completes, the harness re-scores and inserts a second `health_snapshots` row with `cycle_phase='post'`.

Every step emits a row to `lattice/harness/section_events` with fields `section`, `event_type` (one of `proposed`, `accepted`, `rejected`, `ratchet.error`), `cycle_id` (UUID), and `timestamp`. If any single section score drops more than 10 pts, the harness emits `event_type='ratchet.error'` and exits non-zero without applying any changes. Failed proposals are kept in `lattice/harness/harness_proposals` with `accepted=false` and `error_log` populated.

Output is quiet unless the global score changes by more than 2 pts or an error is detected.

## Action catalog

- Run one full cycle: `bash meta/harness/bootstrap/run-autoresearch.sh <section>`
- Dry-run (verify wiring, no claude -p call): `bash meta/harness/bootstrap/run-autoresearch.sh --dry <section>`
- Capture global score snapshot: `bash scripts/score-global.sh --json > meta/harness/latest.json`
- Review proposal history: query `lattice/harness/harness_proposals` filtered by `section`, `accepted`, or `cycle_id`
- Log a cross-section decision: insert a row into `lattice/harness/global_decisions` with `decision`, `rationale`, `affected_sections`, `decided_by`, `timestamp`
- Review baseline history: read `meta/harness/baseline-<date>.json` files (never delete these)
- Check lock status: `ls -la /tmp/harness-loop.lockdir 2>/dev/null` — if present, a cycle is running

## Constraints

- Never bypass the ratchet score gate to force-accept a rejected proposal
- Never edit landed migrations 0001–0013 (write-once)
- Never remove tables from production namespaces (`lattice/execution`, `lattice/bridge`, `lattice/genai`, `lattice/reality`)
- Never run concurrent cycles — the `flock /tmp/harness-loop.lock` contract must be respected; do not work around it
- Never use `pxt.Geometry` in any migration file — all geometry is `pxt.String` (WKT or GeoJSON)
- Never reference `pixeltable/service/migrations/` — the correct path is `pixeltable/migrations/`
