# Skills Landscape

This file records the outside skills that most closely match the bounded FRE
evaluation problem.

## Researched Skills

### `openai/skills/skill-creator`

Why it matters:

- gives the canonical skill structure
- defines the creation sequence
- requires concrete examples before implementation
- recommends lean `SKILL.md` files and optional scripts or references

Borrowed pattern:

- use the official folder shape
- keep only `name` and `description` in frontmatter
- put detailed research and doctrine in references files

### `jwynia/agent-skills/research-workflow`

Why it matters:

- makes research a formal first phase
- separates planning, execution, and synthesis
- fits the user's requirement that research happens before implementation

Borrowed pattern:

- force explicit research grounding before schema work

### `ferueda/agent-skills/research-codebase`

Why it matters:

- prioritizes direct file reading before theory
- treats the local codebase as primary truth
- insists on synthesis from real files

Borrowed pattern:

- read local doctrine and current files before changing the loop

### `charon-fan/agent-playbook/self-improving-agent`

Why it matters:

- centers iterative self-correction
- treats failures as learning signals
- keeps traceable evolution markers

Borrowed pattern:

- log lessons through immutable runs and session summaries

### `browserbase/skills/autobrowse`

Why it matters:

- separates an inner execution loop from an outer improvement loop
- repeats until the behavior stabilizes

Borrowed pattern:

- outer ratchet inspects the inner run and decides whether to keep it

### Local `codex-autoresearch-loop`

Why it matters:

- closest local expression of the user's "keep looping, verify, and stop only
  when the metric stops improving"
- includes keep or revert logic and plateau handling

Borrowed pattern:

- use a bounded modify -> verify -> keep or stop loop

## Composition Decision

This local FRE skill is not a copy of any one external skill.

It composes:

- official skill structure from `skill-creator`
- research-first sequencing from `research-workflow`
- codebase-truth discipline from `research-codebase`
- iterative correction from `self-improving-agent`
- outer-loop improvement logic from `autobrowse`
- local loop behavior from `codex-autoresearch-loop`
