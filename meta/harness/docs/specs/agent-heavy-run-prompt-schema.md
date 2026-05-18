# Agent Heavy-Run Prompt Schema

Last updated: 2026-05-18

## Purpose

This document defines a portable, reusable schema for prompting Copilot or any
other execution agent in a way that is:

- reproducible
- bounded
- testable
- proof-aware
- environment-safe
- portable across agent surfaces

It is designed for the current working style in this repo:

- heavy autonomous runs
- narrow task boundaries
- real runtime truth
- honest blocked states
- landable bounded commits

This spec is intentionally agent-agnostic. `gh copilot -p` is one execution
surface, not the schema itself.

## Core Idea

A good prompt is not just prose. It is a governed execution contract with:

1. mission
2. current verified state
3. allowed and disallowed actions
4. bounded tasks
5. environment rules
6. validation loop
7. reporting contract

The prompt should be strong enough that a different capable agent can pick it up
and behave similarly.

## Heavy-Run Principle

Use one bounded heavy run whenever possible:

- inspect
- implement
- test
- rerun
- proof
- artifact refresh
- docs check
- commit

Do not split these into separate runs unless:

- a human decision is required
- the scope boundary changes materially
- the environment must be changed outside the repo

## Required Prompt Blocks

Every governed execution prompt should contain these blocks in this order:

1. `mode`
2. `mission`
3. `current_verified_state`
4. `hard_rules`
5. `allowed_paths`
6. `disallowed_paths`
7. `tasks`
8. `validation_loop`
9. `success_criteria`
10. `report_contract`

## Portable Prompt Object

Use this logical shape:

```yaml
prompt_schema_version: "1.0.0"
prompt_id: "PROMPT-YYYYMMDD-XXXX"
target_agent:
  name: "copilot"
  surface: "gh_copilot_p"
  invocation: "gh copilot -p"
mode:
  execution_style: "heavy_bounded_run"
  autonomy: "high"
  permission_model: "no_intermediate_permission"
mission:
  objective: ""
  repo_scope: ""
  task_scope: ""
current_verified_state:
  facts: []
hard_rules:
  environment: []
  safety: []
  truthfulness: []
allowed_paths:
  paths: []
disallowed_paths:
  paths: []
tasks:
  ordered_steps: []
validation_loop:
  checks: []
  rerun_policy: ""
success_criteria:
  best_case: ""
  acceptable_fallback: ""
report_contract:
  required_fields: []
```

## Field Definitions

### `prompt_schema_version`

Semantic version of the prompt schema itself.

### `prompt_id`

Stable identifier for this prompt instance.

Recommended format:

```text
PROMPT-YYYYMMDD-XXXX
```

### `target_agent`

Describes the execution surface.

Example:

```yaml
target_agent:
  name: "copilot"
  surface: "gh_copilot_p"
  invocation: "gh copilot -p"
```

Other valid examples:

- `codex`
- `claude`
- `browser_agent`

### `mode`

Defines how the agent should behave.

Recommended values:

- `execution_style`: `heavy_bounded_run`
- `autonomy`: `high`
- `permission_model`: `no_intermediate_permission`

### `mission`

The single bounded objective.

Required fields:

- `objective`
- `repo_scope`
- `task_scope`

`objective` must describe one deliverable or blocker class, not a broad theme.

Good:

- `Finish phases-sync with the smallest honest local seam and bounded ERP write path.`
- `Promote worksheet extraction artifacts into a normalized governed schema layer.`

Bad:

- `Improve DDC`
- `Make ERP better`

### `current_verified_state`

A list of concrete already-known truths. These are facts the agent must start
from instead of rediscovering old ground.

Examples:

- `boq-read passes`
- `cwicr collection is 49,600 x 3072`
- `ifc_elements has rows but no project_id`

### `hard_rules`

This is the most important block after `mission`.

Split into:

- `environment`
- `safety`
- `truthfulness`

Typical environment rules:

- use `uv` for all Python environment, dependency, script, and test execution
- do not use `pip` or ad hoc `venv` unless `uv` is first proven insufficient
- no paid-model API key wiring

Typical safety rules:

- do not broaden into unrelated capability work
- do not create proof-only routes
- do not rewrite broad architecture

Typical truthfulness rules:

- no fake green
- no mock-success path
- if blocked, keep exact live evidence

### `allowed_paths`

Explicitly list acceptable solution classes.

Example:

```yaml
allowed_paths:
  paths:
    - "reuse existing local no-key embedding/runtime if present"
    - "use deterministic lexical path over indexed Qdrant payloads"
    - "seed one proof-project row if existing bridge surfaces support it"
```

### `disallowed_paths`

Explicitly list forbidden solution classes.

Example:

```yaml
disallowed_paths:
  paths:
    - "OPENAI_API_KEY wiring"
    - "fake proof pass"
    - "broad architecture rewrite"
```

### `tasks`

Ordered bounded steps. These are not suggestions. They are the intended
execution envelope.

Each step should be:

- concrete
- bounded
- testable

Good:

1. read adapter, verifier, proof artifact, and targeted tests
2. inspect live seam
3. implement smallest honest pass path
4. run targeted tests and live verifier
5. refresh proof artifact
6. run docs check
7. commit if coherent

### `validation_loop`

Must tell the agent to keep going inside one run.

Recommended contents:

- targeted checks only
- repeat fix/test/proof loop until pass or real blocker
- refresh artifacts before returning

Example:

```yaml
validation_loop:
  checks:
    - "run targeted pytest slice"
    - "run live verifier"
    - "refresh proof artifact"
    - "run docs gate if files changed"
  rerun_policy: "Repeat the fix/test/proof loop until the bounded task passes or the remaining blocker is proven real."
```

### `success_criteria`

Must contain two tiers:

- `best_case`
- `acceptable_fallback`

This keeps the prompt honest while still pushing hard for completion.

### `report_contract`

Defines exactly what the final report must include.

Typical required fields:

- pass or blocked status
- proof artifact path and verification status
- exact live facts used in the conclusion
- files changed
- targeted test/proof results
- commit hash

## Repo-Specific Defaults

For this repo, the following defaults should usually be injected into prompts.

### Python execution default

```text
Use uv for all Python environment, dependency, script, and test execution. Do not use pip or create ad hoc venv/virtualenv environments unless you first prove uv cannot satisfy the requirement in this runtime.
```

### Runtime/proof default

```text
Run only targeted tests and live proof runs. Refresh the proof artifact before returning.
```

### Honesty default

```text
If it still cannot pass, keep the blocked state honest with exact live evidence.
```

### Commit default

```text
Run bash scripts/pre-commit-docs-check.sh if files changed. Make a commit if repo files changed, and report the hash.
```

## Human-Readable Prompt Template

Use this as the general-purpose fill-in template:

```text
Treat this as one continuous autonomous heavy run. Use the current pricing window aggressively. Complete the full bounded mission in one run: inspect -> patch -> targeted tests -> live proof -> fix -> rerun -> artifact refresh -> metadata/doc touch-up if needed -> docs check -> commit. Do not stop at diagnosis if the task can be carried through to an honest final state in this same run.

Mission:
[one bounded objective]

Current verified state:
- [fact]
- [fact]
- [fact]

Hard operating rules:
- [environment rule]
- [safety rule]
- [truthfulness rule]

Acceptable solution paths:
1. [allowed path]
2. [allowed path]

Unacceptable solution paths:
- [disallowed path]
- [disallowed path]

Tasks:
1. [bounded task]
2. [bounded task]
3. [bounded task]
4. [bounded task]

Validation loop:
- [targeted check]
- [targeted check]
- [artifact refresh]
- [docs gate if changed]
- Repeat the fix/test/proof loop until pass or real blocker.

Success criteria:
- Best case: [best case]
- Acceptable fallback: [honest fallback]

After changes, report:
1. [status field]
2. [artifact field]
3. [live evidence field]
4. [files field]
5. [test/proof field]
6. [commit field]
```

## Machine-Readable Semantics

This schema package works best when prompts can be represented in both:

- human-readable execution prose
- machine-readable structured metadata

The structured version should preserve:

- scope
- rules
- task order
- validation gates
- success/fallback contract

## Usage Guidance

Use this schema when:

- the task is expensive enough to justify a heavy autonomous run
- the boundary is already clear
- we want reproducibility across agents
- we want future prompt quality to improve instead of depending on ad hoc wording

Do not use this schema for:

- trivial one-line tasks
- simple copy edits
- cases where no bounded objective exists yet

## Expected Benefit

If followed well, this schema should reduce:

- agent scope drift
- repeated rediscovery of old blockers
- environment/tooling mistakes
- fake-green outcomes
- prompt-by-prompt improvisation

And it should improve:

- portability across agents
- reproducibility
- truthfulness
- landable bounded commits

