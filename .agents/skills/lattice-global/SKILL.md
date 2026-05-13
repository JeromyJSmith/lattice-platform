---
description: Orchestrate the LATTICE global ratchet across all 7 sections — capture scores, identify the lowest section, invoke autoresearch, apply accepted proposals, and emit harness events.
---

# LATTICE Global Ratchet Orchestration

The global ratchet is the top-level improvement loop for the LATTICE platform. It
averages 7 section scores, targets the weakest section each cycle, and only accepts
proposals that move the global mean upward. All state is written to
`lattice/harness/*` Pixeltable tables so every cycle is auditable and replayable.

## When this skill applies

- Operator requests a manual improvement cycle (`bash meta/harness/bootstrap/run-autoresearch.sh <section>`)
- The global score in `meta/harness/latest.json` has not been refreshed in > 24 hours
- A section score drops more than 10 points (ratchet.error event required)
- Cross-section decisions need recording in `lattice/harness/global_decisions`
- Phase 2 cron scheduling fires (not yet active; wire-up only)

## How it works

1. Capture global snapshot:
   ```bash
   bash scripts/score-global.sh --json > meta/harness/latest.json
   ```
   Insert one row into `lattice/harness/health_snapshots` with
   `section='global'`, `score=<mean>`, `breakdown=<per-section JSON>`,
   `cycle_phase='pre'`, `timestamp=<now>`.

2. Read `meta/harness/latest.json` to identify the lowest-scoring section
   (schema | api | frontend | georef | genai | vw-itwin | ddc).

3. Acquire the single-writer lock (the bootstrap script handles this):
   ```bash
   bash meta/harness/bootstrap/run-autoresearch.sh <lowest-section>
   ```
   Exit code 1 means the lock is held by another cycle — abort this run.

4. After the section cycle completes, re-run `scripts/score-global.sh --json`
   and insert a second `health_snapshots` row with `cycle_phase='post'`.

5. If any single section dropped more than 10 points: insert a
   `lattice/harness/section_events` row with `event_type='ratchet.error'` and
   halt. Do not start a new cycle until the drift is manually resolved.

6. Record cross-section decisions in `lattice/harness/global_decisions` with
   fields: `decision`, `rationale`, `affected_sections`, `decided_by`, `timestamp`.

## Files used

- `meta/harness/GOAL.md` — fitness function and operating rules
- `meta/harness/MEMORY.md` — open decisions and session handoff notes
- `meta/harness/latest.json` — current global score (overwritten each run)
- `meta/harness/baseline-<date>.json` — immutable point-in-time snapshots
- `meta/harness/bootstrap/run-autoresearch.sh` — section cycle runner
- `scripts/score-global.sh` — aggregates all 7 section scripts
- `scripts/score-schema.sh`, `score-api.sh`, `score-frontend.sh`, `score-georef.sh`,
  `score-genai.sh`, `score-vw-itwin.sh`, `score-ddc.sh` — section scripts
- `lattice/harness/health_snapshots` — Pixeltable table, time-series score rows
- `lattice/harness/harness_proposals` — Pixeltable table, proposal outcomes
- `lattice/harness/section_events` — Pixeltable table, event log
- `lattice/harness/global_decisions` — Pixeltable table, cross-section decisions

## Constraints

- Only one autoresearch cycle runs at a time; the lock is `/tmp/harness-loop.lockdir`.
  Never work around it.
- The global score is the arithmetic mean of all 7 section scores with equal weight (1/7).
  Do not alter weights without recording a `global_decisions` row first.
- A baseline file (e.g., `meta/harness/baseline-2026-05-13.json`) is never edited
  or deleted — it is the immutable ratchet history anchor.
- A ratchet.error event halts the cycle. Do not attempt in-cycle recovery;
  log the error and exit non-zero.
- Quiet mode: no output unless global score changes by ± 2 pts or an error occurs.
- Proposals are applied via `git apply` only — never `cherry-pick` or direct file edits
  outside the sandbox worktree.
- Migrations 0001–0014 are write-once; 0015+ follow the same rule once landed.
