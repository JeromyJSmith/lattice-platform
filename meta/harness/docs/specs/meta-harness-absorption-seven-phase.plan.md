---
id: "meta-harness-absorption-seven-phase"
slug: "meta-harness-absorption-seven-phase"
doctype: "plan"
status: "active"
version: "1.0.0"
owner: "meta-harness"
execution_mode: "bounded_absorption_run"
scope: "portable_parent_wrapper_repo"
source_repos:
  - "/Volumes/PixelTable/VW_iTwin_Bridge/meta"
  - "/Volumes/PixelTable/VW_iTWIN_Bridge/lattice-worktrees/feat-fre-meta-harness-eval/meta/harness/fre"
child_bodies:
  - "/Volumes/PixelTable/VW_iTWIN_Bridge/VW_iTwin_Bridge"
required_lifecycle_gates:
  - "harvest_gate"
  - "registry_gate"
  - "manifest_gate"
  - "verification_gate"
  - "state_gate"
  - "health_gate"
  - "promotion_gate"
required_proof_package_parts:
  - "source"
  - "schema"
  - "examples"
  - "expected_failures"
  - "tests"
  - "evaluation"
  - "promotion"
---

# Meta-Harness Absorption Seven-Phase Plan

## Purpose

Create the standalone reusable `meta-harness` parent repository by absorbing
the existing parent `meta/` scaffold and the bounded FRE contract lane into one
portable control-plane repo.

The absorption must follow the same fractal lifecycle used inside LATTICE.
Nothing is copied upward informally. Everything is harvested, registered,
manifested, verified, state-scored, health-checked, and only then promoted into
the parent wrapper repo.

Every required Markdown contract surface in the parent repo must carry both:

- top YAML front matter
- bottom `---bottom-matter---` state

If a required Markdown scaffold file lacks either one, promotion remains
blocked.

## Source bodies to absorb

### Parent wrapper scaffold

- `/Volumes/PixelTable/VW_iTwin_Bridge/meta`

### FRE bounded lineage

- `/Volumes/PixelTable/VW_iTWIN_Bridge/lattice-worktrees/feat-fre-meta-harness-eval/meta/harness/fre`

### Child implementation body used as reference

- `/Volumes/PixelTable/VW_iTWIN_Bridge/VW_iTwin_Bridge`

## Seven lifecycle gates for absorption

### 1. Harvest Gate

Question: did we extract the reusable wrapper truth without inventing it?

Required harvest surfaces:

- parent wrapper scaffold files
- FRE schemas
- FRE examples and expected-failure registry
- FRE harness validators and tests
- FRE runs and promotion artifacts
- child mirror surfaces that must remain in LATTICE
- library/config spine:
  - `meta/harness/library.yaml`
  - `meta/harness/agentics-library.md`
- comparison and substrate hooks:
  - InfraNodus surfaces
  - Pixeltable hook surfaces
- governed prompt contract surfaces:
  - `agent-heavy-run-prompt-index.md`
  - `agent-heavy-run-prompt-schema.md`
  - `agent-heavy-run-prompt.schema.json`
  - `agent-heavy-run-prompt.template.yaml`
  - `copilot-prompting-playbook.md`

Harvest output requirements:

- source path inventory
- adoption candidates
- mirror-only candidates
- historical-only candidates
- explicit duplicates and drift findings

### 2. Registry Gate

Question: does every absorbed surface have a canonical identity and declared
role?

Registry requirements:

- canonical IDs for each absorbed contract family
- aliases for old FRE names where needed
- ownership:
  - parent-only
  - child-mirror
  - historical-lineage
- declared dependencies on:
  - library spine
  - prompt contract
  - Pixeltable substrate
  - InfraNodus comparison engine

### 3. Manifest Gate

Question: is each absorbed capability placed in the correct repo and layer?

Manifest decisions must classify each surface as one of:

- `adopt_to_parent`
- `mirror_to_child`
- `leave_historical`
- `delete_after_absorption`

Manifest must also define the parent repo top-level families:

- scaffold contract
- source
- schemas
- examples
- expected-failures
- tests
- evaluation
- promotion
- runs
- docs
- library/config
- prompts

Manifest must explicitly require the parent Markdown scaffold contract:

- `README.md`
- `AGENTS.md`
- `CLAUDE.md`
- `GOAL.md`
- `GOLDENPATH.md`
- `MEMORY.md`

### 4. Verification Gate

Question: can the absorbed parent repo prove its contract surfaces work?

Verification requirements:

- JSON Schema Draft 2020-12 validation
- valid examples pass
- invalid examples fail for exact reasons
- document-contract parsing works with front matter and bottom matter
- required parent Markdown scaffold files exist
- required parent Markdown scaffold files carry both front matter and bottom
  matter
- prompt contract hook remains valid
- the standalone parent repo carries the full governed prompt-contract set used
  by the Copilot playbook
- every heavy or bounded execution prompt in the parent repo must trace back to
  that prompt schema/playbook contract
- library/config references resolve
- Pixeltable substrate references resolve
- InfraNodus comparison references resolve where required

### 5. State Gate

Question: is the absorption status honest and evidence-derived?

State rules:

- red means missing absorbed contract or failed validator
- amber means bounded partial absorption with exact blockers
- green means verifier-backed parent surfaces plus clean parent-child mapping
- no artifact is green if it only exists as prose without proof package support

### 6. Health Gate

Question: is the parent repo internally consistent after absorption?

Health requirements:

- no duplicate contract authorities across parent and child without an explicit
  mirror rule
- no stale FRE lineage pointers that still reference child-only paths as
  canonical parent truth
- no schema/example/test drift
- no library/config references dangling
- no substrate/comparison hook documentation without matching contract fields

### 7. Promotion Gate

Question: is the standalone `meta-harness` repo ready to become the canonical
parent wrapper?

Promotion requirements:

- parent repo skeleton exists
- absorption map is complete
- parent proof package is runnable
- child LATTICE mirror contract is explicit
- FRE lineage is absorbed or deliberately retained as historical evidence
- no unresolved critical blocker on:
  - library spine
  - prompt contract
  - InfraNodus hook
  - Pixeltable substrate hook
- no missing governed prompt-contract artifact from the canonical set

## Seven-part proof package required inside the parent repo

### 1. `source/`

Contains:

- source inventories
- provenance records
- normalization records
- prompt-contract trace
- library/config trace
- prompt schema provenance

### 2. `schemas/`

Contains:

- lifecycle gate schemas
- proof package schemas
- front matter schema
- bottom matter schema
- gate progress schema
- bridge record schema
- any absorbed FRE runtime schemas
- governed heavy-run prompt schema

### 3. `examples/`

Contains:

- valid examples
- invalid examples
- library-aware examples
- substrate-aware examples
- comparison-aware examples where required

### 4. `expected-failures/`

Contains:

- exact failure registry
- anticipated breakage cases
- malformed-state expectations
- stale-reference expectations

### 5. `tests/`

Contains:

- document-contract tests
- failure example tests
- mapping tests
- schema validity tests
- research grounding and determinism checks where applicable
- prompt-contract validity checks

### 6. `evaluation/`

Contains:

- schema-validation outputs
- example-validation outputs
- test summaries
- gap analysis outputs
- drift comparison outputs
- InfraNodus comparison artifacts where required

### 7. `promotion/`

Contains:

- readiness summary
- promotion decision
- blocker carry-forward
- parent adoption status
- child mirror status

## Absorption priorities

### Priority 1

- parent wrapper scaffold at `/Volumes/PixelTable/VW_iTwin_Bridge/meta`
- FRE proof package contract lane
- prompt contract hook
- library/config spine

### Priority 2

- Pixeltable substrate bindings
- InfraNodus comparison bindings
- parent-child mirror contract for LATTICE

### Priority 3

- historical runs
- research sessions
- bounded lineage records preserved as evidence

## Non-negotiable rules

- FRE is absorbed into `meta-harness`, not left as a separate competing home
- LATTICE remains a child implementation body
- parent repo becomes the canonical source for reusable wrapper doctrine
- child repo keeps only mirrors and local execution adaptations
- every absorbed surface must pass through the full seven-gate lifecycle
- every promoted surface must have proof-package backing

## Immediate next implementation slice

1. harvest the parent `meta/` scaffold into a machine-readable inventory
2. harvest the FRE worktree lane into a machine-readable inventory
3. build the adopt/mirror/historical absorption map
4. define the standalone `meta-harness` repo skeleton from that map
5. verify the first parent proof-package slice before any large copy or move

---bottom-matter---
status_summary:
  completeness: 0.82
  confidence: high
  doc_state: active_plan

gate_progress:
  - gate_id: harvest_gate
    status: green
    notes: "Source bodies and reusable surfaces are identified."
  - gate_id: registry_gate
    status: amber
    notes: "Canonical IDs and ownership classes still need a machine-readable registry."
  - gate_id: manifest_gate
    status: amber
    notes: "Adopt, mirror, historical, and delete decisions are defined conceptually but not yet materialized as the absorption map."
  - gate_id: verification_gate
    status: red
    notes: "Standalone parent repo validators do not exist yet."
  - gate_id: state_gate
    status: amber
    notes: "Current state is honest but still pre-repo-creation."
  - gate_id: health_gate
    status: amber
    notes: "Duplicate authority risk remains until parent and child boundaries are codified."
  - gate_id: promotion_gate
    status: red
    notes: "Standalone meta-harness repo does not yet exist."

open_questions:
  - "Which existing parent-level docs become canonical parent repo docs versus historical input artifacts?"
  - "How much of the FRE run history should be absorbed as live parent evidence versus archived lineage?"

pending_validations:
  - "Create a machine-readable harvest inventory for parent meta scaffold."
  - "Create a machine-readable harvest inventory for FRE worktree lane."
  - "Verify the first parent repo skeleton against the seven-part proof package."

promotion_criteria:
  - "Standalone meta-harness repo skeleton exists."
  - "Absorption map is complete and verified."
  - "Parent proof package validates with real tests."
  - "LATTICE child mirror contract is explicit."

blocked_by:
  - "No standalone parent repository has been initialized yet."

next_iteration:
  owner: "codex"
  objective: "Create the harvest inventories and the adopt/mirror/historical absorption map for the standalone meta-harness repo."
