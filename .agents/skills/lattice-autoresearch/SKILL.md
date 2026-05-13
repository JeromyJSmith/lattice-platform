---
description: Drive the LATTICE ratchet loop — score a section, call Codex -p to generate a unified diff proposal, apply it in a sandbox worktree, gate on score improvement, and log all outcomes.
---

# LATTICE Autoresearch Ratchet Driver

The autoresearch skill is the engine of the improvement loop. It wraps
`meta/harness/bootstrap/run-autoresearch.sh`, interprets outcomes, logs events to
Pixeltable harness tables, and escalates errors. Every cycle produces a proposal
(accepted or rejected) logged to `lattice/harness/harness_proposals`. This skill is
operationally distinct from the global orchestrator (`lattice-global`): the global
skill selects which section to target; this skill executes the cycle for one section.

## When this skill applies

- Executing a single autoresearch cycle for one of the 7 sections
- Diagnosing why a proposal was rejected (apply failure vs. score gate)
- Reviewing the proposal history in `lattice/harness/harness_proposals`
- Running dry-run validation to verify harness wiring without AI involvement
- Recovering from a stale sandbox worktree at `/tmp/harness-sandbox`
- Escalating a `ratchet.error` event to ops

## How it works

1. Acquire the single-writer lock and run one section cycle:
   ```bash
   bash meta/harness/bootstrap/run-autoresearch.sh <section>
   ```
   Valid sections: `schema` `api` `frontend` `georef` `genai` `vw-itwin` `ddc`.
   Exit code 0 = cycle completed (accepted or cleanly rejected).
   Exit code 1 = hard error (lock busy, unknown section, sandbox setup failed).

2. Dry-run mode (verify wiring, no AI call, no file changes):
   ```bash
   bash meta/harness/bootstrap/run-autoresearch.sh --dry <section>
   ```
   Emits a no-op (empty) diff. Scores before and after should be identical.
   Useful after harness changes to confirm sandbox/lock/apply wiring is intact.

3. Cycle internals (for diagnosis):
   - Lock: `mkdir /tmp/harness-loop.lockdir` (atomic on POSIX/macOS).
     PID written to `/tmp/harness-loop.lockdir/pid`.
     Stale lock (dead PID) is auto-stolen.
   - Sandbox: `git worktree add --detach /tmp/harness-sandbox <HEAD_SHA>`.
     Cleaned up on exit via `git worktree remove --force`.
   - Proposal: `timeout 120 Codex -p "<prompt>" > /tmp/harness-proposal-*.diff`.
     Prompt reads `<section>/GOAL.md` and `scripts/score-<section>.sh`, asks for
     ONE concrete change as a unified diff.
   - Apply check: `git apply --check < proposal.diff` in sandbox.
     Fails → rejected (no score gate reached).
   - Score gate: `score_after > score_before` → `git apply` to working tree.
     Score equal or lower → rejected, diff kept in `harness_proposals`.

4. Log outcome to Pixeltable (Wave 2 auto-write; currently manual):
   ```python
   import pixeltable as pxt
   proposals = pxt.get_table("lattice/harness/harness_proposals")
   proposals.insert([{
       "cycle_id": "<uuid>",
       "section": "<section>",
       "accepted": True/False,
       "score_before": score_before,
       "score_after": score_after,
       "diff": diff_text,
       "rationale": "<2 sentence rationale>",
       "error_log": None,  # or error text if rejected
       "timestamp": "<now>",
   }])
   ```

5. Emit section event:
   ```python
   events = pxt.get_table("lattice/harness/section_events")
   events.insert([{
       "section": "<section>",
       "event_type": "accepted",  # proposed | accepted | rejected | ratchet.error
       "cycle_id": "<uuid>",
       "timestamp": "<now>",
   }])
   ```

6. On ratchet.error (section score drops > 10 pts): log event_type=ratchet.error,
   exit non-zero. Do not start another cycle until drift is manually resolved.

7. Review recent proposal history:
   ```python
   proposals = pxt.get_table("lattice/harness/harness_proposals")
   recent = proposals.select(
       proposals.section, proposals.accepted, proposals.score_before,
       proposals.score_after, proposals.timestamp
   ).order_by(proposals.timestamp, asc=False).limit(20).collect()
   ```

## Files used

- `meta/harness/bootstrap/run-autoresearch.sh` — cycle runner (do not modify casually)
- `meta/harness/GOAL.md` — ratchet contract and operating rules
- `meta/harness/MEMORY.md` — failed experiments and session handoff notes
- `meta/harness/latest.json` — last global score (overwritten each run)
- `scripts/score-<section>.sh` — section scoring scripts (one per section)
- `lattice/harness/harness_proposals` — all proposal outcomes (accepted + rejected)
- `lattice/harness/section_events` — event log per cycle step
- `/tmp/harness-loop.lockdir` — single-writer lock directory
- `/tmp/harness-sandbox` — git worktree sandbox (ephemeral, cleaned after cycle)

## Constraints

- Never bypass the ratchet score gate to force-accept a rejected proposal.
- Never cherry-pick from the sandbox. Proposals land via `git apply` only.
- The sandbox worktree at `/tmp/harness-sandbox` is discarded after every cycle.
  Do not write permanent artifacts there.
- Failed proposals are kept in `harness_proposals` with `accepted=false`.
  They are the primary debugging artifact — do not delete them.
- `timeout 120` is the wall-clock limit for the `Codex -p` call. On timeout the
  cycle exits cleanly (no proposal this cycle — not a hard error).
- Max concurrency: 1. The `harness-loop.lockdir` prevents parallel cycles.
  Do not work around it.
- All events must be written to `lattice/harness/section_events` before the lock
  is released. Wave 2 automates this; for now, write manually after each cycle.
