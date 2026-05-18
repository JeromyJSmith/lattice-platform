---
id: PLAN-FRE-FRACTAL-CONTRACT-PACKAGE-0001
slug: fre-fractal-contract-package-plan
title: FRE Fractal Contract Package
doctype: plan
status: draft
version: 0.1.0
owner: meta-wrapper-agent
created_at: 2026-05-18
updated_at: 2026-05-18
wrapper_scope: fractal-contract-package
execution_mode: dry-run-first
related_docs:
  - meta/harness/docs/specs/fre-meta-wrapper-seven.gates.md
  - meta/harness/docs/specs/fre-meta-wrapper-implementation.plan.md
  - meta/harness/docs/specs/fre-infranodus-hook.plan.md
  - meta/harness/docs/specs/fre-pixeltable-hook.plan.md
  - meta/harness/docs/specs/fre-worktree-consolidation.plan.md
  - meta/harness/docs/specs/fre-worktree-consolidation.map.md
  - meta/harness/docs/specs/agent-heavy-run-prompt-index.md
  - meta/harness/docs/specs/agent-heavy-run-prompt-schema.md
  - meta/harness/docs/specs/agent-heavy-run-prompt.schema.json
  - meta/harness/docs/specs/agent-heavy-run-prompt.template.yaml
  - meta/harness/docs/copilot-prompting-playbook.md
---

# FRE Fractal Contract Package

## Purpose

This document defines the seven-part proof package that should exist at any
meaningful wrapper or bounded capability-evaluation layer.

It is separate from the five-file wrapper scaffold.

## The five-file wrapper scaffold

Every layer should expose:

- `AGENTS.md`
- `CLAUDE.md`
- `MEMORY.md`
- `GOAL.md`
- `GOLDENPATH.md`

These files define operating context.

## The seven-part contract package

Every proof-bearing layer should also expose a seven-part contract package:

1. `source`
2. `schema`
3. `examples`
4. `expected-failures`
5. `tests`
6. `evaluation`
7. `promotion`

These define proof context, proof rules, and advancement criteria.

## Package roles

### 1. Source

Research-grounded provenance and failure anticipation.

This includes:

- upstream documentation
- GitHub issues and discussions
- Reddit, YouTube, and public failure narratives where relevant
- historical local failures
- source normalization notes

### 2. Schema

Canonical machine-verifiable contract.

The preferred canonical language is JSON Schema Draft 2020-12.

### 3. Examples

Valid examples and representative fixtures that should pass.

### 4. Expected failures

Anticipated failure cases and exact expected failure reasons.

This is the anticipation layer.
It exists to kill likely failures before they are re-encountered in the loop.

### 5. Tests

Contract tests, schema tests, and failure-expectation tests.

### 6. Evaluation

Scoring, gate results, reports, current-run evidence, determinism checks, and
other run-artifact outputs.

### 7. Promotion

Promotion decision, readiness judgment, blocker carry-forward, and movement to
the next goal or release path.

## Canonical chain

The working chain is:

```text
source -> schema -> examples -> expected-failures -> tests -> evaluation -> promotion
```

This is stronger than a simple schema-plus-tests view because evaluation and
promotion remain explicit artifact layers.

## InfraNodus hook across the package

InfraNodus is the required graph-analysis engine for any proof package that
needs corpus comparison, gap detection, drift analysis, or promotion
challenging.

It should be hooked into the seven parts like this:

1. `source`
   - normalized comparison corpora
   - source-quality and packaging notes
2. `schema`
   - graph artifact schemas or references to graph-result contracts
3. `examples`
   - example corpora and expected graph or diff shapes
4. `expected-failures`
   - malformed corpora, mixed-purpose corpora, or structurally weak corpora
5. `tests`
   - exact-failure tests for corpus packaging and graph artifact shape
6. `evaluation`
   - actual gap-analysis, difference, hint, or cluster artifacts
7. `promotion`
   - promotion decision that references the comparison outputs rather than
     prose-only judgment

The authoritative local hook surfaces are:

- `analysis/infranodus/README.md`
- `analysis/capabilities/infranodus-capability-registry.yaml`
- `.claude/rules/infranodus-corpus.md`

## Cross-language validation rule

The contract package should be verifiable across multiple runtimes:

- JSON Schema Draft 2020-12 as the canonical contract language
- Python `jsonschema`
- Pydantic
- Zod
- TypeScript-compatible generated or aligned types

## Prompt contract hook

The prompting schema is a non-negotiable sibling contract for every heavy or
bounded execution prompt.

Canonical prompt-contract surfaces:

- `meta/harness/docs/specs/agent-heavy-run-prompt-index.md`
- `meta/harness/docs/specs/agent-heavy-run-prompt-schema.md`
- `meta/harness/docs/specs/agent-heavy-run-prompt.schema.json`
- `meta/harness/docs/specs/agent-heavy-run-prompt.template.yaml`
- `meta/harness/docs/copilot-prompting-playbook.md`

These define the governed prompt shape that should be used every time a prompt
is composed for Copilot or another execution agent.

The hook rule is:

1. every execution prompt should trace back to the prompt schema
2. every prompt instance should be expressible through the template fields
3. every heavy-run prompt should be reviewable against the schema blocks:
   - `mode`
   - `mission`
   - `current_verified_state`
   - `hard_rules`
   - `allowed_paths`
   - `disallowed_paths`
   - `tasks`
   - `validation_loop`
   - `success_criteria`
   - `report_contract`

If a prompt cannot be mapped back to that contract, it is malformed.

## Pixeltable hook across the package

Pixeltable is the foundational substrate for the proof package.

The package should therefore be able to answer, for any serious slice:

1. which durable tables hold it
2. which UDFs or computed-column surfaces normalize it
3. which evidence or run inventories record it
4. which Arrow or Parquet outputs expose it to downstream consumers

The hook across the seven parts is:

1. `source`
   - source inventories should name upstream Pixeltable tables or intended
     table families
2. `schema`
   - schema families should reserve room for durable substrate pointers
3. `examples`
   - examples should show table or artifact references when relevant
4. `expected-failures`
   - failures should include missing-table, missing-artifact, or missing-UDF
     cases where those are part of the contract
5. `tests`
   - tests should validate substrate-bearing fields when the slice depends on
     them
6. `evaluation`
   - evaluation should point at durable inventories, not only transient output
7. `promotion`
   - promotion should be able to cite the durable Pixeltable substrate and the
     comparison evidence together

Notion remains the workspace helper that mirrors and explains the slice, but it
does not replace the substrate.

## Immediate implication for main

Current `main` already has parts of the wrapper scaffold.
It does not yet have the full seven-part contract package.

That means the next consolidation work should port the package in this order:

1. source
2. schema
3. examples
4. expected-failures
5. tests
6. evaluation
7. promotion

---bottom-matter---
status_summary:
  completeness: 0.95
  confidence: high
  doc_state: draft
gate_progress:
  harvest:
    status: green
    notes: The seven-part package is derived from actual worktree and Notion contract lineage.
  registry:
    status: green
    notes: The package parts are named explicitly and consistently.
  manifest:
    status: green
    notes: The package is clearly separated from the five-file wrapper scaffold.
  verification:
    status: amber
    notes: The package definition is clear, but the package contents are not yet fully ported to main.
  state:
    status: green
    notes: Evaluation and promotion are now explicitly restored as distinct layers.
  health:
    status: green
    notes: The correction closes the earlier incomplete five-part interpretation.
  promotion:
    status: amber
    notes: The package is defined, but still needs concrete adoption into main.
open_questions:
  - Which evaluation artifacts should stay bounded to the historical FRE lane versus become reusable wrapper-level primitives?
pending_validations:
  - Port source inventory shape
  - Port evaluation artifact inventory
  - Port promotion artifact inventory
promotion_criteria:
  - Seven-part package is accepted as canonical
  - The first package slice is ported to main
blocked_by: []
next_iteration:
  owner: meta-wrapper-agent
  objective: Port the first seven-part package slice from the FRE worktree into main.
