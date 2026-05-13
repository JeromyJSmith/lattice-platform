---
description: Author and maintain GOAL.md and MEMORY.md files for the LATTICE meta-harness — fitness functions, improvement loops, action catalogs, and session handoff notes.
---

# LATTICE GOAL.md and MEMORY.md Authoring

Each of the 7 sections and the global harness has a `GOAL.md` that defines the
fitness function, improvement loop, action catalog, and operating mode for that
section's ratchet. `MEMORY.md` (global harness only) records open decisions, failed
experiments, and session handoff notes. These files are editable and improve with
use — unlike migrations, they are not write-once.

## When this skill applies

- Writing a new section `GOAL.md` for a section that does not yet have one
- Refining an existing `GOAL.md` fitness function after the ratchet reveals gaps
- Adding a failed experiment entry to `meta/harness/MEMORY.md`
- Recording a cross-section decision in `MEMORY.md` open decisions
- Updating session handoff notes in `MEMORY.md` at the end of a work session
- A scoring script (`scripts/score-<section>.sh`) is added or changed and the
  corresponding `GOAL.md` fitness function must be updated to match

## How it works

1. Read the global GOAL.md for context on the fitness function contract:
   ```
   meta/harness/GOAL.md
   ```
   The global file defines the 7 sections, the ratchet-up criterion, drift detector
   rules, and operating mode. Section GOAL.md files inherit these constraints.

2. Author or update a section GOAL.md. Required sections (all 4 must be present):

   **Fitness Function** — numbered list of measurable health criteria, each tied to
   a concrete command or query that produces a verifiable signal. Reference the
   section scoring script (`scripts/score-<section>.sh`) and its output format.

   **Improvement Loop** — numbered steps the autoresearch harness follows: score
   before, propose, apply in sandbox, score after, accept/reject, log. Include the
   flock path for concurrency control.

   **Action Catalog** — concrete, runnable shell commands or Python snippets for
   the 4-6 most common operations in this section. Every entry must be immediately
   executable by the harness or a human operator.

   **Operating Mode** — how the section works in normal operation: startup commands,
   file patterns, failure modes, and fallback behavior.

3. Update `meta/harness/MEMORY.md` when:
   - A proposal is rejected for the second time for the same reason (add to Failed
     Experiments with date, section, what was tried, why rejected, lessons).
   - An open decision is resolved (move from Open Decisions to a new Resolved
     Decisions section, or delete and record in `lattice/harness/global_decisions`).
   - A work session ends without completing the next action (update Session Handoff
     Notes with date, current state, and specific next action).

4. Session handoff note format:
   ```markdown
   ## Session Handoff Notes
   - **Date.** YYYY-MM-DD.
   - **Baseline global score.** <score>/100 (see `meta/harness/baseline-<date>.json`).
   - **Phase.** Phase N in progress. <what landed>.
   - **Migration state.** <N> migrations landed (0001–00NN). Next migration is 00NN+1.
   - **Pixeltable harness tables.** <table list and population status>.
   - **Next action.** <single concrete next step>.
   ```

5. Fitness function quality checks for a section GOAL.md:
   - Every criterion references a runnable command or Pixeltable query.
   - At least one criterion references `scripts/score-<section>.sh` output.
   - No criterion is purely qualitative without a numeric threshold.
   - Failure modes are described with concrete fallback behavior.

6. Validate GOAL.md files are referenced by the ratchet runner:
   The runner prompt reads `<section>/GOAL.md` if it exists. Verify the path:
   ```bash
   ls pixeltable/GOAL.md src/GOAL.md georef/GOAL.md genai/GOAL.md \
      vw-plugin/GOAL.md ddc/GOAL.md pixeltable/service/GOAL.md
   ```
   The global harness GOAL.md is at `meta/harness/GOAL.md`.

## Files used

- `meta/harness/GOAL.md` — global fitness function (primary reference)
- `meta/harness/MEMORY.md` — open decisions, failed experiments, handoff notes
- `pixeltable/GOAL.md` — schema section GOAL.md
- `pixeltable/service/GOAL.md` — api section GOAL.md
- `src/GOAL.md` — frontend section GOAL.md
- `georef/GOAL.md` — georef section GOAL.md
- `genai/GOAL.md` — genai section GOAL.md
- `vw-plugin/GOAL.md` — vw-itwin section GOAL.md
- `ddc/GOAL.md` — ddc section GOAL.md
- `scripts/score-<section>.sh` — scoring scripts that GOAL.md files reference
- `meta/harness/bootstrap/run-autoresearch.sh` — runner that reads GOAL.md files

## Constraints

- GOAL.md files are editable and version-controlled — they improve with use.
  Unlike migrations, there is no write-once restriction.
- Every fitness function criterion must be measurable with a concrete command.
  Vague criteria ("code is clean", "tests pass") without a runnable check are
  not acceptable and will not produce useful ratchet signals.
- Action Catalog entries must be immediately runnable. Do not include pseudocode
  or aspirational commands that require setup not described in the file.
- MEMORY.md is the only file in the harness that accumulates failed experiments.
  Proposals rejected by the ratchet are also stored in `lattice/harness/harness_proposals`
  but the lessons learned go into MEMORY.md for human-readable postmortem.
- The runner prompt references `<section>/GOAL.md` by path. If you rename or move
  a GOAL.md file, update `meta/harness/bootstrap/run-autoresearch.sh` PROPOSAL_PROMPT
  in the same commit.
- Session handoff notes must include a single concrete next action. "Continue work"
  is not a valid next action.
