# Meta-Harness

The Meta-Harness is the LATTICE improvement and verification layer. It inventories capabilities, decides what to activate, runs bounded jobs, verifies outcomes, and records evidence.

LATTICE is the enclosing system. Pi, Claude CLI, Codex, Copilot, Symphony, GitHub, Linear, Pixeltable, DuckDB WASM, OpenRouter, Ollama, MLX, Graphify, GitNexus, InfraNodus, and local models are execution or analysis surfaces inside LATTICE.

## Current Doctrine

- The outer wrapper lives at `/Volumes/PixelTable/VW_iTWIN_Bridge/meta/`; this repo is the active body cell registered by that wrapper.
- Pixeltable is the LATTICE operational substrate and eventual system of record.
- Git remains the source and change-control surface while the substrate matures.
- DuckDB WASM is the browser analytical surface over Pixeltable-served Arrow and Parquet.
- Capability Harvest feeds a Capability Matrix. A capability enters the Manifest and Registry only after a proof run produces the desired outcome and evidence.
- No agent has exclusive file-path ownership. Work is dispatched by current context, cost, availability, and verification needs.
- Every new or changed Python file must have module and public-symbol docstrings.
- Runnable one-shot Python harness jobs should use uv inline metadata.

## Entry Points

| File | Purpose |
|---|---|
| `meta/harness/HANDOFF-NEXT-SESSION.md` | Current next-session handoff, including Golden Path 002 and DDC installation plan |
| `meta/harness/CURRENT-STATE.md` | Snapshot of what exists right now |
| `meta/harness/TODO.md` | Prioritized Meta-Harness work queue |
| `meta/harness/golden_path.md` | First success-defined path for promoting a single-file harness agent |
| `/harness/capabilities` | Browser pre-flight table for capability registry contracts and evidence |
| `meta/harness/source-grounding.md` | Source lineage and constraints from Meta-Harness, GOAL.md, and autoresearch |
| `meta/harness/domain_spec.md` | Required onboarding artifact before the first real dry run |
| `meta/harness/pixeltable-operational-substrate.md` | Pixeltable substrate doctrine and staged integration |
| `meta/harness/docs/capability-lifecycle.md` | Harvest to matrix to manifest to registry lifecycle |
| `meta/harness/library.yaml` | Portable catalog of harness prompts, capabilities, references, and jobs |
| `meta/verification/VERIFIER.md` | Verifier contract and deterministic core |

## Core Checks

```bash
bash scripts/lattice-verify.sh HEAD
bash scripts/pre-commit-docs-check.sh
bash scripts/audit-dead-dna.sh
uv run python scripts/check-python-docstrings.py
```

Use `uv run python scripts/check-python-docstrings.py --all` only for a deliberate full legacy uplift pass. Landed migrations `0001` through `0016` are write-once and excluded from automated docstring rewrites.

## Hard Stops

- Do not edit landed migrations `0001` through `0016`.
- Do not touch secrets, `.env*`, or OAuth credentials.
- Do not change branch protection or merge to `main`.
- Do not delete migrations, branches, or issues.
- Do not make incidental doctrine changes. Doctrine changes must be the point of the PR.

## Near-Term Direction

The current branch is still the body-cell incubation surface. Before the first dry run, reconcile the outer wrapper contract, documentation mirror contract, Pixeltable docs substrate, and `domain_spec.md` so the run has the right enclosure and a scored evaluation target. The target architecture is a portable Meta-Harness repo that can snap into LATTICE or another repository through config, library references, capability manifests, and Pixeltable-backed evidence.
