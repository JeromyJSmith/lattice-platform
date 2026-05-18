# Local Meta Wrapper Golden Path

## End state

This project-local wrapper cleanly connects the outer reusable parent wrapper
to the inner `meta/harness/` execution layer.

## Path

1. Agent lands in repo-local `meta/`.
2. Agent reads `AGENTS.md`, `CLAUDE.md`, `MEMORY.md`, `GOAL.md`, and
   `GOLDENPATH.md`.
3. Agent understands the local doctrine and where the execution surfaces live.
4. Agent hands off to `meta/harness/` for score loops, proof runs, gate work,
   and the harness catalog/config spine in `meta/harness/library.yaml`.
5. Project-local truth can be summarized upward to the parent wrapper through
   durable artifacts.

## Guardrails

- This layer must remain project-specific.
- It should not duplicate every execution detail from `meta/harness/`.
- It must preserve the same minimum fractal scaffold as the parent and child
  layers around it.
