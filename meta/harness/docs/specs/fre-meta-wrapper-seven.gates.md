---
id: PLAN-FRE-META-WRAPPER-GATES-0001
slug: fre-meta-wrapper-seven-gates
title: FRE Meta Wrapper Seven Gates
doctype: plan
status: draft
version: 0.1.0
owner: meta-wrapper-agent
created_at: 2026-05-18
updated_at: 2026-05-18
wrapper_scope: parent-child-meta-wrapper
execution_mode: dry-run-first
gate_count: 7
parent_wrapper_path: ../meta
child_wrapper_path: meta
goal_surface: meta/harness/GOAL.md
golden_path_surface: meta/harness/golden_path.md
sources:
  - SRC-PARENT-META-WRAPPER
  - SRC-CHILD-META-HARNESS
  - SRC-FRE-EVAL-WORKTREE
  - SRC-STANFORD-META-HARNESS
  - SRC-AUTORESEARCH-UPSTREAM
  - SRC-AUTORESEARCH-MLX
  - SRC-COPILOT-PROMPT-SCHEMA
related_docs:
  - meta/harness/docs/specs/fre-meta-wrapper-implementation.plan.md
  - meta/harness/docs/specs/fre-infranodus-hook.plan.md
  - meta/harness/docs/specs/fre-pixeltable-hook.plan.md
  - meta/harness/docs/specs/agent-heavy-run-prompt-schema.md
  - meta/harness/docs/copilot-prompting-playbook.md
  - meta/harness/CURRENT-STATE.md
---

# FRE Meta-Wrapper Seven Gates

## Purpose

This document defines the next operational layer above the current repository
Meta-Harness.

The child repository `meta/` directory is the project-local implementation
surface.
The parent `../meta/` directory is the outer wrapper that should be reusable
across projects.

This document turns the current philosophy into a concrete wrapper model:

- one outer parent wrapper
- one child project wrapper
- one recursive seven-gate capability lifecycle
- one FRE-style iterative loop per gate

The outer wrapper does not replace the child repo `meta/` directory.
It governs it, seeds it, evaluates it, and receives evidence back from it.

## Upstream grounding

This wrapper design is informed by three already-proven lineages:

1. Stanford Meta-Harness:
   optimize the harness around a fixed model or agent, not just the prompt.
2. Karpathy Autoresearch and the MLX port:
   fixed goal, fixed metric, bounded mutable surface, keep-or-revert loop, and
   plateau stop condition.
3. Current LATTICE FRE and Copilot heavy-run practice:
   shell-safe prompt contracts, bounded execution scope, verifier-backed proof,
   no fake green, and repeated self-correction inside one run.

What we are building is not a verbatim copy of any of those.
It is a more advanced operational spin-off for project wrappers.

## Existing contract lineage

The wrapper model is not starting from zero.

There is already a richer bounded FRE proof-kernel surface in the sibling
evaluation worktree:

- `../lattice-worktrees/feat-fre-meta-harness-eval/meta/harness/fre/GOAL.md`
- `../lattice-worktrees/feat-fre-meta-harness-eval/meta/harness/fre/GoldenPath.md`
- `../lattice-worktrees/feat-fre-meta-harness-eval/meta/harness/fre/schemas/*`
- `../lattice-worktrees/feat-fre-meta-harness-eval/meta/harness/fre/examples/*`
- `../lattice-worktrees/feat-fre-meta-harness-eval/meta/harness/fre/tests/*`
- `../lattice-worktrees/feat-fre-meta-harness-eval/meta/harness/fre/docs/fre-to-lattice-map.md`

That worktree proves the missing point:
the wrapper contract already evolved beyond simple front matter and bottom
matter.

Its operative proof-kernel chain is:

```text
source -> schema -> examples -> validation -> metrics -> repair task -> promotion decision
```

The current wrapper work on `main` must therefore consolidate three layers of
truth:

1. existing FRE Notion pages
2. sibling FRE evaluation worktree artifacts
3. current `main` wrapper scaffolding

The next iteration should be a reconciliation pass, not a fresh invention pass.

## Fractal contract package

At every meaningful wrapper or bounded proof layer, the contract package should
be thought of as a seven-part proof bundle:

1. `source`
2. `schema`
3. `examples`
4. `expected-failures`
5. `tests`
6. `evaluation`
7. `promotion`

This package is separate from the five-file wrapper scaffold:

- `AGENTS.md`
- `CLAUDE.md`
- `MEMORY.md`
- `GOAL.md`
- `GOLDENPATH.md`

The five-file scaffold tells the agent how to operate at that level.
The seven-part contract package tells the harness how to prove, challenge, and
promote work at that level.

## Foundation hierarchy

The wrapper now needs an explicit substrate hierarchy:

1. Pixeltable is the foundation.
2. InfraNodus is the comparison and gap-analysis engine.
3. Notion is the workspace helper and always-updated narrative surface.

That distinction is non-negotiable.

Pixeltable is not just a storage detail.
It is the multimodal normalization and execution substrate that:

- holds the durable tables
- runs UDFs
- materializes computed columns
- records agent and evidence surfaces
- exports Arrow and Parquet for downstream consumers
- feeds DuckDB, Qdrant, SQLite-derived readers, and other downstream systems

Notion is not the foundation.
It is a collaborator workspace and note-taking assistant that must stay updated
so the team can reason from the same picture.

## InfraNodus as required comparison engine

InfraNodus is not an optional visualization side tool in this wrapper model.
It is the required graph comparison and gap-analysis engine for bounded wrapper
consolidation, drift detection, and promotion decisions.

Authoritative repo-local hook surfaces already exist:

- `analysis/infranodus/README.md`
- `analysis/capabilities/infranodus-capability-registry.yaml`
- `.claude/rules/infranodus-corpus.md`
- `meta/harness/bootstrap/build-gap-analysis.py`

The wrapper must therefore treat InfraNodus as a first-class comparison
surface:

1. every bounded consolidation slice should declare which corpus is being
   compared
2. every comparison-oriented slice should declare which InfraNodus tool is used
3. every graph comparison should emit a durable artifact
4. every gate that depends on structural comparison should name the
   corresponding InfraNodus artifact or report surface

InfraNodus is especially central to the later gates because it is the native
engine for:

- goal-versus-implementation drift
- discourse gap analysis
- corpus clustering and bridge detection
- graph-backed retrieval hints for proposer briefs

### Gate-by-gate InfraNodus role

#### Harvest gate

Use InfraNodus-normalized corpora and corpus-discipline checks to ensure the
harvest is structurally usable rather than a raw dump.

#### Registry gate

Use graph extraction and relation review to identify naming drift, alias
pressure, and disconnected capability terms.

#### Manifest gate

Use topical clusters and cross-surface comparison to detect placement drift
between matrix, registry, UI mirrors, and docs.

#### Verification gate

Use graph-backed diff and summary artifacts as evidence that the bounded proof
surface still matches its declared target.

#### State gate

Use InfraNodus comparison outputs to challenge unsupported green claims and to
surface exact amber or red gaps.

#### Health gate

This is the strongest mandatory hook.
Health requires drift detection, mismatch scans, and cross-surface comparison,
which InfraNodus is already wired to support.

#### Promotion gate

Use content gaps, bridges, and goal-vs-implementation diffs to decide whether
the slice is truly promotable or only locally improved.

## Gate-by-gate Pixeltable role

#### Harvest gate

Harvest should identify which Pixeltable tables, UDFs, computed columns, and
artifact namespaces the slice touches.

#### Registry gate

Registry entries should name the relevant Pixeltable surfaces explicitly so the
capability is not reduced to prose-only wiring.

#### Manifest gate

Manifest placement should make clear which tables and artifact inventories
represent the slice in the durable substrate.

#### Verification gate

Verification should prefer durable Pixeltable-backed artifact or inventory
surfaces over ephemeral terminal-only claims whenever the slice is mature
enough.

#### State gate

State claims should stay anchored to durable substrate facts, not only to docs
or chat summaries.

#### Health gate

Health needs both:

- Pixeltable substrate coherence
- InfraNodus comparison coherence

These are different and complementary.

#### Promotion gate

Promotion is only honest when the slice is legible both as:

- a durable substrate record in Pixeltable
- a comparison-backed claim challenged by InfraNodus

## Notion role

Notion should be treated as:

- workspace memory
- narrative coordination surface
- planning and communication helper

It must stay updated, but it is not the canonical execution substrate.

### Seven-part package roles

#### 1. Source

Research-grounded provenance and failure anticipation.

This is where the wrapper learns from:

- upstream docs
- GitHub issues and discussions
- historical failures
- Reddit, YouTube, and other public failure narratives when relevant
- local lineage and prior proof artifacts

The point is to kill likely problems before they are re-encountered blindly.

#### 2. Schema

Canonical machine-verifiable contract.

#### 3. Examples

Valid examples and representative fixtures.

#### 4. Expected failures

Anticipated failures and exact failure reasons.

This is not optional negative testing.
This is the explicit anticipation layer.

#### 5. Tests

Contract tests, schema tests, and failure-expectation tests.

#### 6. Evaluation

Scoring, gate results, run artifacts, determinism checks, and current-run
evidence.

#### 7. Promotion

Promotion decision, readiness judgment, blocker carry-forward, and advancement
to the next goal path.

## Parent and child roles

### Parent wrapper: `../meta/`

The parent wrapper is the reusable outer shell.

Its job is to:

- register body cells
- define wrapper-level contracts
- store workspace-level memory, evidence, runs, graph artifacts, and
  reproducibility metadata
- initialize project-local wrapper structure
- evaluate child wrapper health and gate state
- coordinate cross-project learnings

Visible current parent artifacts already support this role:

- `../meta/body-registry.yaml`
- `../meta/config.yaml`
- `../meta/bootstrap.md`
- `../meta/metaharness.lock.yaml`
- `../meta/{contracts,graph,memory,evidence,runs,docs}/`

### Child wrapper: `meta/`

The child wrapper is the project-local execution substrate.

Its job is to:

- hold project-specific goals, golden paths, and proof rules
- hold capability harvest, registry, matrix, manifest, and verifier surfaces
- expose project-local scoring and verification
- emit evidence back to the parent wrapper
- own the real bounded implementation loops for this repository

Visible current child artifacts already support this role:

- `meta/harness/GOAL.md`
- `meta/harness/golden_path.md`
- `meta/harness/bootstrap/run-autoresearch.sh`
- `meta/harness/docs/specs/agent-heavy-run-prompt-schema.md`
- `analysis/capabilities/*.yaml`
- `ddc/capability-matrix.yaml`

## Parent-child communication layer

The communication layer between parent and child should be explicit.

The parent wrapper should not guess the child state from chat history.
The child wrapper should not assume the parent has direct repo-local context.

The bridge should be built from durable artifacts:

1. child emits scored gate state
2. child emits proof artifacts and verification outcomes
3. child emits goal and golden-path identity
4. parent records wrapper-level run metadata and history
5. parent decides which gate is the current optimization target

The minimum bridge contract should be:

```yaml
wrapper_bridge_record:
  body_cell_id: string
  repo_root: string
  gate_id: string
  gate_version: string
  score: integer
  status: enum[red, amber, green]
  goal_path: string
  golden_path: string
  verifier_paths: [string]
  proof_artifacts: [string]
  blockers: [string]
  timestamp: datetime
```

## Schema hardening contract

The wrapper must not stop at markdown structure alone.

Front matter, bottom matter, gate records, bridge records, score outputs, and
proof summaries should all become machine-verifiable contracts.

The canonical validation strategy should be:

1. JSON Schema Draft 2020-12 as the language-neutral source of truth
2. Python validation through the `jsonschema` library and Pydantic models
3. TypeScript validation through Zod and generated TypeScript-friendly types
4. Cross-language parity checks so the same artifact can be validated in both
   Python and TypeScript

This avoids pigeonholing the wrapper into one language runtime.

### Canonical contract rule

The canonical schema should live as JSON Schema.

Everything else should be derived from it or checked against it:

- Python runtime validation
- Pydantic models
- TypeScript types
- Zod validators
- future Pixeltable ingestion contracts

### Minimum schema families

The wrapper layer should eventually define at least these schema families:

1. document front matter schema
2. document bottom matter schema
3. gate progress schema
4. harvest artifact schema
5. registry row schema
6. manifest row schema
7. verification artifact schema
8. bridge record schema
9. gate score result schema
10. promotion decision schema

These families already have a bounded precedent in the sibling FRE worktree:

- `fre-loop.schema.json`
- `gate-result.schema.json`
- `repair-task.schema.json`
- `promotion-decision.schema.json`

Those existing schema shapes should be treated as migration inputs for the
current wrapper model.

### Seven-part package mapping to schema families

The contract package should eventually have formal schemas or equivalent typed
contracts for:

- source records
- examples
- expected-failure records
- evaluation artifacts
- promotion decisions

Tests may stay language-native, but their inputs and outputs should still map
back to the canonical schemas where possible.

### Verification posture

The schema layer should be hardened in three separate ways:

- structural validity: schema itself parses and validates under Draft 2020-12
- runtime validity: emitted artifacts validate against the schema
- parity validity: Python and TypeScript validators accept and reject the same
  artifacts

### Tooling direction

Recommended baseline:

- JSON Schema Draft 2020-12
- Python `jsonschema`
- Pydantic
- Zod
- generated TypeScript types from the canonical schema set

The point is not to pick one validator.
The point is to make wrapper contracts portable and testable across the whole
system.

## The seven gates

These are not generic business domains.
They are the seven lifecycle gates of a capability in LATTICE.

### Gate 1: Harvest Gate

Question:
Did we extract the capability truth correctly?

Measures:

- source corpus identified
- source files or docs referenced
- raw harvest artifacts exist
- no invented capability rows
- initial capability boundaries are explicit

### Gate 2: Registry Gate

Question:
Is the harvested capability represented canonically?

Measures:

- canonical capability ID exists
- aliases or stale IDs resolved
- owner and scope defined
- dependencies declared
- registry row is present and coherent

### Gate 3: Manifest Gate

Question:
Is the capability placed correctly in the larger system?

Measures:

- matrix or manifest row exists
- TS or UI mirror is aligned where applicable
- goal and golden-path references exist if the capability is strategic
- dependency placement is coherent

### Gate 4: Verification Gate

Question:
Can we prove the capability actually works?

Measures:

- verifier exists
- verifier is real, not mock
- targeted tests exist
- runtime or proof commands exist
- proof artifact is emitted

### Gate 5: State Gate

Question:
Is the red, amber, and green state honest?

Measures:

- red means exact blocker
- amber means exact partial gap
- green means verifier-backed and proof-backed
- status matches matrix, registry, TS, docs, and proof surfaces

### Gate 6: Health Gate

Question:
Is the capability healthy in the repository right now?

Measures:

- no cross-surface drift
- no stale IDs
- no broken verifier path
- no dead documentation claims
- runtime assumptions still hold

### Gate 7: Promotion Gate

Question:
Is the capability ready to become part of the ship path?

Measures:

- it contributes to a real goal
- dependency chain is satisfied
- operator-facing value is explicit
- no unresolved critical blocker remains
- promotable into the next golden path or ship gate

## Red, amber, and green semantics

The seven gates explain why a capability is red, amber, or green.

### Red

- structural truth is missing
- or verifier truth is absent
- or dependency placement is still broken

Typical red causes:

- no verifier
- no canonical ID
- stale dependency naming
- no project-scoped proof
- runtime seam missing

### Amber

- capability exists
- registry and manifest exist
- verification is partial or bounded
- the blocker is operational, not conceptual

Typical amber causes:

- bounded proof only
- route works but project seam is weak
- proof exists but not end to end
- state drift remains across surfaces

### Green

- verifier-backed
- proof-backed
- cross-surface truth aligned
- dependency placement coherent
- no fake-green narrative needed

## FRE execution pattern per gate

Each gate should use the same outer loop pattern.

```text
goal -> golden path -> score -> bounded patch -> verify -> rescore -> keep or reject -> repeat until plateau
```

The gate loop stops when:

1. score increases no further
2. remaining blocker is proven real
3. widening scope would break the bounded mission

## Gate versioning rule

Do not silently change what `100` means inside an existing gate.

Rules:

- a gate definition is fixed for a given version
- a gate may stay at `100`
- if scope expands, create a new gate version or a downstream gate
- a gate score drops only because of regression or because its own verifier
  truth failed, not because a new gate was added elsewhere

This preserves trust in the harness.

## Current mapping in this repository

### Current realized gate

The current DDC foundation scorer is best treated as the first concrete gate
instance, even though it currently bundles several lifecycle concerns.

Current file:

- `scripts/score-ddc.sh`

Current meaning:

- DDC estimation substrate and governed Juniper foundation are green

Current status:

- saturated at `100`
- should now be frozen as a completed quality gate

### Next gate to implement

The next gate should not be more DDC substrate work.

It should be the next real dependency layer:

- Vectorworks or project entry path into the governed estimation flow

Recommended next scorer:

- `scripts/score-vw-estimation-path.sh`

## Recommended wrapper layout

The parent wrapper should eventually have reusable gate-level scaffolding.

Suggested shape:

```text
../meta/
  gates/
    harvest/
    registry/
    manifest/
    verification/
    state/
    health/
    promotion/
```

The child wrapper should eventually mirror the same concepts locally:

```text
meta/harness/gates/
  harvest/
  registry/
  manifest/
  verification/
  state/
  health/
  promotion/
```

Each gate should eventually own:

- `GOAL.md`
- `GOLDENPATH.md`
- scorer
- verifier
- state artifacts

## Immediate implementation policy

Do not try to implement all seven gates at once.

Sequence:

1. document the seven-gate wrapper model
2. freeze the current DDC scorer as the completed first quality gate
3. define the next gate contract
4. dry-run the wrapper-to-child communication plan
5. only then implement the next scorer and verifier

This keeps the system bounded and avoids destabilizing the current green
substrate.

---bottom-matter---
status_summary:
  completeness: 0.9
  confidence: high
  doc_state: draft
gate_progress:
  harvest:
    status: green
    notes: Seven-gate capability lifecycle is defined and bounded in this document.
  registry:
    status: green
    notes: Gate names and canonical meanings are normalized for wrapper-level use.
  manifest:
    status: green
    notes: Parent-wrapper and child-wrapper placement is documented explicitly.
  verification:
    status: amber
    notes: The gate model is defined, but no executable scorer template is attached yet.
  state:
    status: amber
    notes: The target lifecycle states are clear, but no machine-readable gate-state artifact exists yet.
  health:
    status: green
    notes: Cross-surface terminology is aligned with the current FRE and Meta-Harness direction.
  promotion:
    status: amber
    notes: The model is ready for dry-run adoption, pending the first implemented downstream gate.
open_questions:
  - Should the seven gates live under `../meta/gates/` first, or be templated in the child wrapper first?
  - Should gate weighting be defined now or deferred until Gate 2 exists?
pending_validations:
  - Confirm naming for gate directories and scorer files
  - Confirm parent-child bridge record shape against future Pixeltable ingestion needs
promotion_criteria:
  - Seven-gate model accepted as the canonical wrapper lifecycle
  - Parent-child bridge contract accepted for dry-run use
blocked_by: []
next_iteration:
  owner: meta-wrapper-agent
  objective: Draft Gate 2 and the bridge dry run without mutating runtime behavior.
