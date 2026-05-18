---
id: PLAN-FRE-PIXELTABLE-HOOK-0001
slug: fre-pixeltable-hook-plan
title: FRE Pixeltable Hook Plan
doctype: plan
status: draft
version: 0.1.0
owner: meta-wrapper-agent
created_at: 2026-05-18
updated_at: 2026-05-18
wrapper_scope: pixeltable-foundational-substrate
execution_mode: dry-run-first
related_docs:
  - meta/ARCHITECTURE.md
  - meta/harness/docs/specs/fre-meta-wrapper-seven.gates.md
  - meta/harness/docs/specs/fre-fractal-contract-package.plan.md
  - meta/harness/docs/specs/fre-worktree-consolidation.map.md
  - analysis/infranodus/infranodus-capability-manifest.yaml
---

# FRE Pixeltable Hook Plan

## Purpose

This document makes Pixeltable explicit as the foundational substrate in the
FRE Meta-Wrapper contract.

Pixeltable is not just storage.
It is the multimodal normalization and execution layer that everything durable
feeds through.

## Foundational role

Pixeltable is the substrate that:

- holds the durable tables
- runs UDFs
- materializes computed columns
- records runs, evidence, and artifacts
- normalizes multimodal inputs
- exports Arrow and Parquet outputs
- feeds downstream consumers such as DuckDB, Qdrant, and SQLite-derived
  readers

Notion is not this layer.
Notion is the workspace helper that must stay updated so the team can think and
coordinate from the same picture.

## Non-negotiable wrapper rule

If a bounded slice is durable enough to be part of the wrapper contract, it
must declare its Pixeltable substrate hook.

That hook should name, when applicable:

1. the table family or namespace
2. the UDF or computed-column normalization surface
3. the evidence or artifact namespace
4. the Arrow or Parquet export surface
5. the downstream consumers that depend on the normalized output

## Hook by lifecycle gate

### Harvest gate

Identify which Pixeltable tables, namespaces, UDFs, and computed columns the
slice touches or intends to create.

### Registry gate

Registry rows should name the durable substrate surfaces explicitly when the
capability is more than a transient document contract.

### Manifest gate

Manifest placement should show how the slice appears in durable table or
artifact inventories.

### Verification gate

Verification should prefer durable artifact or inventory pointers rather than
terminal-only claims whenever the slice is mature enough.

### State gate

State claims should be traceable to substrate facts, not only prose.

### Health gate

Health requires both durable substrate coherence and comparison coherence.

### Promotion gate

Promotion should be able to cite the substrate record and the comparison record
together.

## Hook by proof-package part

### Source

Source inventories should point at relevant substrate families or intended
table destinations.

### Schema

Schema families should make room for durable substrate references.

### Examples

Examples should include substrate pointers where they are part of the contract.

### Expected failures

Expected failures should include missing-table, missing-artifact, or
missing-normalizer cases when relevant.

### Tests

Tests should validate substrate-bearing fields when the slice depends on them.

### Evaluation

Evaluation should record durable inventories and outputs, not only transient
logs.

### Promotion

Promotion should be able to cite the substrate and comparison evidence
together.

## Immediate implementation sequence

1. add Pixeltable references to the wrapper gate spec
2. add Pixeltable references to the seven-part contract-package spec
3. add Pixeltable to the consolidation map
4. require explicit substrate references in future serious schema families
5. keep Notion updated as the helper workspace, but do not confuse it with the
   substrate

---bottom-matter---
status_summary:
  completeness: 0.95
  confidence: high
  doc_state: draft
gate_progress:
  - gate_id: harvest
    status: green
    notes: The foundational Pixeltable role is identified explicitly.
    comparison_required: false
  - gate_id: registry
    status: green
    notes: The required hook fields are explicit for future durable capability rows.
    comparison_required: false
  - gate_id: manifest
    status: green
    notes: Pixeltable is mapped across lifecycle and proof-package surfaces.
    comparison_required: false
  - gate_id: verification
    status: amber
    notes: Existing schema families still need explicit substrate fields where applicable.
    comparison_required: false
  - gate_id: state
    status: green
    notes: The hierarchy between Pixeltable and Notion is now explicit.
    comparison_required: false
  - gate_id: health
    status: green
    notes: Substrate coherence and comparison coherence are separated clearly.
    comparison_required: false
  - gate_id: promotion
    status: amber
    notes: Future promotion records still need to adopt substrate pointers in practice.
    comparison_required: false
open_questions:
  - Which first FRE schema family should carry explicit Pixeltable substrate fields beyond inventories?
pending_validations:
  - Add explicit substrate-bearing fields to the next durable schema families
  - Mirror the hierarchy in the Notion wrapper pages
promotion_criteria:
  - Wrapper docs all reference the Pixeltable hook
  - Consolidation map includes the Pixeltable inventory
  - Future durable slices declare substrate pointers explicitly
blocked_by: []
next_iteration:
  owner: meta-wrapper-agent
  objective: Use Pixeltable as the substrate model for the next durable schema and promotion surfaces.
