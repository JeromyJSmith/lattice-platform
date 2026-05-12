<!-- spec-verified: disler/benchy 31e8377 2026-05-12 -->
# Benchmarking

LATTICE incorporates Benchy as the model-fit benchmark doctrine and source
corpus: compare models on the actual task, not a generic leaderboard.

Benchy itself runs a Vue/Vite UI on `http://localhost:5173` and a Python API on
`http://localhost:8000`. LATTICE mirrors the Benchy repo under
`meta/harness/references/benchy/` for full visibility, with `.git`, `.env*`,
dependency folders, generated output, and caches excluded. The operator console
gets a native Benchy-style surface at `/harness/benchmarks` that can visualize
benchmark reports and later stream live Python runner output from
Pixeltable-backed evidence.

The sidecar owns the API surface:

```text
GET  /v1/harness/benchmarks/sample-report
POST /v1/harness/benchmarks/reports/validate
```

Next live-run endpoints should be added beside those routes, not as browser-only
logic.

## Source Tie-In

| Benchy source | LATTICE use |
|---|---|
| `meta/harness/references/benchy/client/src/*` | UI reference for visible benchmark comparison patterns |
| `meta/harness/references/benchy/server/benchmark_data/*.yaml` | Fixture/config reference for future LATTICE benchmark YAML |
| `meta/harness/references/benchy/server/reports/*.json` | Report-shape reference for console and evidence ingestion |
| `meta/harness/references/benchy/server/modules/*_llm.py` | Provider adapter reference for model-fit runners |
| `meta/harness/references/benchy/specs/*.md` | Feature/spec reference for future benchmark surfaces |

The mirror gives agents the whole repo to inspect. LATTICE still adapts runtime
behavior into LATTICE-owned code: TanStack routes, FastAPI sidecar endpoints,
uv single-file jobs, and Pixeltable evidence tables.

## Rule

Benchmarks must be specific to the harness task.

For each benchmark:

- define fixture input
- define expected output or scoring rubric
- run candidate models under the same constraints
- record quality, latency, cost, and failure mode
- write durable report evidence
- visualize live progress in the console while the run is executing
- promote the winner into the task manifest or library entry

## Surfaces

Benchmark candidates may run through:

- Pi model routing
- OpenRouter
- Ollama
- MLX/local models
- Claude CLI
- provider-specific single-file agents
- sandbox/obox parallel forks

## Reports

Benchmark reports are evidence. Store the result path in the model-fit row and avoid rerunning expensive tests without a reason.

The console report shape follows Benchy's `IsoSpeedBench` idea: benchmark name,
purpose, base prompt, prompt iterations, model reports, per-prompt results,
quality signal, latency, cost, and failure mode. The first UI accepts JSON
reports; YAML benchmark execution should be handled by a Python runner that
writes the same report shape before Pixeltable ingestion.

## Parallel variants

When many outcomes could be acceptable, run multiple variants in separate worktrees or sandboxes and compare. Non-determinism is useful only when the selection process is disciplined.
