<!-- spec-verified: code.claude.com/docs 2026-05-11 -->
# LATTICE Verifier

LATTICE is the enclosing system. Pi, Codex, Claude CLI, Copilot, Symphony, GitHub, Linear, Pixeltable, OpenRouter, Ollama, MLX, local models, and the verification loop are capabilities inside that system.

The verifier is a LATTICE harness function, not a separate product and not an agent role. Any builder can do the work; the verifier proves whether the work matches the issue, the diff, the harness contract, and the hard rules.

## Runtime model

LATTICE can use Pi as one execution surface for verification:

- Pi runs the builder session.
- A sibling Pi verifier observes the builder session JSONL.
- The builder forwards lifecycle events over a Unix domain socket as JSONL.
- The verifier reads only the relevant session slice for the turn.
- The verifier decomposes the user request and builder claims into atomic checks.
- The verifier runs deterministic, read-only, script-only commands.
- If a claim fails, the verifier sends one concrete corrective prompt back to the builder.
- After the configured loop limit, it escalates to the human.

Pi is inside LATTICE. Pi is the default harness task runner for bounded script/prompt/model jobs, and the verifier loop is one Pi job type. The LATTICE verifier contract defines what counts as evidence.

Delegation model: see `meta/harness/delegation-model.md`.

## Deterministic core

Use:

```bash
bash scripts/lattice-verify.sh
```

Optional base ref:

```bash
bash scripts/lattice-verify.sh origin/feature/meta-harness
```

The core currently checks:

- `.env*` files are not changed by agents
- landed migrations `0001` through `0016` are not edited
- migrations are not deleted
- `git diff --check`
- `scripts/audit-dead-dna.sh`
- `scripts/pre-commit-docs-check.sh`

The verifier core should grow by adding deterministic scripts, not by adding vague prompt instructions. Python, C++, Vectorworks plugin work, scripting, docs, sync, and model delegation all need concrete commands that can run once, emit an artifact, and pass/fail.

## Verifier persona contract

A Pi verifier persona for this repo should use read-only tools only and treat `scripts/lattice-verify.sh` as the first oracle. It may inspect files, diffs, logs, CI output, Linear/GitHub sync evidence, and harness reports, but it must not write, edit, install, delete, merge, or mutate remote state.

Bash policy for the verifier is script-only: call repo-owned verification scripts, do not improvise shell workflows.

Every report should use this shape:

```text
## Report
STATUS: verified | failed | unsure
CONFIDENCE: PERFECT | VERIFIED | PARTIAL | FEEDBACK | FAILED
### What did you verify?
### What could you not verify?
### What feedback did you give?
### What do you need from me to verify this next time?
### Verification metadata
```

## Hard prohibitions

These survive every workflow model:

- no editing landed migrations
- no secrets, `.env*`, or OAuth credentials
- no branch protection changes
- no merges to `main`
- no deletions of migrations, branches, or issues
- no incidental doctrine changes
