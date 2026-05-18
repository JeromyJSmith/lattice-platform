---
id: PLAN-FRE-INFRANODUS-HOOK-0001
slug: fre-infranodus-hook-plan
title: FRE InfraNodus Hook Plan
doctype: plan
status: draft
version: 0.1.0
owner: meta-wrapper-agent
created_at: 2026-05-18
updated_at: 2026-05-18
wrapper_scope: infranodus-comparison-engine
execution_mode: dry-run-first
related_docs:
  - analysis/infranodus/README.md
  - analysis/capabilities/infranodus-capability-registry.yaml
  - .claude/rules/infranodus-corpus.md
  - meta/harness/docs/specs/fre-meta-wrapper-seven.gates.md
  - meta/harness/docs/specs/fre-fractal-contract-package.plan.md
  - meta/harness/docs/specs/fre-worktree-consolidation.map.md
  - meta/harness/docs/specs/agent-heavy-run-prompt-index.md
---

# FRE InfraNodus Hook Plan

## Purpose

This document makes InfraNodus an explicit, mandatory comparison engine inside
the FRE Meta-Wrapper contract.

InfraNodus is already present in the repository as:

- an MCP server surface
- a harvested capability registry
- a corpus-discipline rule
- a gap-analysis artifact workspace

What is missing is the wrapper-level hook that says when and how it must be
used.

## Authoritative local surfaces

The local source-of-truth surfaces are:

- `analysis/infranodus/README.md`
- `analysis/capabilities/infranodus-capability-registry.yaml`
- `.claude/rules/infranodus-corpus.md`
- `meta/harness/bootstrap/build-gap-analysis.py`

These already define:

- named graphs
- preferred tool choices
- corpus normalization rules
- artifact output patterns

## Non-negotiable wrapper rule

If a bounded slice involves any of the following:

- goal versus implementation comparison
- cross-surface drift detection
- capability wording or dependency normalization
- graph-backed retrieval hinting
- gap analysis used to justify repair or promotion

then the slice must declare an InfraNodus hook.

That hook must name:

1. the corpus or corpora under comparison
2. the InfraNodus tool or tool sequence used
3. the expected output artifact
4. how the artifact affects gate state or promotion

## Hook by lifecycle gate

### Harvest gate

Require corpus-discipline compliance and source normalization before graph
analysis artifacts are trusted.

### Registry gate

Use InfraNodus to surface term drift, alias pressure, and disconnected naming.

### Manifest gate

Use clustering and comparison outputs to detect inconsistent placement across
matrix, registry, docs, and UI mirrors.

### Verification gate

Use graph comparison outputs as evidence that the verified slice still matches
its declared target surfaces.

### State gate

Use graph-based diffs and gap outputs to challenge unsupported green claims and
to justify exact amber or red blockers.

### Health gate

Require an InfraNodus-backed comparison artifact for any slice that claims
cross-surface health or drift closure.

### Promotion gate

Require the promotion decision to reference comparison artifacts when
promotion depends on closing structural gaps or wording drift.

## Hook by proof-package part

### Source

Provide normalized corpora and provenance notes.

### Schema

Provide graph artifact schemas or explicit graph-output contracts.

### Examples

Provide example corpora and expected comparison outputs.

### Expected failures

Provide malformed or mixed-purpose corpora that should fail structurally or
fail the declared comparison rules.

### Tests

Provide tests that validate corpus packaging and artifact shape or exact
failure reasons.

### Evaluation

Provide actual InfraNodus outputs:

- difference artifacts
- gap-analysis artifacts
- contextual hints
- cluster reports

### Promotion

Provide decision records that cite those outputs rather than freeform prose.

## Prompt-contract hook

Any heavy or bounded prompt that depends on structural comparison should
include an explicit InfraNodus section inside its governed task and validation
blocks.

At minimum it should specify:

- corpus scope
- comparison purpose
- output artifact expectation
- stop condition if the graph comparison is missing or inconclusive

If the prompt omits this for a comparison-bearing slice, the prompt is
incomplete.

## Immediate implementation sequence

1. add InfraNodus references to the wrapper gate spec
2. add InfraNodus references to the seven-part contract-package spec
3. add InfraNodus to the worktree-to-main consolidation map
4. require an explicit InfraNodus comparison inventory in future ports
5. later, port any missing schema or artifact contracts that formalize the
   comparison outputs

---bottom-matter---
status_summary:
  completeness: 0.95
  confidence: high
  doc_state: draft
gate_progress:
  harvest:
    status: green
    notes: The existing local InfraNodus surfaces are identified and grounded.
  registry:
    status: green
    notes: The mandatory hook fields and authoritative local surfaces are explicit.
  manifest:
    status: green
    notes: The hook is mapped across lifecycle gates and proof-package parts.
  verification:
    status: amber
    notes: The wrapper hook is defined, but artifact schemas and tests are not yet ported.
  state:
    status: green
    notes: InfraNodus is now treated as required comparison infrastructure rather than optional tooling.
  health:
    status: green
    notes: The repo-level drift and gap-analysis role is explicitly anchored to existing local surfaces.
  promotion:
    status: amber
    notes: The hook is defined, but future prompts and ports still need to enforce it in practice.
open_questions:
  - Which InfraNodus artifact outputs should get their own schema family on main first?
pending_validations:
  - Wire explicit InfraNodus sections into future bounded prompt instances
  - Port any missing graph artifact schemas or example fixtures
promotion_criteria:
  - Wrapper docs all reference the InfraNodus hook
  - Consolidation map includes the InfraNodus inventory
  - Future comparison-bearing prompts declare an InfraNodus hook explicitly
blocked_by: []
next_iteration:
  owner: meta-wrapper-agent
  objective: Treat InfraNodus as mandatory comparison infrastructure in the first reusable contract-package port.
