# Local Harness Agents

## Purpose

This directory is the innermost active self-improvement wrapper for the LATTICE
repo.

It owns the concrete scoring loops, verifier paths, proof artifacts, and
bounded capability-promotion work. Its catalog/config spine lives in
`library.yaml`.

## Minimum fractal contract

This harness layer is only complete when the following same-level files exist:

- `AGENTS.md`
- `CLAUDE.md`
- `MEMORY.md`
- `GOAL.md`
- `GOLDENPATH.md`

The detailed execution path still lives in `golden_path.md`; `GOLDENPATH.md`
is the fractal peer that points at it.

## Role

- run bounded score and proof loops
- keep status honest
- emit durable artifacts for the outer wrapper layers
- preserve regression safety while the active gate improves
- treat `library.yaml` as the harness catalog/config authority

## Outer relationships

- parent child wrapper: `meta/`
- outer reusable wrapper: `../meta/`
