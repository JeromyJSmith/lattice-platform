# Local Meta Wrapper Memory

## Stable truths

- This directory is the child wrapper for the LATTICE repo.
- It is not the runtime itself; it is the project-local meta surface above
  `meta/harness/`.
- The execution-oriented self-improvement layer currently lives in
  `meta/harness/`.
- The harness catalog/config spine currently lives in
  `meta/harness/library.yaml`.
- The wrapper model is fractal and should repeat the same five-file scaffold
  at every level.

## Current role

- hold project-local architecture, schema, mapping, and operational documents
- point agents toward `meta/harness/` for score loops and proof execution
- stay understandable to the parent wrapper above the repo

## Open decisions

- how much of the gate-state bridge should live here versus directly in
  `meta/harness/`
- which local documents should be elevated into canonical wrapper contracts
