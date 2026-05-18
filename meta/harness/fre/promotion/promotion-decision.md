---
id: PROMOTION-FRE-MAIN-SLICE-0003
slug: fre-main-slice-promotion-decision
title: FRE main slice promotion decision (third slice — 2026-05-18 seven-phase run)
doctype: promotion_decision
status: ready
version: 0.2.0
owner: meta-wrapper-agent
created_at: 2026-05-18
updated_at: 2026-05-18
run_id: HARVEST-FRE-INFRANODUS-20260518-7PHASE
comparison_engine: infranodus
comparison_engine_refs:
  - analysis/infranodus/README.md
  - analysis/capabilities/infranodus-capability-registry.yaml
  - analysis/infranodus/infranodus-capability-manifest.yaml
  - analysis/infranodus/infranodus-schema-map.md
  - analysis/infranodus/infranodus-capability-harvest.md
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
  - meta/harness/fre/evaluation/evaluation-comparison-summary.json
---

# FRE main slice promotion decision (third slice — 2026-05-18 seven-phase run)

## Decision

Promotable as an honest bounded improvement. This third-slice record supersedes
PROMOTION-FRE-MAIN-SLICE-0002 and reflects the 2026-05-18 seven-phase FRE run.

The second slice extended the schema family from four to eight by porting
`fre-loop`, `gate-result`, `repair-task`, and `promotion-decision`. This run
confirms those schemas are clean, corrects a lifecycle_phases drift in
`prompt-contract-trace.json` (phase names had drifted to proof-package part
names), adds the missing `gate-result` failure mode to the capability registry,
extends the manifest examples artifacts to 20 fixture paths, and produces the
evaluation-phase InfraNodus comparison summary as a new evidence artifact.

The comparison-engine pattern is applied only where the data flow requires it:
`gate-result` conditionally on the three lifecycle comparison gates
(verification, health, promotion) and `promotion-decision` unconditionally.
`fre-loop` and `repair-task` remain non-comparison-bearing.

## Required comparison mapping

- scope surface: `meta/harness/fre/source/provenance.json#/infranodus_scope`
- manifest surface: `analysis/infranodus/infranodus-capability-manifest.yaml`
- schema map surface: `analysis/infranodus/infranodus-schema-map.md`

## Required evidence

- `analysis/infranodus/goal-vs-implementation.diff.json`
- `analysis/infranodus/infranodus-schema-map.md`
- `analysis/infranodus/infranodus-capability-harvest.md`
- `analysis/infranodus/infranodus-capability-manifest.yaml`
- `analysis/capabilities/infranodus-capability-registry.yaml`
- `meta/harness/fre/evaluation/artifacts-inventory.json`
- `meta/harness/fre/evaluation/schema-validation.json`
- `meta/harness/fre/evaluation/example-validation.json`
- `meta/harness/fre/evaluation/contract-tests.txt`
- `meta/harness/fre/evaluation/evaluation-comparison-summary.json`

## Promotion rule

Do not promote from evaluation alone. Promotion is only honest when the bounded
validation loop is clean and the comparison mapping plus evidence remain
explicit.

## InfraNodus evidence note (Phase 7 step — 2026-05-18)

No new InfraNodus comparison run was performed during the promotion phase in
this session. Promotion relies on the exact evidence paths already present from
the source through evaluation phases:

- `analysis/infranodus/infranodus-capability-harvest.md`
- `analysis/capabilities/infranodus-capability-registry.yaml`
- `analysis/infranodus/infranodus-capability-manifest.yaml`
- `analysis/infranodus/infranodus-schema-map.md`
- `analysis/infranodus/goal-vs-implementation.diff.json`
- `meta/harness/fre/evaluation/evaluation-comparison-summary.json`

This keeps the promotion record honest: promotable with zero blockers based on
existing bounded evidence, not on an invented Phase 7 InfraNodus result.

---bottom-matter---
status_summary:
  completeness: 1.0
  confidence: high
  doc_state: active
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
    notes: Promotion is explicitly evidence-backed and remains distinct from evaluation. InfraNodus evidence pointers verified in 2026-05-18 seven-phase run.
    comparison_required: true
    comparison_engine: infranodus
    comparison_artifacts:
      - analysis/infranodus/goal-vs-implementation.diff.json
      - analysis/infranodus/infranodus-schema-map.md
      - analysis/infranodus/infranodus-capability-harvest.md
      - meta/harness/fre/evaluation/evaluation-comparison-summary.json
open_questions: []
pending_validations: []
promotion_criteria:
  - Promotion cites comparison mapping and evidence explicitly.
  - The bounded validation loop stays clean.
blocked_by: []
next_iteration:
  owner: meta-wrapper-agent
  objective: Preserve the bounded InfraNodus hook contract while extending future parity work without broadening this slice.
