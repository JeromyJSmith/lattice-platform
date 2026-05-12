# Domain Spec: LATTICE Meta-Harness Incubation

This is the onboarding artifact required before the first real Meta-Harness dry run. Unknowns stay explicit until they are resolved.

## Domain Summary

The target domain is improving the LATTICE Meta-Harness itself: the harness code, docs, setup flows, validation scripts, capability registries, evidence routing, and task execution wrappers around LATTICE agents.

Unit of evaluation: one bounded harness job. A job has a goal, files involved, constraints, acceptance criteria, verification target, required checks, output artifact, and do-not-touch list.

Fixed for the first pass:

- repository: `/Volumes/PixelTable/VW_iTWIN_Bridge/VW_iTwin_Bridge`
- outer wrapper: `/Volumes/PixelTable/VW_iTWIN_Bridge/meta`
- base branch: `feature/meta-harness`
- hard prohibitions: landed migrations, secrets, branch protection, main merges, deletions, incidental doctrine changes
- required verification oracle: `bash scripts/lattice-verify.sh HEAD`

Allowed to change in the first pass:

- Meta-Harness docs
- capability registries
- verification scripts
- library config
- wrapper/body-cell contract docs
- stub implementation only when the tracking issue and acceptance gate are clear

Out of scope for the first pass:

- editing migrations `0001` through `0016`
- moving all source into Pixeltable
- model/provider optimization
- broad task dispatch automation
- full docs mirror implementation
- standalone Meta-Harness repo extraction

Base model or proposer: unknown. Candidate proposers may include Codex, Claude CLI, Pi-launched models, OpenRouter, Ollama, and MLX-backed local models, but the first loop should fix one proposer to avoid attribution noise.

Optimization budget: unknown. Conservative default for first run: one candidate, one evaluation, no automatic keep/revert beyond human review.

## Harness and Search Plan

Candidate harness shape:

```text
candidate/
  instructions/
  scripts/
  config/
  verification/
  evidence/
```

Every candidate must satisfy:

- exposes a single entrypoint command
- writes an evidence artifact
- records changed files and command output
- runs `scripts/lattice-verify.sh`
- does not touch protected paths
- can be compared against a baseline candidate

Initial baseline:

- current body-cell harness docs and scripts on `feature/meta-harness`
- current outer wrapper config under `/Volumes/PixelTable/VW_iTWIN_Bridge/meta`

First search loop:

1. Start with a no-op baseline candidate.
2. Run the verification oracle.
3. Store logs and score output.
4. Make one small candidate change.
5. Re-run the same oracle.
6. Keep only if the score improves and hard rules hold.

## Evaluation Plan

Search-set evaluation: one bounded Meta-Harness job that exercises wrapper-to-body-cell evidence flow and local verification.

Held-out evaluation: unknown. Candidate default: a second job that touches a different surface, such as docs mirror stubs or capability registry coverage, after the first loop works.

Primary metric: unknown until the first scorer is implemented. Candidate default:

```text
harness_readiness_score =
  0.30 * verification_pass
+ 0.20 * evidence_artifact_present
+ 0.20 * wrapper_body_contract_valid
+ 0.15 * capability_registry_valid
+ 0.15 * docs_substrate_contract_valid
```

Secondary metrics:

- runtime
- command count
- changed-file count
- protected-path violations
- unresolved critical gaps
- whether evidence is Pixeltable-ingestable

Capability activation starts at zero. Harvest and matrix rows can describe
candidate capability surfaces, but a capability receives operational credit only
after a proof run produces the desired outcome and writes evidence. That first
passing run is the gateway into the manifest and registry; subsequent runs track
pass rate, runtime, cost, model/provider used, input and output shape, and
failure patterns.

Noise and leakage risks:

- Human review may hide failures unless command output is preserved.
- If the scorer rewards doc volume, the agent may add bloat.
- If the same job is both search set and final test, the harness can overfit to that job.

Mitigation:

- Keep scorer simple and auditable.
- Store raw logs.
- Use at least one held-out job before claiming improvement.
- Penalize bloat and off-target edits.

## Experience and Logging

Offline evidence available:

- `/Volumes/PixelTable/VW_iTWIN_Bridge/meta/meta-repomix.xml`
- `meta/harness/PLAN/*.md`
- `meta/harness/docs/*`
- `analysis/capabilities/*.yaml`
- `scripts/*`
- `meta/verification/*`

Online traces to store per candidate:

- candidate ID
- base git SHA
- changed files
- diff summary
- command log
- scorer output
- verifier output
- keep/discard decision
- reason for decision

Initial filesystem evidence target:

```text
/Volumes/PixelTable/VW_iTWIN_Bridge/meta/runs/<run-id>/
```

Pixeltable target:

Candidate runs should later ingest into `lattice/harness/verification_runs`, `lattice/harness/evidence`, `lattice/harness/jobs`, and `lattice/harness/capabilities`.

## Open Questions and Unknowns

- What is the first scored job?
- What proposer is fixed for the first loop?
- What exact scalar score should be authoritative?
- What is the held-out job?
- Should the first candidate ledger live only in wrapper `runs/`, or also write a body-cell copy?
- What fields must migration `0017` include to ingest the first candidate run without redesign?
