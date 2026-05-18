---
id: "meta-harness-absorption-validation"
slug: "meta-harness-absorption-validation"
doctype: "plan"
status: "active"
version: "1.0.0"
owner: "meta-harness"
execution_mode: "validation_gate_run"
scope: "portable_parent_wrapper_repo"
depends_on:
  - "meta-harness-absorption-seven-phase"
  - "meta-harness-absorption-harvest.inventory"
  - "meta-harness-absorption.manifest"
---

# Meta-Harness Absorption Validation Plan

## Principle

The standalone `meta-harness` repo is not promotable because it is described.
It is only promotable if the absorption artifacts pass a bounded validation
loop and emit durable proof outputs.

## Required validation passes

1. `harvest_validation`
   - all harvested source roots exist
   - all required hook files exist
   - all manifest decision sources resolve
   - the full governed prompt-contract artifact set exists in the harvested
     authority surfaces

2. `registry_validation`
   - every manifest decision has a unique `surface_id`
   - every decision class is in the allowed enum
   - every required parent family is declared

3. `document_validation`
   - the seven-phase plan parses as a front-matter plus bottom-matter contract
   - this validation plan parses as a front-matter plus bottom-matter contract
   - required parent Markdown scaffold files are declared:
     - `README.md`
     - `AGENTS.md`
     - `CLAUDE.md`
     - `GOAL.md`
     - `GOLDENPATH.md`
     - `MEMORY.md`
   - those required parent Markdown scaffold files must carry both front matter
     and bottom matter before promotion can turn green
   - required prompt-contract artifacts are declared:
     - `agent-heavy-run-prompt-index.md`
     - `agent-heavy-run-prompt-schema.md`
     - `agent-heavy-run-prompt.schema.json`
     - `agent-heavy-run-prompt.template.yaml`
     - `copilot-prompting-playbook.md`

4. `docs_sync_validation`
   - `bash scripts/pre-commit-docs-check.sh`
   - `git diff --check`

5. `promotion_validation`
   - promotion remains red until:
     - a parent repo skeleton exists
     - the required Markdown scaffold exists with front matter and bottom matter
     - the required prompt-contract artifacts exist in the standalone parent repo
     - a first parent proof package exists
     - real validator outputs are emitted for the parent repo

## Required proof artifacts

- `meta-harness-absorption-validation.report.json`
- `meta-harness-absorption-promotion.readiness.json`

## Current bounded run

This run only validates the pre-repo-creation absorption contract. Promotion
must remain blocked until the standalone parent repo exists and reruns the same
validation logic in its own proof package.

---bottom-matter---
status_summary:
  completeness: 0.86
  confidence: high
  doc_state: active_plan

gate_progress:
  - gate_id: harvest_gate
    status: amber
    notes: "Validation plan exists, but harvest proof output has not been emitted yet."
  - gate_id: registry_gate
    status: amber
    notes: "Manifest decisions exist, but need machine-checked uniqueness and enum validation."
  - gate_id: manifest_gate
    status: amber
    notes: "Manifest is defined and ready for validation."
  - gate_id: verification_gate
    status: red
    notes: "Validation report has not yet been emitted."
  - gate_id: state_gate
    status: amber
    notes: "Promotion is intentionally blocked until proof output exists."
  - gate_id: health_gate
    status: amber
    notes: "Health requires existence checks, docs checks, and contract verification."
  - gate_id: promotion_gate
    status: red
    notes: "No standalone parent repo skeleton exists yet."

open_questions:
  - "Should the parent repo reuse FRE validator code verbatim or expose a separate meta-harness validator surface?"

pending_validations:
  - "Emit validation report JSON."
  - "Emit blocked promotion readiness JSON."

promotion_criteria:
  - "Validation report exists and passes all pre-repo-creation checks."
  - "Blocked promotion readiness is explicit and evidence-backed."

blocked_by:
  - "Standalone meta-harness repo has not yet been created."

next_iteration:
  owner: "codex"
  objective: "Run the bounded pre-repo-creation validation pass and emit proof artifacts."
