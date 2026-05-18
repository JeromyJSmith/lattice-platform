---
id: GOLDENPATH-FRE-MAIN-SLICE-0001
slug: fre-main-contract-slice-golden-path
title: FRE main contract slice golden path
doctype: golden_path
status: draft
version: 0.1.0
owner: meta-wrapper-agent
created_at: 2026-05-18
updated_at: 2026-05-18
comparison_engine_refs:
  - analysis/infranodus/README.md
  - analysis/capabilities/infranodus-capability-registry.yaml
  - .claude/rules/infranodus-corpus.md
prompt_contract_refs:
  - meta/harness/docs/specs/agent-heavy-run-prompt-index.md
  - meta/harness/docs/specs/agent-heavy-run-prompt-schema.md
  - meta/harness/docs/specs/agent-heavy-run-prompt.schema.json
  - meta/harness/docs/specs/agent-heavy-run-prompt.template.yaml
  - meta/harness/docs/copilot-prompting-playbook.md
related_docs:
  - meta/harness/fre/GOAL.md
  - meta/harness/fre/source/provenance.json
  - meta/harness/fre/source/prompt-contract-trace.json
entrypoints:
  - uv run --project pixeltable python meta/harness/fre/harness/validate_schema.py
  - uv run --project pixeltable python meta/harness/fre/harness/validate_examples.py
  - uv run --project pixeltable pytest meta/harness/fre/tests -q
---

# FRE main contract slice golden path

## Purpose

This is the bounded execution path for the first proof-package slice restored on
`main`.

## Ordered path

1. Read the governed local consolidation docs.
2. Read the source provenance and prompt-contract trace.
3. Validate all schemas as schemas.
4. Validate valid and invalid examples.
5. Run the contract tests.
6. Re-read touched surfaces and compare the package inventory against the files.
7. Fail closed on any unresolved drift.

## Required outputs

The run is only complete when it can point to:

- source provenance
- schema family files
- valid and invalid examples
- expected-failure registry
- contract tests
- evaluation inventory
- promotion inventory

---bottom-matter---
status_summary:
  completeness: 0.6
  confidence: high
  doc_state: draft
gate_progress:
  - gate_id: harvest
    status: green
    notes: The execution path is grounded in the local consolidation documents.
    comparison_required: false
  - gate_id: registry
    status: green
    notes: The proof-package inventory names the restored surfaces explicitly.
    comparison_required: false
  - gate_id: manifest
    status: amber
    notes: The first reusable schema family exists, but the remaining worktree families are still pending.
    comparison_required: false
  - gate_id: verification
    status: amber
    notes: Verification depends on schema validation, example validation, and contract tests passing together.
    comparison_required: true
    comparison_engine: infranodus
    comparison_artifacts:
      - analysis/infranodus/goal-vs-implementation.diff.json
  - gate_id: state
    status: green
    notes: Evaluation and promotion remain explicit and separate in the run path.
    comparison_required: false
  - gate_id: health
    status: amber
    notes: The slice is small by design, so broader parity drift still has to be reviewed later.
    comparison_required: true
    comparison_engine: infranodus
    comparison_artifacts:
      - analysis/infranodus/goal-vs-implementation.diff.json
  - gate_id: promotion
    status: red
    notes: Promotion is blocked until the minimal slice is validated cleanly on main.
    comparison_required: true
    comparison_engine: infranodus
    comparison_artifacts:
      - analysis/infranodus/goal-vs-implementation.diff.json
      - analysis/infranodus/infranodus-schema-map.md
open_questions:
  - Should later parity work keep this lane bounded or fold it into more general wrapper contracts?
pending_validations:
  - Re-check the prompt-contract trace after any future heavy-run prompt changes.
promotion_criteria:
  - The ordered validation path stays bounded and repeatable.
  - No proof-package part is implied by another part.
blocked_by: []
next_iteration:
  owner: meta-wrapper-agent
  objective: Keep the slice bounded while extending schema parity only when the current contract remains clean.
