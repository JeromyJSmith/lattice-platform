# FRE Schema Evaluation Plan for LATTICE Meta-Harness

Date: 2026-05-16
Branch: `feat/fre-meta-harness-eval`
Worktree: `/Volumes/PixelTable/VW_iTWIN_Bridge/lattice-worktrees/feat-fre-meta-harness-eval`
Source packet: `/Volumes/PixelTable/VW_iTWIN_Bridge/fre-test-eval-improvement 76019c48ec2441c0a42a1ac7a3f9b49b.md`
Base commit: `d02328e` (`origin/main`)

## 0. Evaluation Hypothesis

This branch evaluates FRE as a candidate proof kernel, not as doctrine and not as a replacement framework.

The bounded claim is:

> A schema-driven loop of source -> schema -> examples -> validation -> metrics -> repair task -> promotion decision can serve as the smallest repeatable proof kernel for future LATTICE and non-LATTICE projects.

The evaluation must prove, amend, or reject that claim.

## 1. Evaluation Boundary

```yaml
date: 2026-05-16
branch: feat/fre-meta-harness-eval
worktree: /Volumes/PixelTable/VW_iTWIN_Bridge/lattice-worktrees/feat-fre-meta-harness-eval
source_packet: /Volumes/PixelTable/VW_iTWIN_Bridge/fre-test-eval-improvement 76019c48ec2441c0a42a1ac7a3f9b49b.md
base_commit: d02328e
allowed_write_scope:
  - meta/harness/fre/**
  - meta/harness/docs/specs/fre-method-evaluation-plan-2026-05-16.md
forbidden_write_scope:
  - pixeltable/**
  - src/**
  - public/**
  - scripts/**
  - meta/SCHEMA.md
  - meta/ARCHITECTURE.md
  - meta/API.md
  - pixeltable/migrations/**
  - deployment config
  - production runtime config
  - production data
```

Any change outside `meta/harness/fre/**` requires explicit justification in the session report and in the adoption memo.

## 2. Production Safety Constraints

The evaluation must not modify:

- production Pixeltable schema
- migrations
- runtime routes
- application UI
- deployment config
- production data
- existing LATTICE proof artifacts except by adding references

Allowed write scope during the evaluation is:

```text
meta/harness/fre/**
```

The plan file itself is the only approved exception while bootstrapping the branch.

## 3. Success Criteria

The evaluation succeeds only if all are true:

1. The FRE packet is translated into repo-local executable artifacts.
2. The loop runs end to end with deterministic commands.
3. Valid examples pass.
4. Invalid examples fail for the expected reasons.
5. Failures produce repair tasks and promotion decisions.
6. Results map cleanly or explicitly conflict with existing LATTICE concepts:
   - proof evidence
   - ratchet decisions
   - capability promotion
   - restart-ready docs
7. At least two real LATTICE fixtures are evaluated.
8. The final decision memo recommends one of:
   - `ADOPT`
   - `ADOPT WITH AMENDMENTS`
   - `REJECT`

## 4. Rejection Criteria

Reject FRE as a future base framework if any are true:

1. Same inputs do not produce repeatable outputs.
2. Invalid examples pass or fail for accidental reasons.
3. Repair tasks are vague or non-actionable.
4. FRE vocabulary conflicts with existing LATTICE proof language without adding clarity.
5. Real LATTICE fixtures require major schema expansion before the loop is useful.
6. The experiment requires migrations, UI, or runtime integration before proving the contract.
7. The adoption memo cannot state what FRE adds beyond existing Meta-Harness practice.
8. The schema cannot represent existing LATTICE proof, evidence, or promotion concepts without major distortion.

## 5. Ground Rules

- Keep the experiment isolated under `meta/harness/fre/`.
- Do not add Pixeltable migration `0017`.
- Do not wire FRE into production runtime.
- Do not build UI, Notion sync, InfraNodus, MCP, or multi-agent orchestration.
- Treat FRE as a candidate harness contract.
- Preserve LATTICE proof language until a translation map proves a better abstraction.
- Use `uv` for deterministic Python commands.

## 6. Repository Shape

```text
meta/harness/fre/
  README.md
  CLAUDE.md
  docs/
    goal.md
    sources.md
    source-normalization.md
    evaluation-questions.md
    fre-to-lattice-map.md
    adoption-rubric.md
    gaps.md
    decisions/
    sessions/
  schemas/
    fre-loop.schema.json
    gate-result.schema.json
    repair-task.schema.json
    promotion-decision.schema.json
  examples/
    fre-loop.valid.json
    fre-loop.invalid.missing-promotion.json
    fre-loop.invalid.green-terminology.json
    expected-failures.yaml
    gate-result.valid.json
    repair-task.valid.json
    promotion-decision.valid.json
  tests/
    test_schema_validity.py
    test_examples_validate.py
    test_failure_examples_fail.py
    test_no_green_terminology.py
    test_required_metrics.py
    test_repair_tasks.py
    test_lattice_mapping.py
  harness/
    validate_schema.py
    validate_examples.py
    evaluate.py
    report.py
    propose_repairs.py
  runs/
    README.md
```

## 7. Vocabulary Anti-Corruption Layer

FRE vocabulary must not overwrite working LATTICE vocabulary by default.

Required mapping doc:

```text
meta/harness/fre/docs/fre-to-lattice-map.md
```

Minimum statuses:

```text
clean
partial
conflict
reject
needs_extension
```

Minimum mapping shape:

| FRE field | LATTICE concept | Transfer status | Notes |
|---|---|---|---|
| `repair_task` | proposal / bounded implementation task | clean | Requires owner and acceptance criteria |
| `promotion_decision` | ratchet decision / capability promotion gate | partial | Needs stronger evidence fields |
| `scorecard` | benchmark / evidence artifact | clean | Should include command output hashes |
| `validation_pass_criteria` | ratchet acceptance rule | clean | Rename acceptable |
| `source_record` | provenance evidence | partial | Needs richer source typing |
| `artifact` | capability/proof artifact | partial | Needs artifact lineage |

## 8. Phase 0 - Normalize Source Packet

### Goal

Convert the Notion-derived FRE source packet into clean repo-local source references and executable artifacts.

### Required cleanup

- Remove Notion-created markdown links inside code blocks.
- Replace malformed commands such as `validate_[schema.py](http://schema.py)` with `validate_schema.py`.
- Replace malformed commands such as `harness/[evaluate.py](http://evaluate.py)` with `harness/evaluate.py`.
- Convert Notion page mentions into provenance table entries.
- Validate YAML blocks.
- Validate JSON blocks.
- Ensure code fences are closed correctly.
- Preserve the terminology decision:
  - forbidden: `definition_of_green`
  - required: `validation_pass_criteria`
- Keep `definition_of_green` only in intentional invalid fixtures and terminology tests.

### Deliverables

```text
meta/harness/fre/docs/sources.md
meta/harness/fre/docs/source-normalization.md
meta/harness/fre/docs/goal.md
```

### Exit check

One repo-local source bundle summary exists and can be read without the external source packet.

## 9. Phase 1 - Build Minimal Executable Loop

### Goal

Create a runnable FRE loop under `meta/harness/fre/`.

### Commands

```bash
uv run python meta/harness/fre/harness/validate_schema.py
uv run python meta/harness/fre/harness/validate_examples.py
uv run python meta/harness/fre/harness/evaluate.py
uv run python meta/harness/fre/harness/propose_repairs.py
uv run python meta/harness/fre/harness/report.py
uv run pytest meta/harness/fre/tests
```

### Required outputs

Every run must use an immutable run directory:

```text
meta/harness/fre/runs/RUN-YYYY-MM-DD-0001/
  input-manifest.yaml
  normalized-source-summary.md
  schema-validation.json
  example-validation.json
  gate-results.json
  scorecard.yaml
  repair-tasks.yaml
  report.md
  promotion-decision.md
```

Optional convenience pointer:

```text
meta/harness/fre/runs/latest -> RUN-YYYY-MM-DD-0001
```

Do not treat `latest` as canonical.

### Required run manifest

Every `input-manifest.yaml` must capture:

```yaml
run_id: RUN-YYYY-MM-DD-0001
branch: feat/fre-meta-harness-eval
base_commit: d02328e
worktree: /Volumes/PixelTable/VW_iTWIN_Bridge/lattice-worktrees/feat-fre-meta-harness-eval
source_packet: /Volumes/PixelTable/VW_iTWIN_Bridge/fre-test-eval-improvement 76019c48ec2441c0a42a1ac7a3f9b49b.md
commands:
  - uv run python meta/harness/fre/harness/validate_schema.py
  - uv run python meta/harness/fre/harness/validate_examples.py
  - uv run python meta/harness/fre/harness/evaluate.py
  - uv run python meta/harness/fre/harness/propose_repairs.py
  - uv run python meta/harness/fre/harness/report.py
  - uv run pytest meta/harness/fre/tests
```

### Exit check

The loop runs locally from source packet to scorecard and report with deterministic outputs.

## 10. Expected Failure Contracts

An invalid example failing is not enough. It must fail for the intended reason.

Required manifest:

```text
meta/harness/fre/examples/expected-failures.yaml
```

Minimum structure:

```yaml
expected_failures:
  - example: examples/fre-loop.invalid.green-terminology.json
    expected_failure_classes:
      - REQUIRED_FIELD_MISSING
      - ADDITIONAL_PROPERTY_NOT_ALLOWED
    expected_field:
      - validation_pass_criteria
      - definition_of_green

  - example: examples/fre-loop.invalid.missing-promotion.json
    expected_failure_classes:
      - AUTHORITY_CHAIN_MISSING_REQUIRED_VALUE
    expected_field:
      - authority_chain
    expected_missing_value:
      - promotion_decision
```

The invalid-example tests must assert:

```text
invalid example fails for expected failure class and expected field
```

not merely:

```text
invalid example fails
```

## 11. Phase 2 - Map FRE to LATTICE Semantics

### Goal

Prove whether FRE outputs map cleanly to existing LATTICE proof surfaces.

### Deliverables

```text
meta/harness/fre/docs/fre-to-lattice-map.md
meta/harness/fre/docs/sessions/RUN-YYYY-MM-DD-0001.md
meta/harness/fre/docs/gaps.md
```

### Exit check

The team can point to exact fields that transfer cleanly and exact fields that do not.

## 12. Phase 3 - Pressure Test with Real LATTICE Fixtures

### Goal

Test FRE against real artifacts, not just toy examples.

### Candidate fixtures

Use at least two:

- a capability contract document
- a harness proof report
- a route or schema change proposal
- a research-derived adoption packet
- a restart-ready handoff doc

### Test questions

1. Does FRE clarify provenance and evidence?
2. Does it produce better repair tasks?
3. Does it capture ratchet and promotion decisions?
4. Does it stay small?
5. Does it conflict with existing LATTICE proof language?

### Exit check

At least two real LATTICE artifacts have gone through the loop and produced reports.

## 13. Phase 4 - Adoption Decision

### Decision options

```text
ADOPT
ADOPT WITH AMENDMENTS
REJECT
```

### Adoption scoring rubric

Score each category from `0` to `2`.

- `0` = failed or not useful
- `1` = partially useful or needs amendment
- `2` = strong fit

| Category | Score |
|---|---:|
| Deterministic execution | 0-2 |
| Schema clarity | 0-2 |
| Repair task usefulness | 0-2 |
| LATTICE vocabulary compatibility | 0-2 |
| Real artifact usefulness | 0-2 |
| Integration restraint | 0-2 |
| Evidence quality | 0-2 |
| Restart readiness | 0-2 |

Decision rule:

```text
14-16 = ADOPT
9-13  = ADOPT WITH AMENDMENTS
0-8   = REJECT
```

### Memo must include

- what FRE proved
- what FRE failed to prove
- where FRE conflicted with LATTICE
- minimal amendments needed
- whether FRE should become the cross-project baseline
- what remains LATTICE-specific

## 14. Risks and Controls

### Risk 1 - Building a second harness instead of evaluating a schema

Control:

Keep all work under `meta/harness/fre/` and refuse to wire it into the main runtime until the adoption memo exists.

### Risk 2 - Adopting FRE vocabulary too early

Control:

Preserve a translation layer and do not rewrite existing Meta-Harness language prematurely.

### Risk 3 - Treating toy-example passes as proof

Control:

Require at least two real LATTICE fixtures before any adoption recommendation.

### Risk 4 - Pulling migrations, UI, or runtime work into the experiment

Control:

Explicitly mark those as post-evaluation integrations, not part of the proof.

### Risk 5 - Source packet corruption from Notion export

Control:

Do not generate executable files until Phase 0 normalization is complete and recorded.

## 15. Immediate Next Tasks

1. Create `meta/harness/fre/README.md` and `CLAUDE.md` as the bounded experiment charter.
2. Translate the source packet into local `docs/sources.md`, `docs/source-normalization.md`, and `docs/goal.md`.
3. Implement the four core schemas plus the valid and invalid example set.
4. Add `examples/expected-failures.yaml`.
5. Add the first seven tests, including `test_lattice_mapping.py`.
6. Add `evaluate.py`, `report.py`, and `propose_repairs.py` so every failure emits a repair task.
7. Run one end-to-end session and record it under an immutable run directory.
8. Write the FRE-to-LATTICE mapping memo before expanding scope.

## 16. Recommendation

Proceed with this as a bounded evaluation branch, not a doctrine branch.

The standard is not whether FRE is elegant. The standard is whether FRE produces better proof artifacts, better repair tasks, and better promotion decisions than LATTICE already has.

The likely winning outcome is not raw FRE adoption. The likely winning outcome is:

- FRE supplies the smallest executable loop.
- LATTICE supplies evidence, ratchet, capability-promotion, and operator-proof discipline.
- The merged result becomes the reusable cross-project framework.
