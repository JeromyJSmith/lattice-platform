# FRE Kernel Goal

## Mission

This namespace exists to determine whether the FRE candidate loop can survive
honest LATTICE proof discipline.

Canonical chain:

```text
research -> source -> schema -> examples -> validation -> metrics -> repair task -> promotion decision
```

This is not an adoption surface. It is a bounded evaluation surface.

## Definition of Ready

The FRE kernel is only "ready" when all of the following are true:

1. The checked-in JSON Schemas are the source of truth.
2. Valid examples are validated against the real schemas, not a parallel Python-only contract.
3. Invalid examples fail for the intended failure class, field, and missing value.
4. Research grounding is measured from explicit provenance and research artifacts.
5. Real fixture pressure is measured from current-run evidence, not a historical pass.
6. Every blocking failure emits a stable repair-task artifact shape.
7. Promotion decisions are derived from measured rubric evidence only.
8. Determinism is measured by repeatable run outputs, not hardcoded scores.
9. The bounded loop remains isolated under `meta/harness/fre/`.

## Ratchet Rule

Accept only if the repaired kernel improves evidence honestly.

```text
score_before -> run repair cycle -> score_after -> accept only if score_after > score_before
```

No score may increase because of:

- hardcoded rubric values
- stale fixture evidence
- weaker tests
- relaxed contract language that removes proof obligations

## Required Metrics

The bounded kernel must measure:

- `research_grounding`
- `schema_validity`
- `example_validation`
- `repair_task_count`
- `promotion_readiness`

Additional rubric dimensions must be backed by concrete evidence:

- deterministic execution
- schema clarity
- repair task usefulness
- LATTICE vocabulary compatibility
- real artifact usefulness
- integration restraint
- evidence quality
- restart readiness

## Exit Condition

The evaluation is complete only when the hard review can say:

- what is real
- what is still weak
- what remains intentionally out of scope
- whether the kernel is still only `ADOPT WITH AMENDMENTS`
- or whether it truly earns `ADOPT`
