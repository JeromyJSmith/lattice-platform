# FRE Kernel Hardening Plan

## Scope

This plan fixes every defect raised by the hard review inside the bounded FRE
evaluation namespace.

## Workstreams

### 1. Contract Repair

Targets:

- `schemas/fre-loop.schema.json`
- `schemas/gate-result.schema.json`
- `schemas/repair-task.schema.json`
- `schemas/promotion-decision.schema.json`
- `examples/*`

Fixes:

1. Make the schema files the source of truth.
2. Add the research-first chain to the checked-in FRE schema.
3. Align schema enums, metric sets, stage counts, and ordering requirements with
   the actual evaluation contract.
4. Ensure valid and invalid fixtures reflect the same contract.

### 2. Validation Repair

Targets:

- `harness/lib.py`
- `harness/validate_schema.py`
- `harness/validate_examples.py`
- `tests/test_schema_validity.py`
- `tests/test_examples_validate.py`
- `tests/test_failure_examples_fail.py`

Fixes:

1. Replace "schema exists and has a type" checks with real schema parsing and
   real example-vs-schema validation.
2. Keep failure reasons exact and testable.
3. Keep a minimal Python contract layer only where it adds logic that JSON
   Schema cannot express directly; do not let it redefine the schema.

### 3. Scoring and Gate Repair

Targets:

- `harness/lib.py`
- `harness/evaluate.py`
- `harness/report.py`

Fixes:

1. Remove hardcoded rubric wins.
2. Measure determinism from repeatable artifacts.
3. Measure LATTICE vocabulary compatibility from mapping coverage plus fixture
   translation evidence.
4. Prevent `ADOPT` when a required proof dimension is unmeasured.

### 4. Real Fixture Repair

Targets:

- `harness/evaluate_real_fixtures.py`
- `harness/lib.py`
- `fixtures/*`
- `runs/*`

Fixes:

1. Score fixture pressure from current-run evaluation artifacts.
2. Stop treating `RUN-2026-05-16-0004` as permanently sufficient evidence.
3. Preserve historical fixture runs as evidence, but do not let them satisfy the
   current run automatically.

### 5. Artifact Shape Repair

Targets:

- `harness/propose_repairs.py`
- `harness/report.py`
- `harness/iterate.py`
- `runs/README.md`

Fixes:

1. Make `repair-tasks.yaml` stable everywhere.
2. Make report and promotion-decision outputs consistent across scripts.
3. Keep run manifests and required artifacts auditable.

### 6. Test Expansion

Targets:

- `tests/*`

Add:

1. real schema validation tests
2. artifact shape tests
3. current-run fixture evidence tests
4. promotion decision gate tests
5. determinism tests

### 7. Ratchet Execution

Targets:

- `GOAL.md`
- `GoldenPath.md`
- `harness/iterate.py`
- `skills/fre-research-ratchet/*`

Fixes:

1. Keep the bounded Meta-Harness flow explicit.
2. Run score-before/score-after honestly after repairs land.
3. Stop on plateau or regression.
4. Never commit score gains caused by weaker proof.

### 8. MLX Autoresearch Staging

Targets:

- `docs/research-grounding.md`
- `docs/research-findings.md`
- `docs/kernel-hardening-plan.md`

Before any MLX run:

1. define allowed inputs
2. define write boundary
3. define measurable objective
4. define ratchet acceptance criteria
5. define rollback behavior

## Execution Order

1. Contract repair
2. Validation repair
3. Scoring and gate repair
4. Artifact shape repair
5. Test expansion
6. Real fixture repair
7. Ratchet execution
8. MLX staging

## Acceptance Standard

Do not call the kernel ready until:

- the hard-review findings are closed,
- the evidence is current-run based,
- the score survives stricter validation,
- and the promotion decision still holds.
