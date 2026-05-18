---
id: PLAN-FRE-WORKTREE-CONSOLIDATION-0001
slug: fre-worktree-consolidation-plan
title: FRE Worktree Consolidation Plan
doctype: plan
status: draft
version: 0.1.0
owner: meta-wrapper-agent
created_at: 2026-05-18
updated_at: 2026-05-18
wrapper_scope: main-vs-worktree-reconciliation
execution_mode: dry-run-first
source_worktree: ../lattice-worktrees/feat-fre-meta-harness-eval
notion_parent_page: https://www.notion.so/362c487604f481fcb505d19d6b85a0d4
related_docs:
  - meta/harness/docs/specs/fre-meta-wrapper-seven.gates.md
  - meta/harness/docs/specs/fre-meta-wrapper-implementation.plan.md
  - meta/harness/docs/specs/fre-infranodus-hook.plan.md
  - meta/harness/docs/specs/fre-pixeltable-hook.plan.md
---

# FRE Worktree Consolidation Plan

## Purpose

This plan reconciles the already-defined FRE contract from the sibling
evaluation worktree and the existing Notion FRE pages with the current wrapper
surfaces on `main`.

This is a consolidation gate.
It should happen before the next downstream gate implementation.

## Sources of truth under comparison

1. Notion FRE evaluation workspace
2. sibling worktree `lattice-worktrees/feat-fre-meta-harness-eval`
3. current `main` repo wrapper surfaces

## Worktree contract already present

The sibling evaluation worktree already contains:

- bounded `meta/harness/fre/` namespace
- `GOAL.md`
- `GoldenPath.md`
- `CLAUDE.md`
- schema files
- valid and invalid examples
- expected-failure contracts
- fixture artifacts
- evaluator and validator scripts
- tests
- translation map
- run artifacts

## Main-scaffold gaps identified

Current `main` has:

- fractal wrapper scaffold at parent, child, and harness layers
- wrapper seven-gate concept docs
- wrapper implementation plan docs

Current `main` is still missing:

- local seven-part contract package
- local schema family package
- expected-failure inventory
- evaluation and promotion inventory
- explicit InfraNodus hook inventory for wrapper comparison slices
- explicit Pixeltable hook inventory for wrapper substrate slices
- local translation-map inventory for wrapper terms
- local bridge-record schema
- direct reconciliation of `meta/harness/GOAL.md`, `MEMORY.md`, and
  `golden_path.md` with the worktree contract

## Consolidation questions

1. Which worktree artifacts should be adopted unchanged into `main`?
2. Which worktree artifacts should stay historical lineage only?
3. Which worktree terms require translation into the wrapper gate vocabulary?
4. Should `meta/harness/fre/` be restored on `main`, mirrored partially, or
   remain an external reference lane?
5. Which parts of the bounded FRE proof kernel become reusable wrapper
   contracts rather than one-off evaluation artifacts?

## Required mapping outputs

### 1. Namespace map

Map:

- Notion page
- worktree path
- current `main` path
- status: adopted, missing, renamed, historical, or superseded

### 2. Schema inventory

Inventory:

- schema name
- source worktree path
- intended wrapper role
- adopt as-is or translate

### 3. Seven-part contract-package inventory

Inventory:

- source
- schema
- examples
- expected-failures
- tests
- evaluation
- promotion

For each:

- worktree source
- current `main` state
- adopt, translate, mirror, or historical-only decision

### 4. Example inventory

Inventory:

- valid examples
- invalid examples
- expected-failure records
- whether each example belongs in the reusable wrapper layer

### 5. Translation inventory

Inventory:

- FRE term
- LATTICE term
- wrapper gate equivalent
- retain, translate, or reject

### 6. Runtime inventory

Inventory:

- evaluator scripts
- validator scripts
- report scripts
- tests
- whether they are reusable in the general wrapper or only in the bounded FRE
  lane

### 7. InfraNodus comparison inventory

Inventory:

- named graphs
- preferred tool map
- corpus-discipline rules
- graph artifact outputs
- which wrapper stages require InfraNodus-backed comparison
- which artifacts are required for promotion decisions

### 8. Pixeltable substrate inventory

Inventory:

- table families
- UDF or computed-column surfaces
- evidence and run namespaces
- Arrow and Parquet export surfaces
- which wrapper stages require durable substrate references
- which promotion decisions require durable table or artifact pointers

## Exit condition

This consolidation gate passes only when:

1. the Notion contract and worktree contract are mapped explicitly
2. the missing pieces on `main` are listed exactly
3. the next adoption or translation steps are ordered
4. the InfraNodus comparison hook is explicit rather than assumed
5. the Pixeltable substrate hook is explicit rather than assumed
6. no further wrapper invention is needed before the next implementation pass

---bottom-matter---
status_summary:
  completeness: 0.8
  confidence: high
  doc_state: draft
gate_progress:
  harvest:
    status: green
    notes: Notion pages, current main surfaces, and sibling worktree sources are all identified.
  registry:
    status: green
    notes: Source groups and comparison targets are named explicitly.
  manifest:
    status: amber
    notes: The mapping outputs are defined, but the actual line-by-line consolidation table is not written yet.
  verification:
    status: amber
    notes: The worktree contract is inspected, but no validator parity work has been ported to main yet.
  state:
    status: amber
    notes: The current main scaffold is honestly labeled as partial, not complete.
  health:
    status: green
    notes: The main source of drift is now identified as worktree versus main divergence rather than missing philosophy.
  promotion:
    status: red
    notes: No downstream wrapper gate should be promoted until this consolidation pass is complete.
open_questions:
  - Should `meta/harness/fre/` be restored directly on `main` or remain a historical sibling worktree lane?
  - Which FRE evaluation artifacts should become reusable wrapper primitives versus staying bounded-evaluation-only?
pending_validations:
  - Write the explicit namespace map
  - Write the schema family inventory
  - Write the translation inventory
promotion_criteria:
  - Worktree to main mapping is explicit
  - Wrapper contract gaps on main are enumerated exactly
  - Next adoption order is agreed
blocked_by: []
next_iteration:
  owner: meta-wrapper-agent
  objective: Produce the explicit worktree to main mapping table and mark adopt, translate, or keep-historical for each major FRE surface.
