# Copilot Shell-Safe Heavy-Run Template

Last updated: 2026-05-18

## Purpose

This template exists to prevent shell-breakage when running a heavy GitHub
Copilot prompt from the terminal.

Use this when the task needs:

- one bounded heavy run
- repeated self-correction inside that bounded scope
- `uv`-first Python execution
- safe shell wrapping with no accidental command substitution

## Canonical Shape

Use this exact outer structure:

```bash
cd /Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge
gh copilot -p '...plain prompt text...' --allow-all
```

## Non-Negotiable Shell Rules

1. The prompt body must be wrapped in plain ASCII single quotes.
2. Do not use backticks anywhere inside the prompt body.
3. Do not use `$()` anywhere inside the prompt body.
4. Do not use shell variables like `$FOO` inside the prompt body.
5. Do not use apostrophes or contractions inside the prompt body, because they
   break the surrounding single-quoted shell string.
6. Do not paste smart quotes or other editor-substituted quote characters.
7. Capability IDs, file paths, and commands inside the prompt body are plain
   text, not markdown formatting.
8. If the prompt mentions Python tooling, it must say `uv`, not `pip`,
   `poetry`, `conda`, `venv`, or `virtualenv`.

## Why Prior Runs Broke

These patterns are unsafe in a shell-passed prompt:

```bash
gh copilot -p " ... `boq-sync` ... " --allow-all
gh copilot -p " ... $(cat file) ... " --allow-all
```

They trigger shell evaluation before Copilot receives the prompt.

Typical failure symptoms:

- `zsh: command not found: boq-sync`
- `zsh: permission denied: ddc/GOAL.md`
- `uv` help output appearing unexpectedly

## Safe Prompt Skeleton

Copy this and replace the placeholder sections.

```bash
cd /Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge
gh copilot -p 'Treat this as one continuous autonomous heavy run. Use the current Copilot pricing window aggressively.

Mission:
[one bounded objective]

Current verified state:
- [fact]
- [fact]

Tasks:
1. [read current truth]
2. [inspect bounded runtime or repo surfaces]
3. [implement the smallest honest slice]
4. [re-read changed surfaces]
5. [compare cross-surface truth]
6. [patch again if needed]
7. [run checks]
8. [final self-audit]
9. [commit if clean]

Hard operating rules:
- Use uv for Python execution and environment management if Python is needed.
- Do not use pip, python -m pip, venv, virtualenv, poetry, or conda.
- No fake green states.
- No shallow one-file fix if directly related truth surfaces remain inconsistent.
- Keep scope bounded to the named slice.

FRE self-loop requirement:
- define the concrete goal
- use the golden path as the execution target
- loop back on your own output
- fail closed on unresolved drift
- do not stop at the first plausible patch if cross-surface truth is still inconsistent

Validation loop:
1. [search for stale IDs or drift]
2. [confirm canonical forms remain]
3. Run bash scripts/pre-commit-docs-check.sh
4. Run the targeted verifier, test, or build commands
5. Run git diff --check
6. Re-read the final diff and confirm the slice is coherent
7. Commit only if the slice is clean

Output:
1. [canonical IDs or truth chosen]
2. [files changed]
3. [validation results]
4. [final self-audit result]
5. [commit hash if created]

Do not stop at analysis if the bounded repair slice can be landed honestly in this same run.' --allow-all
```

## Pre-Run Checklist

Before pressing enter, verify:

- the repo root after `cd` is correct
- the prompt body contains no single quote characters
- the prompt body contains no backticks
- the prompt body contains no `$()` or `$NAME`
- `uv` is the only Python environment tool named
- the mission is one bounded objective, not a whole-program rewrite

## Relationship To Other Prompt Artifacts

- `agent-heavy-run-prompt-schema.md` defines the logical contract
- `agent-heavy-run-prompt.template.yaml` defines the structured prompt fields
- this file defines the shell-safe terminal invocation shape

Use this file when you are about to paste a terminal Copilot command and want to
avoid shell corruption.
