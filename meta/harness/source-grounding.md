# Meta-Harness Source Grounding

This file keeps the LATTICE Meta-Harness aligned with the sources it is derived from. LATTICE modifies the pattern heavily, but these are the grounding constraints.

## Source Lineage

| Source | What LATTICE takes from it | Constraint |
|---|---|---|
| `arxiv.org/abs/2603.28052` | Meta-Harness is an outer loop that searches over harness code around a fixed model. | Do not call ordinary orchestration a Meta-Harness unless there is an evaluation loop, candidate history, stored traces, and keep/reject logic. |
| `yoonholee.com/meta-harness` | The proposer reads prior candidate source, scores, and execution traces through a filesystem. | Store raw evidence, not only summaries. The proposer needs inspectable logs and files. |
| `stanford-iris-lab/meta-harness` | New domains start with onboarding and a `domain_spec.md`; implementation waits until required fields are filled or marked `unknown`. | Do not jump straight to dry run without a domain spec. |
| `SuperagenticAI/metaharness` | Practical harnesses optimize instruction files, setup flows, validation scripts, test scripts, routing, and acceptance checks. | Treat these files as candidate harness surfaces, not just docs. |
| `jmilinovich/goal-md` | Construct the ruler before optimizing: fitness function, improvement loop, action catalog, operating mode, and constraints. | Every section needs a score that can move, plus a check that the score itself is trustworthy. |
| `trevin-creator/autoresearch-mlx` | Fixed artifact, fixed metric, fixed budget, keep-or-revert via git. | Use tight loops first; do not expand search space before the ratchet is real. |

Detailed adoption decisions are recorded in `meta/harness/source-adoption-audit.md`.

## Correct LATTICE Interpretation

The LATTICE Meta-Harness is not just a set of agents, docs, or scripts. It must become an optimization loop:

1. Define a fixed task domain and candidate harness interface.
2. Define what is fixed and what may change.
3. Define a search-set evaluation and a held-out evaluation.
4. Store candidate workspaces, diffs, logs, scores, and metadata.
5. Let a proposer inspect prior source, scores, and traces.
6. Accept candidates only when the score improves and guardrails hold.
7. Revert or discard failures.
8. Preserve enough evidence for the next proposer to diagnose recurring failure modes.

LATTICE adds Pixeltable as the operational substrate. That changes storage and analytics, not the core rule: no metric, no candidate history, no keep/reject gate means no Meta-Harness yet.

## What We Should Not Do

- Do not treat a dry run as a Meta-Harness run unless it has a scored evaluation unit.
- Do not let capability registries become shelfware. They must feed candidate harness decisions or gap checks.
- Do not optimize the whole system at once. Start with one bounded domain and one measurable loop.
- Do not rely on summaries only. Store raw logs, traces, diffs, command output, and scorer output.
- Do not change model/provider, tool surface, task, and harness logic in the same first loop. Fix as much as possible before searching.
- Do not register a harvested capability as active until a proof run produces the desired outcome and writes evidence.

## LATTICE-Specific Additions

Pixeltable eventually holds the candidate ledger, evidence, docs, capabilities, run state, model benchmarks, and relationships. Git remains the change-control surface while this matures. DuckDB WASM consumes Pixeltable-served Arrow/Parquet for browser analytics.

Pi, Claude CLI, Codex, Copilot, OpenRouter, Ollama, MLX, and local models are execution surfaces. They are not the Meta-Harness by themselves. The Meta-Harness is the outer loop that chooses, evaluates, and ratchets harness changes from evidence.
