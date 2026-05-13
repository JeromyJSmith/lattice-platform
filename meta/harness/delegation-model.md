<!-- spec-verified: code.claude.com/docs 2026-05-11 -->
# Delegation Model

LATTICE is the system. The orchestrator dispatches bounded work to execution surfaces, then the harness verifies the result with deterministic scripts and evidence.

## Execution surfaces

| Surface | Use |
|---|---|
| Claude CLI | High-context coding, repo edits, structured handoffs |
| Codex | Repo orchestration, implementation, verification, GitHub/Linear coordination |
| GitHub Copilot | GitHub-native issue/PR execution and review support |
| Pi | Default harness task runner: one-shot scripts, prompt commands, verifier loop, multi-model task routing |
| OpenRouter | Remote model fan-out when a task needs a specific model profile |
| Ollama | Local low-cost one-off tasks and repeatable harness jobs |
| MLX | Apple Silicon local model execution |
| Domain local models | Small scoped tasks, including Prism ML, Gemma-family, Bonsai-style classifiers, and other local specialists |

No surface owns the system. The orchestrator chooses the cheapest capable surface based on context, availability, blast radius, and task size.

## Pi-run harness jobs

Pi is the primary way LATTICE runs bounded harness jobs. A job may be a script, prompt command, local-model task, verifier pass, or delegated code task. The invariant is the same: Pi runs the job, the job emits an artifact, the harness verifies it.

Verifier is one Pi job type. It is not the only one.

Bash policy for these jobs follows `meta/harness/bash-safety.md`: L4 whitelist minimum for general jobs, L5 no-bash/custom-tools for verifier and high-blast-radius jobs.

IndyDevDan patterns are incorporated into LATTICE as doctrine and harness capabilities, not treated as external vendor drops. See `meta/harness/indydevdan-incorporation.md`.

Reusable skills, agents, prompts, and one-shot harness jobs are cataloged through `meta/harness/library.yaml` using the incorporated `the-library` pattern.

Library-backed jobs should prefer ephemeral sandboxes: resolve references from the catalog, clone/copy into a temp workspace, execute once, emit evidence, then delete the sandbox. The repo should retain durable config and outputs, not transient tool checkouts.

For isolated or parallel work, follow `meta/harness/fork-and-sandbox.md`. For setup and maintenance, follow `meta/harness/install-maintain.md`. For choosing Pi versus Claude CLI, follow `meta/harness/pi-claude-routing.md`.

For programmable CLI calls, single-file agents, file-triggered work intake, hook observability, and model benchmarks, use:

- `meta/harness/programmable-agents.md`
- `meta/harness/single-file-harness-agents.md`
- `meta/harness/drop-zones.md`
- `meta/harness/hooks-observability.md`
- `meta/harness/benchmarking.md`

## Single-file harness agents

Most section harnesses should start as tiny, single-file agents:

- one clear purpose
- one prompt contract
- one input shape
- one output artifact
- one verification command
- no ambient authority beyond the task

The point is not to make a permanent role taxonomy. The point is to make small executable workers that can be prompted by the harness, run once, emit evidence, and stop.

## Job contract

Every delegated job should fit this shape:

```text
Goal:
Files involved:
Constraints:
Acceptance criteria:
Verification target:
Required checks:
Output artifact:
Do-not-touch list:
```

The same contract can be sent through Pi to Claude CLI, Copilot-backed flows, OpenRouter-backed models, Ollama, MLX, or a local model wrapper.

## Execute-once rule

A delegated harness job should be runnable by Pi as a script or prompt command:

```bash
<command> <input> > <artifact>
<verification-command> <artifact>
```

Preferred pattern:

1. Load the job prompt and input.
2. Execute once.
3. Write a bounded artifact.
4. Run deterministic verification.
5. Report pass/fail with exact evidence.

Retries are allowed only when the verifier gives concrete corrective feedback. Open-ended loops are not.

## Programming surfaces

LATTICE expects real programmatic work, including:

- Python services, scripts, Pixeltable migrations, geospatial and IFC processing
- C++ Vectorworks SDK plugins
- Vectorworks scripting and MCP bridge work
- TypeScript/TanStack operator-console work
- CI, docs, graph, sync, and verification scripts

Every programming surface needs a local verifier command before it becomes routine harness work.

## Verification exit

All delegated work exits through verification:

- script ran
- output artifact exists
- hard prohibitions passed
- repo-specific checks passed
- relevant tests or compile checks passed
- PR/issue evidence is attached when the work is external-facing

For repo-wide verification, start with:

```bash
bash scripts/lattice-verify.sh
```

## Current priority

The active priority is Meta-Harness setup and dry-run readiness. Do not expand into broader platform development until the Meta-Harness can run, verify itself, benchmark useful model routes, and improve to a plateau.
