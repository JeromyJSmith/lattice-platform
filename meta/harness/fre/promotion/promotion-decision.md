---
id: PROMOTION-FRE-MAIN-SLICE-0002
slug: fre-main-slice-promotion-decision
title: FRE main slice promotion decision (second slice)
doctype: promotion_decision
status: draft
version: 0.1.0
owner: meta-wrapper-agent
created_at: 2026-05-18
updated_at: 2026-05-18
comparison_engine_refs:
  - analysis/infranodus/README.md
  - analysis/capabilities/infranodus-capability-registry.yaml
  - analysis/infranodus/infranodus-capability-manifest.yaml
  - analysis/infranodus/infranodus-schema-map.md
prompt_contract_refs:
  - meta/harness/docs/specs/agent-heavy-run-prompt-index.md
  - meta/harness/docs/specs/agent-heavy-run-prompt-schema.md
  - meta/harness/docs/specs/agent-heavy-run-prompt.schema.json
  - meta/harness/docs/specs/agent-heavy-run-prompt.template.yaml
  - meta/harness/docs/copilot-prompting-playbook.md
related_docs:
  - meta/harness/fre/GOAL.md
  - meta/harness/fre/GOLDENPATH.md
  - meta/harness/fre/promotion/readiness-summary.json
---

# FRE main slice promotion decision (second slice)

## Decision

Promotable as an honest bounded improvement. Second slice extends the schema
family from four to eight by porting `fre-loop`, `gate-result`, `repair-task`,
and `promotion-decision` from the sibling worktree. The comparison-engine
pattern is applied only where the data flow requires it: `gate-result`
conditionally on the three lifecycle comparison gates (verification, health,
promotion) and `promotion-decision` unconditionally. `fre-loop` and
`repair-task` remain non-comparison-bearing because their data flow records
orchestration and remediation respectively, not cross-corpus comparison.

## Required comparison mapping

- scope surface: `meta/harness/fre/source/provenance.json#/infranodus_scope`
- manifest surface: `analysis/infranodus/infranodus-capability-manifest.yaml`
- schema map surface: `analysis/infranodus/infranodus-schema-map.md`

## Required evidence

- `analysis/infranodus/goal-vs-implementation.diff.json`
- `analysis/infranodus/infranodus-schema-map.md`
- `meta/harness/fre/evaluation/artifacts-inventory.json`
- `meta/harness/fre/evaluation/schema-validation.json`
- `meta/harness/fre/evaluation/example-validation.json`
- `meta/harness/fre/evaluation/contract-tests.txt`

## Promotion rule

Do not promote from evaluation alone. Promotion is only honest when the bounded
validation loop is clean and the comparison mapping plus evidence remain
explicit.

---bottom-matter---
status_summary:
  completeness: 0.95
  confidence: high
  doc_state: ready
gate_progress:
  - gate_id: harvest
    status: green
    notes: The promotion record names the authoritative comparison surfaces.
    comparison_required: false
  - gate_id: registry
    status: green
    notes: The InfraNodus scope is traced back to the harvested registry rows.
    comparison_required: false
  - gate_id: manifest
    status: green
    notes: Promotion declares the proof-part comparison mapping explicitly.
    comparison_required: false
  - gate_id: verification
    status: green
    notes: Draft 2020-12 schema validation, example validation, pytest, and git diff checks are all clean.
    comparison_required: true
    comparison_engine: infranodus
    comparison_artifacts:
      - analysis/infranodus/goal-vs-implementation.diff.json
  - gate_id: state
    status: green
    notes: Promotion remains separate from evaluation and test execution.
    comparison_required: false
  - gate_id: health
    status: green
    notes: Provenance, evaluation inventory, promotion inventory, and prompt trace agree on InfraNodus dependencies.
    comparison_required: true
    comparison_engine: infranodus
    comparison_artifacts:
      - analysis/infranodus/goal-vs-implementation.diff.json
  - gate_id: promotion
    status: green
    notes: Promotion is explicitly evidence-backed and remains distinct from evaluation.
    comparison_required: true
    comparison_engine: infranodus
    comparison_artifacts:
      - analysis/infranodus/goal-vs-implementation.diff.json
      - analysis/infranodus/infranodus-schema-map.md
open_questions: []
pending_validations: []
promotion_criteria:
  - Promotion cites comparison mapping and evidence explicitly.
  - The bounded validation loop stays clean.
blocked_by: []
next_iteration:
  owner: meta-wrapper-agent
  objective: Preserve the bounded InfraNodus hook contract while extending future parity work without broadening this slice.
