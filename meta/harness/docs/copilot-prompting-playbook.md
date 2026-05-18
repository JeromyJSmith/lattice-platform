# GitHub Copilot Prompting Playbook

Last updated: 2026-05-18

## Purpose

This document defines how we should use terminal GitHub Copilot in this repo for the next few weeks.

It is based on two things together:

1. the current temporary GitHub Copilot pricing window, where very large autonomous sessions can still be unusually cheap relative to raw token/API cost
2. what actually worked in LATTICE, so we exploit that window without burning time on sloppy prompts

This means the goal is not to be conservative with Copilot usage right now. The goal is to spend the current arbitrage window on the heaviest real repo work while keeping the prompts bounded enough to produce landable results.

The playbook therefore combines:

- give Copilot one bounded objective
- force it to operate on real repo truth
- require real proof artifacts and tests
- accept honest blocked states instead of fake-green output
- inspect or commit only coherent slices

## Python Environment Rule

For this repo and adjacent local work, Python environment and dependency management must be expressed through `uv`, not ad hoc Python tooling.

Hard rules:

- use `uv run ...` for Python script execution
- use `uv run --project pixeltable ...` when the `pixeltable/` project boundary is the real runtime
- use `uv sync` / `uv sync --project ...` to materialize Python environments
- use `uv add`, `uv remove`, or direct project-file edits plus `uv sync` for dependency changes
- prefer `uv tool run` or `uvx` for one-off Python tools

Do **not** let Copilot default to:

- `pip install ...`
- `python3 -m pip install ...`
- ad hoc `venv` or `virtualenv` creation
- system Python package mutation
- mixed environment strategies inside one run

The only acceptable fallback is:

- explicitly prove that `uv` cannot satisfy the need in the current environment
- record that failure honestly
- only then use the smallest temporary fallback if the task absolutely requires it

Prompt language should make this explicit. The easiest version is:

- `Use uv for all Python environment, dependency, script, and test execution. Do not use pip or create ad hoc venv/virtualenv environments unless you first prove uv cannot satisfy the requirement in this runtime.`

## Core Rule

Do not prompt Copilot like a chatbot.

Prompt it like a bounded execution worker that is allowed to burn a lot of compute inside one run:

1. one capability or one blocker class
2. one explicit scope
3. real tests and proof runs
4. explicit "stay blocked if not real"
5. explicit report format

Inside that bounded scope, we should absolutely let Copilot do heavy work:

- full repo scans within the bounded area
- multi-step retry/fix/test loops
- direct runtime probing
- verifier reruns
- diff refreshes
- repeated compile/test iterations

## What Worked Best Here

The most effective pattern in this repo has been:

1. I diagnose the real blocker locally.
2. We give Copilot a narrow `gh copilot -p "..." --allow-all` command.
3. Copilot edits code, runs targeted checks, and reports back.
4. We inspect the diff and proof artifacts.
5. We commit only bounded truth.

This does **not** conflict with the video’s advice. The right interpretation is:

- go big on compute
- stay sharp on scope

In other words:

- expensive inside the box
- narrow at the boundary

This worked well for:

- proof-trust hardening on `main`
- `cwicr-qdrant-cost-search`
- `boq-read`
- `boq-export`
- `boq-sync`
- `cwicr-seed`
- `phases-sync`
- ERP runtime + Portless + auth correction

## What To Avoid

Avoid prompts that:

- ask for broad cleanup or general improvement
- ask for "analyze and recommend" when we already know the blocker
- ask for multiple unrelated capabilities in one run
- ask for architecture rewrites
- let Copilot decide its own scope
- assume localhost ports without checking Portless/runtime truth
- ask it to "make green" without allowing honest red/blocked outcomes

Avoid being cheap with Copilot on token-heavy work during the current window. Do **not** waste the pricing asymmetry on tiny autocomplete-grade tasks if there is a heavier blocker-resolution task ready.

Avoid `gh copilot suggest -t shell` for repo work unless the task is trivial. It is less constrained than the `-p` flow and easier to mis-steer.

## Standard Prompt Shape

Use this structure:

```text
Work only on the smallest bounded surface needed for [one capability or one blocker].

Current verified state:
- [facts already known]
- [facts already known]

Tasks:
1. [bounded task]
2. [bounded task]
3. [bounded task]

Rules:
- Do not broaden into unrelated capability work.
- Do not undo the current runtime/auth/proof path.
- Keep changes bounded to [specific files or surfaces].
- Run only targeted tests and live proof runs.
- Run bash scripts/pre-commit-docs-check.sh if files changed.
- Make a commit if repo files changed, and report the hash.

After changes, report:
1. [pass/blocked status]
2. [proof artifact path and verification status]
3. [files changed]
4. [targeted test/proof results]
5. [commit hash if created]
```

## Prompting Rules For This Repo

### 1. Always anchor on current verified state

Before asking Copilot to act, give it the current truth:

- what already passes
- what is still blocked
- exact blocker text if we know it
- exact runtime URL if relevant
- exact branch or baseline if relevant

This prevents Copilot from re-solving old problems.

### 2. Force bounded scope

Always name the exact capability or blocker class.

Good:

- `boq-sync`
- `cwicr-seed`
- ERP auth bootstrap
- Portless ERP route
- project-scoped IFC seam

Bad:

- DDC integration
- improve ERP
- make the matrix greener

Bounded scope does **not** mean "small amount of work." It means "clear boundary." Inside that boundary, ask for the full heavy loop.

### 3. Prefer blocker-oriented prompts after enough proof surfaces exist

Early on, capability-oriented prompts were best.

Now that several proof surfaces exist, blocker-oriented prompts are often better:

- ERP runtime identity
- ERP auth
- project seam
- schedule seam
- CWICR dataset contract

If multiple capabilities share the same blocker, attack the blocker, not each capability separately.

### 4. Require honest failure

Always include language like:

- "If it still cannot pass, keep the blocked state honest with exact live evidence."
- "Prefer a real failed proof over fake-green or mock-success proof."

This repo benefits more from truthful red than from fake green.

### 5. Demand the same auth/runtime path everywhere

Do not allow Copilot to invent alternate auth or runtime modes.

For example:

- use the same UI-equivalent login-authenticated state
- use Portless namespace as source of truth
- do not drift back to `localhost:8080`

### 6. Require targeted tests only

Do not ask Copilot to run the whole world unless necessary.

Prefer:

- `uv run --project pixeltable pytest ...specific tests...`
- one verifier script
- one harness proof refresh
- docs sync check

When the bounded slice is Python-heavy, prefer commands written in this style:

- `uv run python scripts/...`
- `uv run --project pixeltable python scripts/...`
- `uv run pytest ...`
- `uv run --project pixeltable pytest ...`

But within the bounded slice, do let Copilot do repeated retries and self-correction loops before it returns.

### 7. Require commit only if coherent

This line should appear in almost every prompt:

- "Make a commit if repo files changed, and report the hash."

That keeps successful bounded slices landable.

## Recommended Command Style

Use:

```bash
gh copilot -p "..." --allow-all
```

Why:

- it gives Copilot enough tool access to inspect, edit, and test
- the prompt itself is where we constrain behavior

The old narrow tool-allowlisting (`--allow-tool 'shell(git:*)'`) was too restrictive for real repo work.

## Use The Pricing Window Aggressively

For the current temporary Copilot pricing window, the default should be:

- decline tiny tasks
- assign heavy bounded tasks
- ask for autonomous loops in one run

Good use of the window:

- runtime bring-up
- endpoint contract discovery
- full bounded adapter/verifier rewrites
- targeted migration loops
- proof refresh across a capability slice
- repeated test/fix/test cycles

Poor use of the window:

- one-off line edits
- lightweight rewrites we could do instantly ourselves
- unscoped research rambles

## Autonomous Loop Language To Include

When the task is heavy enough, explicitly tell Copilot to keep going inside one run.

Useful phrases:

- "Treat this as one bounded autonomous execution task."
- "Do not stop after analysis; implement, test, fix, and rerun within this same pass."
- "Repeat the fix/test loop until the targeted checks pass or the blocker is proven real."
- "Do not ask for permission between steps inside this bounded scope."
- "Use uv for all Python environment, dependency, script, and test execution."

This captures the real benefit from the pricing window while keeping the repo-safe constraints intact.

## Operating Modes

### Capability mode

Use when:

- a capability has no real proof path yet
- the next step is wiring a verifier or bounded route/adapter

Examples:

- `boq-read`
- `boq-export`
- `cwicr-qdrant-cost-search`

### Blocker mode

Use when:

- several proof surfaces already exist
- multiple capabilities share the same failure class

Examples:

- Portless ERP runtime
- ERP auth bootstrap
- local project IFC seam
- CWICR dataset mismatch

## Approval Heuristics

Accept a Copilot run when:

- scope stayed bounded
- proof artifact is real
- tests ran and make sense
- blocked state is concrete and useful
- diff is coherent

Do not accept blindly when:

- the diff is much larger than the stated scope
- it rewrites adjacent systems
- it invents fake data or fake proof
- it claims success without proof artifact refresh

## Current Repo Pattern To Reuse

The most reliable sequence has been:

1. diagnose locally
2. prompt Copilot with bounded `-p`
3. inspect proof artifact + diff
4. commit the truth
5. push `main`
6. pick next blocker from updated evidence

## Temporary Copilot Pricing Window

If GitHub Copilot still treats a long autonomous agent session as effectively one premium request in the current temporary pricing window, then we should spend that budget on the heaviest bounded tasks:

- runtime bring-up
- contract discovery
- proof-backed migrations
- refactors with test loops
- blocker resolution that would be expensive via direct token billing

But even during that window, keep prompts bounded. "Unlimited" execution value is not a reason to let scope sprawl.

## Ready-To-Use Mini Templates

### Bounded capability prompt

```text
Work only on the smallest bounded surface needed for [capability].

Current verified state:
- [truth]
- [truth]

Tasks:
1. [wire/tighten route or adapter]
2. [add or rerun verifier/proof path]
3. [update only directly related metadata/tests]
4. Treat this as one bounded autonomous execution task: implement, rerun targeted tests/proofs, fix failures, and repeat until the targeted checks pass or the remaining blocker is proven real.

Rules:
- Do not broaden into unrelated capability work.
- Keep blocked state honest if it still cannot pass.
- Run only targeted tests and proof runs.
- Run bash scripts/pre-commit-docs-check.sh if files changed.
- Make a commit if repo files changed, and report the hash.
```

### Shared blocker prompt

```text
Work only on the smallest bounded surface needed to reduce the shared blocker for [capability A], [capability B], [capability C].

Current verified state:
- [truth]
- [truth]

Tasks:
1. [discover real contract/runtime/seam]
2. [correct only directly related files]
3. [rerun targeted proofs]
4. Treat this as one bounded autonomous execution task: continue through diagnosis, edits, reruns, and self-correction without stopping early.

Rules:
- Do not broaden into unrelated work.
- Do not add new proof-only surfaces unless strictly needed.
- Keep blocked state honest if not fully resolved.
- Run bash scripts/pre-commit-docs-check.sh if files changed.
- Make a commit if repo files changed, and report the hash.
```

## Final Rule

In this repo, the goal is not to get Copilot to "do a lot."

The goal is to get Copilot to land one truthful, bounded, verifier-backed step at a time, while fully exploiting the current high-compute low-friction pricing window inside that step.
