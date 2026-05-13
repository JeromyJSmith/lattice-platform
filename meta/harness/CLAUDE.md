# meta/harness/ — Local Harness Notes

This directory is the global self-improvement layer for the LATTICE platform.
It aggregates 7 section harnesses into one ratchet loop that continuously
proposes, evaluates, and accepts score-improving changes.

## Key Files

| File | Purpose |
|------|---------|
| `GOAL.md` | Fitness function, improvement loop, action catalog, operating mode |
| `MEMORY.md` | Open decisions, failed experiments, session handoff notes |
| `bootstrap/run-autoresearch.sh` | The ratchet loop — one cycle per invocation |
| `baseline-*.json` | Point-in-time score snapshots (never deleted) |
| `latest.json` | Last global score output (overwritten each run) |

## How to Run a Cycle

```bash
# One section cycle (proposes via claude -p, scores, applies if better):
bash meta/harness/bootstrap/run-autoresearch.sh schema

# Dry run (skips claude -p, emits no-op diff — verifies wiring only):
bash meta/harness/bootstrap/run-autoresearch.sh --dry schema

# Help:
bash meta/harness/bootstrap/run-autoresearch.sh --help
```

Valid sections: `schema` `api` `frontend` `georef` `genai` `vw-itwin` `ddc`

## Where Baselines Live

`meta/harness/baseline-<date>.json` — one file per captured baseline.
Never edit or delete these. They form the ratchet history.

## The Ratchet Contract

1. Score the section **before** the proposal (`score_before`).
2. Apply the proposal in an isolated `git worktree` sandbox.
3. Score again in the sandbox (`score_after`).
4. **Accept only if `score_after > score_before`.** Otherwise discard.
5. On accept: `git apply` the diff to the working tree. Never cherry-pick.
6. Single writer enforced by `flock /tmp/harness-loop.lock`.

## Phase Notes

- Phase 1 (current): manual invocation, 7 section scripts (most stubs).
- Phase 2: `score-global.sh`, cron scheduling, Pixeltable event logging.
- Wave 2: InfraNodus integration decision pending (see MEMORY.md).
