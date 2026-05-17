---
name: fre-research-ratchet
description: Research-first Meta-Harness skill for bounded FRE and LATTICE evaluation loops. Use when work must begin with explicit research grounding, translate source packets into repo-local authority, run a score-before or score-after ratchet, accept only real improvements, stop on plateau, and commit only after three consecutive accepted improvements. Trigger when users ask for autoresearch, continuous evaluation, self-improving harness behavior, research-first schema work, or Meta-Harness iteration inside meta/harness/fre.
---

# FRE Research Ratchet

## Overview

This skill composes research workflow, codebase research, self-improvement, and
the local Meta-Harness ratchet into one bounded FRE loop.

Use it when the task is not just "run tests" or "edit a schema", but:

- ground a loop in research before execution
- convert a copied source packet into local authority
- run deterministic evaluation cycles
- keep only score-improving iterations
- stop automatically when improvement stalls

## Workflow

### 1. Ground the loop in research first

Before touching schemas, examples, or scorers:

1. Read the primary source packet.
2. Read the local Meta-Harness doctrine:
   - `meta/harness/CLAUDE.md`
   - `meta/harness/GOAL.md`
3. Read the current bounded FRE docs:
   - `meta/harness/fre/docs/sources.md`
   - `meta/harness/fre/docs/source-normalization.md`
   - `meta/harness/fre/docs/research-grounding.md`
   - `meta/harness/fre/docs/research-findings.md`
4. If the task depends on outside skill patterns, read
   `references/skills-landscape.md`.

Never allow the loop to claim progress if the research layer is missing.

### 2. Define the local authority chain

The canonical chain for this skill is:

```text
research -> source -> schema -> examples -> validation -> metrics -> repair task -> promotion decision
```

Do not collapse `research` into `source`. A copied source bundle is not enough.

### 3. Run the bounded ratchet

Use the wrapper script:

```bash
bash meta/harness/fre/skills/fre-research-ratchet/scripts/run_fre_research_first_cycle.sh
```

This runs:

1. research artifact presence checks
2. FRE tests
3. the bounded iteration loop at `meta/harness/fre/harness/iterate.py`

### 4. Accept only real improvements

The ratchet rules are strict:

- compare `score_after` to the last complete accepted run
- keep only runs with `score_after > score_before`
- stop on the first plateau or regression
- do not commit unless three consecutive accepted improvements occur

If the loop exposes a scorer bug, contract bug, or artifact-order bug, fix the
loop first. Do not count broken scoring as progress.

### 5. Treat real fixtures as stronger evidence than toy examples

After the contract is stable, prefer real artifact pressure tests over more
schema-only passes. Read `references/local-doctrine-map.md` before widening the
fixture set.

## Expected Outputs

Each accepted cycle should leave:

- a new immutable run under `meta/harness/fre/runs/`
- updated session summary under `meta/harness/fre/docs/sessions/`
- a clear score comparison against the last accepted run

## Resources

### `references/skills-landscape.md`

External skill research from skills.sh and which patterns belong in this local
skill.

### `references/local-doctrine-map.md`

How this skill maps onto the LATTICE Meta-Harness and local autoresearch loop.

### `scripts/run_fre_research_first_cycle.sh`

Deterministic wrapper for the research-first FRE cycle.
