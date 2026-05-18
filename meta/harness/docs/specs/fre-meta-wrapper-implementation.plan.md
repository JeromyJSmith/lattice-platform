---
id: PLAN-FRE-META-WRAPPER-IMPLEMENTATION-0001
slug: fre-meta-wrapper-implementation-plan
title: FRE Meta Wrapper Implementation Plan
doctype: plan
status: draft
version: 0.1.0
owner: meta-wrapper-agent
created_at: 2026-05-18
updated_at: 2026-05-18
wrapper_scope: parent-child-meta-wrapper
execution_mode: dry-run-first
plan_type: implementation
parent_wrapper_path: ../meta
child_wrapper_path: meta
requires_goal_surface: true
requires_golden_path_surface: true
sources:
  - SRC-PARENT-META-WRAPPER
  - SRC-CHILD-META-HARNESS
  - SRC-STANFORD-META-HARNESS
  - SRC-AUTORESEARCH-UPSTREAM
  - SRC-AUTORESEARCH-MLX
  - SRC-FRE-PROMPT-SCHEMA
related_docs:
  - meta/harness/docs/specs/fre-meta-wrapper-seven.gates.md
  - meta/harness/docs/specs/fre-infranodus-hook.plan.md
  - meta/harness/docs/specs/fre-pixeltable-hook.plan.md
  - meta/harness/docs/specs/fre-worktree-consolidation.plan.md
  - meta/harness/docs/specs/agent-heavy-run-prompt-index.md
  - meta/harness/docs/specs/agent-heavy-run-prompt-schema.md
  - meta/harness/docs/specs/agent-heavy-run-prompt.schema.json
  - meta/harness/docs/specs/agent-heavy-run-prompt.template.yaml
  - meta/harness/docs/specs/copilot-shell-safe-heavy-run-template.md
  - meta/harness/CURRENT-STATE.md
---

# FRE Meta-Wrapper Implementation Plan

## Purpose

This plan turns the seven-gate wrapper concept into a dry-run-first
implementation sequence.

The point of this document is not to mutate the runtime immediately.
The point is to verify that the parent wrapper, child wrapper, prompt schema,
and Meta-Harness loop all fit together coherently before implementation.

## Current state summary

### Parent wrapper exists

Observed under `../meta/`:

- body registry
- bootstrap file
- contracts
- graph
- memory
- evidence
- runs
- docs
- wrapper lock file

This is a real outer shell, not just a concept, but it is still underused.

### Child wrapper exists

Observed under `meta/`:

- project-local `meta/harness/`
- scoring surfaces
- prompt schema
- autoresearch runner
- capability harvest and registry surfaces
- golden path and current-state surfaces

This is the active project-local wrapper.

### Gap

The parent and child wrappers are not yet joined by an explicit operational gate
bridge.

That is the problem this plan addresses.

There is also a second active gap:
the current `main` wrapper scaffolding is shallower than the already-defined
FRE contract documented in Notion and implemented in the sibling
`feat-fre-meta-harness-eval` worktree.

## Goal

Implement the wrapper model so that:

1. the parent wrapper can recognize and evaluate child wrapper gate state
2. the child wrapper can emit durable gate state and evidence back upward
3. the seven lifecycle gates become the governing abstraction for future project
   wrappers
4. the prompt schema and heavy-run methodology can target a gate explicitly
5. implementation starts only after a dry run proves the contract is coherent

## Scope

This plan is bounded to:

- parent wrapper analysis
- child wrapper analysis
- seven-gate contract design
- bridge artifact design
- dry-run design
- next-gate implementation plan

This plan is not yet:

- a live parent-wrapper runtime integration
- a full live Pixeltable ingestion and schema contract
- a full seven-gate scorer rollout
- a broad runtime refactor

## The parent-child relationship

### Parent responsibilities

- define generic wrapper contracts
- register body cells
- store cross-project memory, evidence, and runs
- decide which gate is currently active
- record gate-level histories across projects

### Child responsibilities

- expose project-local goals and golden paths
- implement scorers and verifiers
- own bounded proof runs
- emit gate state and proof artifacts
- stay truthful about red, amber, and green state

### Bridge responsibilities

- make gate state durable
- make project-local evidence legible to the parent wrapper
- make the active optimization target explicit

## Seven-gate rollout strategy

### Phase 0: Reconcile the known contract

Before new implementation work continues, consolidate the already-existing
contract from:

1. the FRE Notion workspace
2. the sibling worktree `lattice-worktrees/feat-fre-meta-harness-eval`
3. the current `main` wrapper scaffolding

This phase should produce a single mapping of:

- what already exists in the worktree
- what already exists in Notion
- what exists on `main`
- what is missing from `main`
- what should be adopted unchanged
- what should be renamed or translated
- what should remain historical lineage only

Deliverables:

1. worktree-to-main consolidation map
2. explicit seven-part contract-package inventory
3. explicit schema family inventory
4. explicit expected-failure contract inventory
5. explicit evaluation-and-promotion artifact inventory
6. explicit translation-map inventory
7. explicit InfraNodus comparison inventory and hook points
8. decision on whether the FRE bounded namespace should be restored, mirrored,
   or only referenced

No new wrapper abstraction should outrun this reconciliation step.

### Phase A: Freeze and name

1. Freeze the current DDC scorer as the first completed gate instance.
2. Name the seven gates explicitly.
3. Record the parent-child bridge contract.

Deliverables:

- `fre-meta-wrapper-seven.gates.md`
- this plan document

### Phase A1: Harden the contract layer

Before runtime implementation, define the wrapper contracts in a machine-checkable
way.

Deliverables:

1. JSON Schema Draft 2020-12 source schemas for wrapper documents and gate
   artifacts
2. Python validation path using `jsonschema`
3. Pydantic models aligned to the same contracts
4. Zod validators or TypeScript-compatible schema output aligned to the same
   contracts
5. parity tests proving that Python and TypeScript validators agree on valid and
   invalid examples
6. seven-part contract-package shape defined for source, schema, examples,
   expected-failures, tests, evaluation, and promotion
7. explicit InfraNodus artifact expectations for comparison-bearing slices
8. explicit Pixeltable artifact and table expectations for substrate-bearing slices

This phase exists because markdown structure alone is not enough.
The wrapper should be verifiable across languages, not only readable by humans.

### Phase B: Dry-run the bridge

Dry run only. No runtime mutation.

Simulate:

1. a child gate score snapshot
2. a child gate proof record
3. a parent wrapper bridge record
4. a selected active gate

Deliverables:

- bridge record example
- dry-run checklist
- implementation decision memo
- example artifacts that validate against the canonical schemas

### Phase C: Implement Gate 2 only

After dry run passes:

1. create the next gate
2. define its goal
3. define its golden path
4. define its scorer
5. define its verifier

Recommended next gate:

- `vw_estimation_path`

This is the next dependency layer after DDC foundation.

### Phase D: Template the wrapper

Only after Gate 2 works:

1. formalize parent wrapper gate scaffolding
2. formalize child wrapper gate scaffolding
3. make the pattern reusable for future projects

## Dry-run checklist

The dry run should confirm all of the following before implementation:

1. the seven gates are understandable and non-overlapping
2. the parent wrapper can point to a body cell and know which child meta
   surfaces matter
3. the child wrapper can emit one explicit gate state artifact
4. the current DDC gate can be treated as a frozen completed quality gate
5. the next gate can be defined without changing the meaning of Gate 1
6. the prompt schema can target one gate cleanly
7. the Copilot heavy-run contract can execute against that gate without shell
   breakage or scope sprawl
8. InfraNodus comparison surfaces are named explicitly for the dry-run slice
9. the dry run produces at least one comparison artifact requirement rather than
   only prose claims
10. the dry run names the durable Pixeltable tables or inventories that would
    hold the slice once promoted

## Example bridge dry run

Example child output:

```yaml
body_cell_id: body.vw_itwin_bridge
gate_id: ddc_foundation
gate_version: 1.0.0
score: 100
status: green
goal_path: ddc/GOAL.md
golden_path: ddc/estimation/GOLDENPATH.md
proof_artifacts:
  - meta/harness/docs/sessions/2026-05-18-ddc-estimation-contract-proof.json
blockers: []
```

Example parent interpretation:

- body cell is healthy on Gate 1
- active optimization target should advance to Gate 2
- Gate 1 remains monitored as a regression gate

## Prompt schema relationship

The existing prompt schema already gives the right bounded execution shape:

- mission
- current verified state
- hard rules
- tasks
- validation loop
- success criteria
- report contract

Canonical prompt-contract files:

- `meta/harness/docs/specs/agent-heavy-run-prompt-index.md`
- `meta/harness/docs/specs/agent-heavy-run-prompt-schema.md`
- `meta/harness/docs/specs/agent-heavy-run-prompt.schema.json`
- `meta/harness/docs/specs/agent-heavy-run-prompt.template.yaml`
- `meta/harness/docs/copilot-prompting-playbook.md`

The missing layer is gate identity.

The next schema revision should eventually add optional fields like:

```yaml
gate_context:
  gate_id: ""
  gate_version: ""
  parent_gate_ids: []
  child_gate_ids: []
```

Do not change the schema yet.
First validate the wrapper concept with docs and a dry run.

## Prompt hook rule

Every future prompt used by the wrapper should pass through the governed prompt
contract.

That means:

1. the prompt should be buildable from the template
2. the prompt should be auditable against the JSON Schema
3. the playbook should define shell-safe emission and execution behavior
4. no freeform execution prompt should bypass that contract silently

## Schema implementation strategy

The wrapper should use one canonical schema language and multiple validation
surfaces.

### Canonical source of truth

Use JSON Schema Draft 2020-12 as the canonical source of truth for:

- front matter
- bottom matter
- gate progress
- bridge records
- score results
- proof summaries

### Python path

Python should validate emitted artifacts in two ways:

1. direct validation using the `jsonschema` library
2. Pydantic models for runtime ergonomics and typed manipulation

### TypeScript path

TypeScript should validate emitted artifacts in two ways:

1. generated or hand-aligned types from the canonical schema
2. Zod validators for runtime checking in UI and tooling surfaces

### Acceptance rule

A wrapper contract is not hardened until:

1. the JSON Schema validates as a schema
2. valid examples pass in Python
3. invalid examples fail in Python
4. valid examples pass in TypeScript or Zod
5. invalid examples fail in TypeScript or Zod
6. the Python and TypeScript paths agree on the bounded test set

## Recommended immediate outputs

After this document, the next repo-local outputs should be:

1. `meta/harness/docs/specs/fre-worktree-consolidation.plan.md`
2. `meta/harness/docs/specs/fre-fractal-contract-package.plan.md`
3. schema family inventory for the wrapper contract
4. expected-failure inventory for wrapper artifacts
5. evaluation and promotion inventory for wrapper artifacts
6. translation-map inventory for FRE-to-LATTICE wrapper terms
7. only then `meta/harness/docs/specs/vw-estimation-path-gate.plan.md`
8. only then `meta/harness/docs/specs/vw-estimation-path-dry-run.plan.md`
9. only then `scripts/score-vw-estimation-path.sh`

## Decision rule

Proceed to implementation only if the dry run confirms:

- gate boundaries are coherent
- bridge artifacts are enough to relate parent and child wrappers
- the current DDC gate remains stable
- the next gate has measurable, non-hand-wavy metrics

If the dry run reveals ambiguity, fix the contract before writing the scorer.

---bottom-matter---
status_summary:
  completeness: 0.9
  confidence: high
  doc_state: draft
gate_progress:
  harvest:
    status: green
    notes: The implementation sequence has been extracted from current wrapper truth and recent DDC work.
  registry:
    status: green
    notes: Parent-wrapper, child-wrapper, and bridge responsibilities are named consistently.
  manifest:
    status: green
    notes: The implementation order is staged cleanly across parent, child, and bridge surfaces.
  verification:
    status: amber
    notes: The plan is dry-run oriented, but the bridge validator and gate scorer do not exist yet.
  state:
    status: amber
    notes: The rollout path is honest, but the future gate-state artifact contract still needs proof.
  health:
    status: green
    notes: The sequence is intentionally non-destructive and preserves the current green DDC foundation.
  promotion:
    status: amber
    notes: The plan is ready to guide implementation, pending agreement on the first downstream gate contract.
open_questions:
  - Should the bridge record be emitted first as markdown or YAML before Pixeltable ingestion exists?
  - Should Gate 2 live under `meta/harness/gates/` immediately or remain under `docs/specs/` until the dry run passes?
pending_validations:
  - Confirm `.plan.md` naming as the canonical implementation-plan suffix
  - Confirm future schema revision path for gate context fields
promotion_criteria:
  - Dry-run-first implementation sequence accepted
  - Gate 2 selected and bounded without destabilizing Gate 1
blocked_by: []
next_iteration:
  owner: meta-wrapper-agent
  objective: Draft the Vectorworks estimation path gate and its dry-run checklist.
