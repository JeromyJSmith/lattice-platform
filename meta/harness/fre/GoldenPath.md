# FRE Kernel Golden Path

## Purpose

This is the bounded execution path for repairing and evaluating the FRE kernel
 inside LATTICE without touching production surfaces.

## Preconditions

1. Work only inside `meta/harness/fre/`.
2. Read:
   - `meta/harness/CLAUDE.md`
   - `meta/harness/GOAL.md`
   - `meta/harness/fre/CLAUDE.md`
   - `meta/harness/fre/GOAL.md`
   - `meta/harness/fre/docs/research-grounding.md`
   - `meta/harness/fre/docs/research-findings.md`
3. Confirm the current contract defects before editing:
   - schema and validator disagree
   - scorer overpromotes
   - real-fixture gate uses stale evidence
   - repair-task artifact shape is inconsistent
   - tests are shallower than the claims

## Repair Path

### Step 1. Repair the contract

- Align `schemas/fre-loop.schema.json` to the research-first model.
- Ensure the schema includes `research` where the kernel requires it.
- Remove all schema/validator/example mismatches.

### Step 2. Repair validation

- Validate examples against the checked-in schemas.
- Keep the expected-failure contract exact.
- Fail the build if schema truth and validator truth diverge.

### Step 3. Repair scoring

- Replace hardcoded rubric values with measured evidence.
- Prevent `ADOPT` when evidence is incomplete or stale.
- Score current-run fixture evidence only.

### Step 4. Repair artifacts

- Keep one stable shape per artifact.
- Require current-run fixture outputs when fixture pressure is claimed.
- Keep session summaries and scorecards restart-ready.

### Step 5. Repair tests

- Add tests for real schema validation.
- Add tests for run-artifact shapes.
- Add tests for determinism evidence.
- Add tests for promotion decision correctness.

### Step 6. Run the bounded ratchet

Run:

```bash
uv run pytest meta/harness/fre/tests
uv run python meta/harness/fre/harness/validate_schema.py
uv run python meta/harness/fre/harness/validate_examples.py
uv run python meta/harness/fre/harness/evaluate.py
uv run python meta/harness/fre/harness/propose_repairs.py
uv run python meta/harness/fre/harness/report.py
uv run python meta/harness/fre/harness/evaluate_real_fixtures.py
uv run python meta/harness/fre/harness/iterate.py
```

## Success Signal

The kernel may only claim a stronger state when:

1. the contract is internally consistent,
2. the run artifacts are stable,
3. current-run fixture evidence passes,
4. the score improves honestly,
5. the promotion decision matches the evidence.
