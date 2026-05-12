<!-- spec-verified: code.claude.com/docs 2026-05-11 -->
# Model Fit

The Meta-Harness must learn which model works best for each recurring task. Do not pick models by intuition when a dry run can measure them.

## Rule

Every repeatable harness script or prompt command should eventually have a model-fit row:

| Task | Candidate models | Dataset / fixtures | Metric | Current winner | Evidence |
|---|---|---|---|---|---|
| `<task id>` | `Ollama / MLX / OpenRouter / Claude CLI / Pi route` | `<fixture path>` | `<accuracy, validity, latency, cost, score improvement>` | `<model>` | `<report path>` |

## Candidate surfaces

- Pi routes for delegated execution
- Ollama local models
- MLX local models on Apple Silicon
- OpenRouter remote models
- Claude CLI for high-context tasks
- Domain local models for narrow extract/classify/validate jobs
- fork-terminal comparisons for CLI agents
- sandbox/obox parallel forks for isolated model experiments

## Benchmark loop

1. Pick one bounded harness task.
2. Build a tiny fixture set with expected outputs or a scoring rubric.
3. Run candidate models through the same Pi/job contract.
4. Verify outputs with deterministic scripts where possible.
5. Record score, latency, cost, and failure mode.
6. Promote the best model into the task manifest.
7. Re-run when the task, model, or fixture changes.

Benchmark doctrine: see `meta/harness/benchmarking.md`.

## Plateau rule

Before LATTICE shifts attention back to the wider platform, the Meta-Harness must complete a dry run and then improve until it reaches a plateau:

- dry run executes end-to-end
- verifier catches real gaps
- at least one capability lifecycle gate is active
- at least one model-fit benchmark has run or is explicitly blocked
- score/doc/verification improvements flatten across repeated iterations

Until that plateau is reached, Meta-Harness setup has priority over broader product work.
