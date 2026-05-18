# Local Meta Wrapper Goal

## Purpose

This local `meta/` directory is the project-specific child wrapper for the
LATTICE body cell.

It bridges the reusable parent wrapper above this repo to the more specific
execution surfaces under `meta/harness/`.

## Goal

The local wrapper is complete when it can:

1. expose the project-local doctrine, contracts, and architecture surfaces
2. point cleanly at the active execution wrapper under `meta/harness/`
3. translate project-local truth into durable artifacts the parent wrapper can
   understand
4. preserve the same fractal five-file scaffold as every other wrapper layer

## Minimum fractal contract

This directory should always contain:

- `AGENTS.md`
- `CLAUDE.md`
- `MEMORY.md`
- `GOAL.md`
- `GOLDENPATH.md`

## Downstream execution surface

- `meta/harness/`
- `meta/harness/library.yaml`
