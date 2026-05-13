# Global Meta-Harness — GOAL.md

## Fitness Function

The platform is healthy when all 7 sections trend upward together.

**Global score** = arithmetic mean of 7 section scores:

| Section   | Scoring script               | Weight |
|-----------|------------------------------|--------|
| schema    | `scripts/score-schema.sh`    | 1/7    |
| api       | `scripts/score-api.sh`       | 1/7    |
| frontend  | `scripts/score-frontend.sh`  | 1/7    |
| georef    | `scripts/score-georef.sh`    | 1/7    |
| genai     | `scripts/score-genai.sh`     | 1/7    |
| vw-itwin  | `scripts/score-vw-itwin.sh`  | 1/7    |
| ddc       | `scripts/score-ddc.sh`       | 1/7    |

**Ratchet-up criterion:** any cycle that increases the global score (even by 0.1 pts) is accepted.

**Drift detector:** if any single section score drops more than 10 pts in one cycle, the harness emits a `ratchet.error` event to `lattice/harness/section_events` and halts that cycle. No cross-section changes may land until the drift is resolved.

The global score is computed by `scripts/score-global.sh --json`, which calls each section script, averages the results, and writes `meta/harness/latest.json`.

## Improvement Loop

Schedule: invoked manually by an agent or operator. Phase 2 will add cron scheduling.

Per cycle:

1. Capture a global score snapshot — insert a row into `lattice/harness/health_snapshots` with `section='global'`, `score=<mean>`, `breakdown=<per-section JSON>`, `timestamp=<now>`.
2. Identify the lowest-scoring section from the current snapshot.
3. Invoke the section autoresearch runner:
   ```bash
   bash meta/harness/bootstrap/run-autoresearch.sh <section>
   ```
4. The section runner proposes a change, evaluates it in a `git worktree` sandbox, and logs the outcome to `lattice/harness/harness_proposals`.
5. If accepted: apply the proposal to the working tree via `git apply` (never a plain cherry-pick — the sandbox worktree is discarded after scoring).
6. Re-capture the global score and write a second row to `health_snapshots` marking `cycle_phase='post'`.
7. Every step emits a row to `lattice/harness/section_events` with `section=<section>`, `event_type` in `{proposed, accepted, rejected, ratchet.error}`, `cycle_id=<uuid>`, `timestamp=<now>`.

Concurrency: the runner acquires `flock /tmp/harness-loop.lock` at startup. Only one autoresearch cycle runs at a time across all sections.

## Action Catalog

**Run one cycle for a specific section:**
```bash
bash meta/harness/bootstrap/run-autoresearch.sh <section>
```

**Dry-run (no claude -p call, no file changes):**
```bash
bash meta/harness/bootstrap/run-autoresearch.sh --dry <section>
```

**Capture current global score:**
```bash
bash scripts/score-global.sh --json > meta/harness/latest.json
```

**Review proposal history:**
Query `lattice/harness/harness_proposals` — filter by `section`, `accepted`, or `cycle_id`.

**Make a cross-section decision:**
Insert a row into `lattice/harness/global_decisions` with `decision`, `rationale`, `affected_sections`, `decided_by`, `timestamp`.

**NOT allowed:**
- Bypassing the ratchet score gate to force-accept a rejected proposal.
- Editing landed migrations (0001–0013 are write-once; 0014+ follow the same rule once landed).
- Removing tables from production namespaces.
- Running concurrent cycles (the flock prevents this; do not work around it).

## Operating Mode

- **Read-only by default.** The meta-harness proposes; it does not commit. The section autoresearch runner applies proposals only within the sandbox worktree, then uses `git apply` on the working tree after the ratchet gate passes.
- **Every proposal includes:** unified diff of all changed files, section name, rationale (max 2 sentences), predicted score delta, and `cycle_id` for traceability.
- **Quiet mode:** no output unless the global score changes by ± 2 pts or an error is detected.
- **On error:** log a row to `lattice/harness/section_events` with `event_type='ratchet.error'`, halt the cycle, and exit non-zero. Do not attempt recovery within the same cycle invocation.
- **Failed proposals are kept.** Every rejected diff is written to `lattice/harness/harness_proposals` with `accepted=false` and `error_log` explaining why the ratchet rejected it.
