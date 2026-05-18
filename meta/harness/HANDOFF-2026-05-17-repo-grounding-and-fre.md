# Repo Grounding + FRE Handoff (2026-05-17)

Date: 2026-05-17
Canonical repo root: `/Volumes/PixelTable/VW_iTWIN_Bridge/VW_iTwin_Bridge`
Parent container only: `/Volumes/PixelTable/VW_iTWIN_Bridge`
Timezone used during this work: `America/Denver`

## What This Handoff Covers

This handoff captures two distinct but now-related outcomes:

1. the repo/worktree cleanup and Git grounding pass
2. the FRE branch review and refinement pass

The important result is that the repo is no longer in a confused half-local,
half-unpushed state, and the newest FRE evaluation branch is preserved, pushed,
and meaningfully improved.

## Current Git Truth

### Main branch

Local `main` is now intentionally reset to the real remote baseline:

```text
branch: main
HEAD: d02328e
status: clean
tracking: origin/main
```

This was deliberate.

Do not assume the more recent local-only commits are on `main`.
They are not.

### Why `main` was not pushed directly

A direct push of the local advanced `main` failed for two verified reasons:

1. GitHub rejected oversized files in local-only history:
   - `projects/vectorworks project files/*.vwx`
   - backup `.vwx` files
   - `3d_assets/model.bim` produced a warning
2. after cleaning that history, GitHub rejected the required rewrite because:

```text
GH006: Protected branch update failed for refs/heads/main.
Cannot force-push to this branch.
```

So the correct path became:

```text
clean history on a repair branch
-> push repair branch
-> open PR
-> leave protected main untouched
```

### Safety branches created during cleanup

These branches exist locally and should be preserved until the cleanup work is
fully resolved upstream:

- `repair/main-clean-history-20260517`
- `backup/main-pre-largefile-cleanup`

### Repair PR already opened

The cleanup and harness-grounding work lives here:

- PR: [#388](https://github.com/JeromyJSmith/lattice-platform/pull/388)
- branch: `repair/main-clean-history-20260517`

This PR carries:

- no-mock runtime enforcement
- benchmark/use-case grounding work
- MCP capability wiring additions
- Vectorworks local-binary ignore guardrails on the repaired history path

## Current Worktree Truth

The active registered worktrees are clean and recognized:

```text
/Volumes/PixelTable/VW_iTWIN_Bridge/VW_iTwin_Bridge                          -> main
/Volumes/PixelTable/VW_iTWIN_Bridge/lattice-worktrees/develop               -> develop
/Volumes/PixelTable/VW_iTWIN_Bridge/lattice-worktrees/feat-fre-meta-harness-eval
                                                                        -> feat/fre-meta-harness-eval
/Volumes/PixelTable/VW_iTWIN_Bridge/lattice-worktrees/feature-3d-viewer     -> feature/3d-viewer
/Volumes/PixelTable/VW_iTWIN_Bridge/lattice-worktrees/feature-analytics-layer
                                                                        -> feature/analytics-layer
/Volumes/PixelTable/VW_iTWIN_Bridge/lattice-worktrees/feature-plant-geometry
                                                                        -> feature/plant-geometry
/Volumes/PixelTable/VW_iTWIN_Bridge/lattice-worktrees/feature-point-cloud    -> feature/point-cloud
/Volumes/PixelTable/VW_iTWIN_Bridge/lattice-worktrees/feature-vw-bridge      -> feature/vw-bridge
/Volumes/PixelTable/VW_iTWIN_Bridge/VW_iTwin_Bridge/.claude/worktrees/grove-harvest
                                                                        -> feature/portless-browser-bonsai
/Volumes/PixelTable/VW_iTWIN_Bridge/VW_iTwin_Bridge_redshift                 -> feature/redshift-vw-integration
```

The stale hidden Claude worktree `awesome-jepsen-912660` was cleaned and
removed. Its stale local branch was also deleted.

## Local-Only Heavy Asset Rule

The user explicitly decided that `3d_assets/model.bim` is local-only storage.

Machine-local excludes were added in:

```text
.git/info/exclude
```

Current local-only patterns added there:

- `3d_assets/model.bim`
- `projects/vectorworks project files/*.vwx`
- `projects/vectorworks project files/**/*.vwx`
- `projects/vectorworks project files/*.lck`
- `projects/vectorworks project files/**/*.lck`

This is intentionally machine-local, not committed repo policy.

## Harness / Proof-Grounding Work Already Done

The repo cleanup also surfaced and corrected a real proof-integrity problem in
the harness stack:

- a weak CWICR match for “creeping thyme” was being dressed up as a successful
  use-case
- the UI was presenting low-signal retrieval as if it were valid proof

That was corrected in the repair branch so low-confidence retrieval is treated
as failed evidence instead of successful operator proof.

## FRE Branch Status

The newest branch and newest serious evaluation branch is:

```text
feat/fre-meta-harness-eval
```

It is intentionally left unmerged for later review.

The user explicitly likes the direction and wants it reviewed as a serious
candidate, not merged automatically.

### Current FRE branch head

```text
branch: feat/fre-meta-harness-eval
HEAD: 8511990
tracking: origin/feat/fre-meta-harness-eval
status: clean
```

### Important FRE commits

Recent branch history:

```text
8511990 feat(fre): gate document contract readiness
e5093e2 feat(fre): add document contract parsing and fresh run allocation
92b9ee5 feat(fre): checkpoint bounded meta-harness evaluation
d02328e feat(vw-bridge): AppleScript-based VW MCP server — no TCP, no file dialog
```

## FRE Review Conclusion So Far

The branch is a strong candidate for adoption as a proof-gating contract, but
not yet as universal platform doctrine.

Current recommendation:

```text
adopt for proof gating only
not yet for core Meta-Harness doctrine
```

Reason:

- the branch is genuinely schema-oriented
- it creates a research -> source -> schema -> validation -> repair ->
  promotion loop
- it pressures invalid examples
- it emits repair tasks and promotion decisions

But it should still prove itself against one narrow LATTICE integration slice
before expanding further.

## FRE Issues That Were Identified and Addressed

### 1. Standalone commands were overwriting the same run id

Before refinement, direct commands like:

```bash
uv run python meta/harness/fre/harness/evaluate.py
```

could write into the default run:

```text
RUN-2026-05-16-0001
```

unless `FRE_RUN_ID` was manually pinned.

This was dangerous because it weakened restart-ready evidence and allowed run
artifact collision.

### 2. The branch implied a document contract but did not actually parse one

The branch discussed schema-first discipline and the user clarified a desired
document shape:

- front matter = beacon/configuration
- body = narrative
- bottom matter = checklist / plan-state / cursor-style execution state

The implementation did not yet support that explicitly.

## FRE Refinement Landed

The latest FRE commit (`e5093e2`) adds:

### A. Document contract parsing

In:

- `meta/harness/fre/harness/lib.py`

New capabilities:

- parse Markdown front matter
- parse checklist-style bottom matter
- scan FRE docs for document-contract participation
- emit `document-contract.json` into each run

### B. Fresh run allocation for standalone commands

Standalone FRE scripts now allocate a fresh `RUN-*` directory unless
`FRE_RUN_ID` is explicitly pinned.

This affects:

- `meta/harness/fre/harness/evaluate.py`
- `meta/harness/fre/harness/propose_repairs.py`
- `meta/harness/fre/harness/iterate.py`

### C. Contract-bearing docs

These docs were updated to carry real contract metadata:

- `meta/harness/fre/GOAL.md`
- `meta/harness/fre/GoldenPath.md`

Both now include:

- front matter
- bottom matter checklist sections

### D. New tests

Added:

- `meta/harness/fre/tests/test_document_contract.py`

This covers:

- front-matter extraction
- bottom-matter extraction
- document-contract status reporting
- fresh run allocation via CLI context

## FRE Validation Performed

All FRE checks in the latest refinement session were run with `uv run`, not
`python3`.

Validated commands:

```bash
uv run pytest meta/harness/fre/tests -q
uv run python meta/harness/fre/harness/validate_schema.py
uv run python meta/harness/fre/harness/validate_examples.py
uv run python meta/harness/fre/harness/evaluate.py
uv run python meta/harness/fre/harness/evaluate_real_fixtures.py
```

Observed result after refinement:

```text
15 passed
```

Standalone evaluate command was re-checked and now created a fresh run:

```text
before=RUN-2026-05-16-0014
after=RUN-2026-05-16-0015
fresh-run-created
```

And the emitted `document-contract.json` reported:

```text
front_matter_count = 3
bottom_matter_count = 2
status = pass
```

There is still a local `uv` warning on this machine:

```text
WARN Ignoring malformed managed Python entry:
Failed to parse Python installation key `.temp`
```

This warning did not prevent the FRE validations from completing.

## 2026-05-18 Addendum

### Current baseline in this worktree

At the start of this follow-up pass, the repo root on local `main` reported:

```text
## main...origin/main [ahead 1]
 M meta/harness/docs/specs/agent-heavy-run-prompt-index.md
?? meta/harness/HANDOFF-2026-05-17-repo-grounding-and-fre.md
?? meta/harness/docs/specs/copilot-shell-safe-heavy-run-template.md
```

That baseline matters because this pass is intentionally limited to those three
paths only.

### DDC state now worth carrying forward

The DDC repair slice is now in a genuinely green promoted state and should be
treated as a verified baseline, not an aspirational target.

Carry forward this truth:

- OpenConstructionERP BOQ read, export, sync, and governed Juniper writeback
  are green
- the governed quantity-takeoff path is green and posts explicit evidence
- the Juniper estimation path is the operational proof target
- remaining DDC work is follow-on surface expansion, not basic proof recovery

### Shell-safe FRE prompt artifacts are now established

The heavy-run prompt contract now has a more bulletproof operator surface for
terminal-driven Copilot execution.

Key artifacts in this slice:

- `meta/harness/docs/specs/agent-heavy-run-prompt-index.md`
- `meta/harness/docs/specs/copilot-shell-safe-heavy-run-template.md`

What is now explicit:

- wrap the full prompt body in plain ASCII single quotes
- do not use inner apostrophes
- do not use backticks, subshell forms, or shell variables
- keep the text plain ASCII
- keep Python execution `uv`-first
- structure the run as one bounded mission with a self-loop before validation

This should be treated as the safer default whenever a heavy terminal-passed
Copilot prompt is prepared by hand.

### Next backlog priorities after this cleanup

The top completed priority-queue items are already landed, so the next immediate
product work moves to the first unchecked operator-console items:

1. truncate long task strings in the runtime table and show full text on hover
2. replace plain-text runtime statuses with color-coded badges
3. upgrade EventTimeline rendering for markdown, timestamps, and full-response
   copy
4. add the active-run pulse indicator and Cmd+Enter task submission

The next DDC-specific follow-on priorities are:

1. broaden the `POST /v1/erp/phases` proof into a fuller 4D/5D project-facing
   surface
2. finish CWICR follow-on work for IFC writeback and vector-query parity
3. extract the 221 DDC skill patterns into agent-callable Pixeltable-backed
   tools
4. convert DDC n8n workflow patterns into governed LATTICE pipeline templates
5. finish the admin dashboard surface and cost overlays

## What The Next Session Should Do

### If continuing repo-direction work

1. Start from the real repo root:
   - `/Volumes/PixelTable/VW_iTWIN_Bridge/VW_iTwin_Bridge`
2. Treat local `main` as aligned to `origin/main`
3. Treat PR `#388` as the active path for the cleaned harness-grounding work
4. Do not re-run the large-file cleanup or force-push investigation from
   scratch unless the remote situation changes

### If continuing FRE work

Work in:

```text
/Volumes/PixelTable/VW_iTWIN_Bridge/lattice-worktrees/feat-fre-meta-harness-eval
```

Start by reading:

1. `meta/harness/fre/README.md`
2. `meta/harness/fre/GOAL.md`
3. `meta/harness/fre/GoldenPath.md`
4. `meta/harness/fre/docs/fre-to-lattice-map.md`
5. `meta/harness/docs/specs/fre-method-evaluation-plan-2026-05-16.md`

Then re-run:

```bash
uv run pytest meta/harness/fre/tests -q
```

### Best next FRE step

The previous best-next step is now done:

```text
promote document_contract from passive artifact to evaluated gate/metric
```

This is now true on branch `feat/fre-meta-harness-eval` at `8511990`:

- `document_contract` is now a required metric
- `document_contract` is now a blocking gate in `evaluate_data()`
- malformed document-contract parsing now forces promotion status to `REJECT`
- the FRE loop example/schema were updated to include the new metric
- regression coverage now proves malformed document-contract state degrades
  promotion readiness

### Best next adoption review step

Take one existing LATTICE proof workflow and run it through the FRE contract as
a bounded pilot.

Do not broaden FRE into doctrine first.

## Do Not Forget

- Use `uv run`, not `python3`, for FRE execution
- `model.bim` is local-only storage by user decision
- `feat/fre-meta-harness-eval` is intentionally unmerged
- `main` is clean but does not contain the repair branch or FRE branch work
- `repair/main-clean-history-20260517` and PR `#388` still matter
