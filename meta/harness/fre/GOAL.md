---
id: GOAL-FRE-MAIN-SLICE-0001
slug: fre-main-contract-slice-goal
title: FRE main contract slice goal
doctype: goal
status: draft
version: 0.1.0
owner: meta-wrapper-agent
created_at: 2026-05-18
updated_at: 2026-05-18
comparison_engine_refs:
  - analysis/infranodus/README.md
  - analysis/capabilities/infranodus-capability-registry.yaml
  - .claude/rules/infranodus-corpus.md
library_refs:
  - meta/harness/library.yaml
  - meta/harness/agentics-library.md
  - analysis/capabilities/the-library-capability-registry.yaml
substrate_refs:
  - meta/harness/pixeltable-operational-substrate.md
  - meta/ARCHITECTURE.md
  - analysis/capabilities/pixeltable-capability-registry.yaml
  - projects/template/library.yaml
prompt_contract_refs:
  - meta/harness/docs/specs/agent-heavy-run-prompt-index.md
  - meta/harness/docs/specs/agent-heavy-run-prompt-schema.md
  - meta/harness/docs/specs/agent-heavy-run-prompt.schema.json
  - meta/harness/docs/specs/agent-heavy-run-prompt.template.yaml
  - meta/harness/docs/copilot-prompting-playbook.md
related_docs:
  - meta/harness/docs/specs/fre-worktree-consolidation.map.md
  - meta/harness/docs/specs/fre-worktree-consolidation.plan.md
  - meta/harness/docs/specs/fre-fractal-contract-package.plan.md
---

# FRE main contract slice goal

## Mission

Restore the first proof-bearing FRE slice on `main` without collapsing the three
authoritative contracts:

- lifecycle gates governance
- proof package completeness
- heavy-run prompt governance

## Scope

This slice is intentionally narrow:

1. restore source provenance and normalization stubs
2. create the first reusable schema family package
3. add valid and invalid examples with expected-failure coverage
4. make evaluation and promotion explicit inventories

## Exit condition

This slice is only honest when:

1. the new schema families validate under Draft 2020-12,
2. valid examples pass,
3. invalid examples fail for expected reasons,
4. document-contract and lattice-mapping tests hold,
5. evaluation and promotion remain separate proof-package parts.

---bottom-matter---
status_summary:
  completeness: 0.55
  confidence: high
  doc_state: draft
gate_progress:
  - gate_id: harvest
    status: green
    notes: Local authority docs and sibling worktree artifacts are mapped.
    comparison_required: false
  - gate_id: registry
    status: green
    notes: The first proof-package inventory is restored under source provenance.
    comparison_required: false
  - gate_id: manifest
    status: amber
    notes: The initial schema and example families are present, but not full worktree parity.
    comparison_required: false
  - gate_id: verification
    status: amber
    notes: Schema, example, and contract tests are the first verification layer.
    comparison_required: true
    comparison_engine: infranodus
    comparison_artifacts:
      - analysis/infranodus/goal-vs-implementation.diff.json
  - gate_id: state
    status: green
    notes: Evaluation and promotion are explicit inventories instead of implied steps.
    comparison_required: false
  - gate_id: health
    status: amber
    notes: Drift still has to be checked against the sibling worktree beyond this minimal slice.
    comparison_required: true
    comparison_engine: infranodus
    comparison_artifacts:
      - analysis/infranodus/goal-vs-implementation.diff.json
  - gate_id: promotion
    status: red
    notes: This slice is not promotable until the targeted checks pass on main.
    comparison_required: true
    comparison_engine: infranodus
    comparison_artifacts:
      - analysis/infranodus/goal-vs-implementation.diff.json
      - analysis/infranodus/infranodus-schema-map.md
open_questions:
  - Which evaluation-only fixtures should remain historical lineage instead of moving into the reusable lane?
pending_validations:
  - Validate all new schemas as Draft 2020-12 schemas.
  - Validate all valid and invalid examples against the canonical schemas.
promotion_criteria:
  - The seven-part slice exists on main with explicit inventories.
  - Expected-failure matching is green.
blocked_by: []
next_iteration:
  owner: meta-wrapper-agent
  objective: Expand from the first schema family slice into broader worktree parity without changing the governed contracts.
