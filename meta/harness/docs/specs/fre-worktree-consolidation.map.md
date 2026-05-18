---
id: MAP-FRE-WORKTREE-CONSOLIDATION-0001
slug: fre-worktree-consolidation-map
title: FRE Worktree Consolidation Map
doctype: plan
status: draft
version: 0.1.0
owner: meta-wrapper-agent
created_at: 2026-05-18
updated_at: 2026-05-18
wrapper_scope: main-vs-worktree-reconciliation
execution_mode: dry-run-first
source_worktree: ../lattice-worktrees/feat-fre-meta-harness-eval
notion_parent_page: https://www.notion.so/362c487604f481fcb505d19d6b85a0d4
related_docs:
  - meta/harness/docs/specs/fre-worktree-consolidation.plan.md
  - meta/harness/docs/specs/fre-meta-wrapper-seven.gates.md
  - meta/harness/docs/specs/fre-meta-wrapper-implementation.plan.md
  - meta/harness/docs/specs/fre-infranodus-hook.plan.md
  - meta/harness/docs/specs/fre-pixeltable-hook.plan.md
---

# FRE Worktree Consolidation Map

## Purpose

This document maps the already-defined FRE contract from Notion and the sibling
evaluation worktree to the current `main` wrapper surfaces.

The goal is to stop re-inventing the same structure and instead decide, for
each major surface, whether it should be:

- adopted unchanged
- translated into the wrapper-gate vocabulary
- mirrored as a bounded historical lane
- or kept as historical lineage only

## High-level result

The sibling worktree proves that the deeper contract already exists.
Current `main` only has the outer wrapper scaffold and wrapper concept docs.

That means the next implementation work should mostly be consolidation and
translation, not invention.

## Namespace map

| Surface | Notion | Worktree | Current main | Decision | Notes |
|---|---|---|---|---|---|
| evaluation parent | `FRE Schema Evaluation Plan for LATTICE Meta-Harness` | none | none | historical + reference | Notion remains the narrative parent for the bounded evaluation lineage. |
| bounded FRE namespace | implied by Repository Shape page | `meta/harness/fre/**` | missing | decide restore or mirror | This is the biggest structural gap between worktree and `main`. |
| wrapper scaffold parent | not explicitly modeled | parent-level `../meta/` indirectly implied | present on disk above repo | adopt | Fractal outer wrapper is valid and should stay. |
| wrapper scaffold child | not explicitly modeled | repo-local `meta/` indirectly implied | present | adopt | Child wrapper layer is now scaffolded on `main`. |
| inner execution wrapper | bounded FRE namespace and local harness ideas | `meta/harness/fre/**` plus repo-local harness docs | `meta/harness/**` present, but older doctrine | translate | `meta/harness/` on `main` must absorb newer FRE contract lessons. |

## Core contract map

| Contract surface | Notion evidence | Worktree path | Current main path | State on main | Decision | Notes |
|---|---|---|---|---|---|---|
| mission chain | Evaluation Hypothesis | `meta/harness/fre/GOAL.md` | partial in wrapper docs only | missing in live harness | translate into main | Canonical chain is `source -> schema -> examples -> validation -> metrics -> repair task -> promotion decision`. |
| bounded evaluation boundary | Evaluation Boundary | `meta/harness/fre/CLAUDE.md`, `GOAL.md`, `GoldenPath.md` | missing | missing | keep historical for eval lane, translate principles | `main` should not blindly become the bounded eval namespace, but should inherit the boundary discipline. |
| success criteria | Success Criteria | tests + run artifacts | missing as wrapper criteria | missing | translate | Wrapper-level success criteria should become explicit. |
| ground rules | Ground Rules | `meta/harness/fre/CLAUDE.md` | partial | partial | translate | `uv`, bounded scope, no fake green, no production mutation all remain useful. |
| repository shape | Repository Shape | `meta/harness/fre/{schemas,examples,tests,harness,runs}` | missing | missing | adopt in some form | These folder families are likely needed for the reusable wrapper lane. |
| expected failure contracts | Expected Failure Contracts | `meta/harness/fre/examples/expected-failures.yaml` plus tests | missing | missing | adopt | This is a concrete missing piece on `main`. |
| translation map | FRE-to-LATTICE Translation Map | `meta/harness/fre/docs/fre-to-lattice-map.md` | missing | missing | adopt + extend | This is another concrete missing piece on `main`. |
| InfraNodus comparison hook | Ground Rules, Repository Shape, Success Criteria | `analysis/infranodus/**`, `.claude/rules/infranodus-corpus.md`, harness gap-analysis scripts | present but not integrated into wrapper specs | partial | adopt + make explicit | InfraNodus already exists locally as the graph comparison engine and must become first-class in wrapper contracts. |
| Pixeltable substrate hook | Architecture and runtime foundation docs | `pixeltable/**`, `meta/ARCHITECTURE.md`, `lattice/*` table families | present but not integrated into wrapper specs | partial | adopt + make explicit | Pixeltable is the durable multimodal substrate, not just one implementation detail. |

## Seven-part contract-package map

| Package part | Notion evidence | Worktree source | Current main status | Decision | Notes |
|---|---|---|---|---|---|
| source | Evaluation Hypothesis, Ground Rules, research pages | `meta/harness/fre/docs/{research-grounding.md,research-findings.md,sources.md,source-normalization.md}` | missing | adopt pattern | Source is the research and provenance layer, not just a citation footer. |
| schema | Evaluation Hypothesis, Repository Shape | `meta/harness/fre/schemas/*` | missing | adopt/translate | JSON Schema remains canonical. |
| examples | Success Criteria, Repository Shape | `meta/harness/fre/examples/*.valid.json` | missing | adopt pattern | Valid fixtures belong in the reusable package. |
| expected-failures | Expected Failure Contracts | `meta/harness/fre/examples/expected-failures.yaml` plus invalid fixtures | missing | adopt | This is the explicit anticipation layer. |
| tests | Success Criteria | `meta/harness/fre/tests/*` | missing | adopt pattern | Contract and failure tests should be ported first. |
| evaluation | Success Criteria, run-ledger thinking | `meta/harness/fre/harness/{evaluate.py,report.py,evaluate_real_fixtures.py}` plus `runs/*` | missing | translate | Evaluation is a distinct artifact layer, not implied by tests. |
| promotion | Success Criteria, translation map | `meta/harness/fre/schemas/promotion-decision.schema.json`, `runs/*/promotion-decision.md` | missing | adopt/translate | Promotion is distinct from evaluation and must remain separate. |

## Schema family map

| Schema family | Worktree source | Current main status | Decision | Notes |
|---|---|---|---|---|
| loop schema | `meta/harness/fre/schemas/fre-loop.schema.json` | missing | translate | Wrapper-wide gate-loop contract may be derived from this. |
| gate result schema | `meta/harness/fre/schemas/gate-result.schema.json` | missing | adopt/translate | Likely reusable with naming adjustments. |
| repair task schema | `meta/harness/fre/schemas/repair-task.schema.json` | missing | adopt/translate | Directly relevant to wrapper repair flows. |
| promotion decision schema | `meta/harness/fre/schemas/promotion-decision.schema.json` | missing | adopt/translate | Directly relevant to gate promotion. |
| front matter schema | bounded by document contract tests, not standalone file | missing | create on main | Current wrapper docs need this explicitly. |
| bottom matter schema | bounded by document contract tests, not standalone file | missing | create on main | Current wrapper docs need this explicitly. |
| gate progress schema | implied by new wrapper docs | missing | create on main | New local concept but not yet formalized as schema. |
| bridge record schema | implied by wrapper docs | missing | create on main | New local concept but not yet formalized as schema. |

## Example and failure map

| Example surface | Worktree source | Current main status | Decision | Notes |
|---|---|---|---|---|
| valid examples | `meta/harness/fre/examples/*.valid.json` | missing | adopt pattern | Main wrapper needs valid example fixtures per schema family. |
| invalid examples | `fre-loop.invalid.*.json` | missing | adopt pattern | Main wrapper needs invalid fixtures, not just happy-path prose. |
| expected failure registry | `examples/expected-failures.yaml` | missing | adopt | Needed for exact-failure validation. |
| real fixtures | `fixtures/*` | missing | keep bounded or adapt | Some belong to the FRE evaluation lane only, not the general wrapper. |

## Runtime and test map

| Surface | Worktree source | Current main status | Decision | Notes |
|---|---|---|---|---|
| schema validator | `harness/validate_schema.py` | missing | adopt pattern | Main wrapper should have schema self-validation. |
| example validator | `harness/validate_examples.py` | missing | adopt pattern | Main wrapper needs example-vs-schema validation. |
| evaluator | `harness/evaluate.py` | missing | later translate | Useful after schemas and examples exist on `main`. |
| iteration loop | `harness/iterate.py` | older unrelated loop exists in harness bootstrap | translate carefully | Do not overwrite current production-facing harness loop blindly. |
| document contract tests | `tests/test_document_contract.py` | missing | adopt | High-value immediate port target. |
| failure tests | `tests/test_failure_examples_fail.py` | missing | adopt | Required for exact-failure discipline. |
| lattice mapping tests | `tests/test_lattice_mapping.py` | missing | adopt | Supports the wrapper translation layer directly. |

## InfraNodus map

| Surface | Current main path | State on main | Decision | Notes |
|---|---|---|---|---|
| workspace README | `analysis/infranodus/README.md` | present | adopt | Already defines named graphs, gap-analysis script, and auth model. |
| capability registry | `analysis/capabilities/infranodus-capability-registry.yaml` | present | adopt | Already enumerates active, deferred, and blocked tool rows. |
| corpus discipline rule | `.claude/rules/infranodus-corpus.md` | present | adopt | Already defines input checklist and preferred tool map. |
| gap-analysis artifact | `analysis/infranodus/goal-vs-implementation.diff.json` | present | adopt | Existing durable comparison artifact pattern. |
| wrapper-spec hook | missing from wrapper spec set | missing | create and wire | This is the main missing integration point. |

## Pixeltable map

| Surface | Current main path | State on main | Decision | Notes |
|---|---|---|---|---|
| architecture foundation | `meta/ARCHITECTURE.md` | present | adopt | Already states Pixeltable is the data layer and embedded substrate. |
| Python project boundary | `pixeltable/pyproject.toml` and `pixeltable/service/**` | present | adopt | The runtime boundary exists even though current editable build tooling is noisy. |
| execution namespaces | `lattice/execution/*` described in docs and migrations | present | adopt | Evidence, runs, threads, and artifacts are already substrate concepts. |
| bridge namespaces | `lattice/bridge/*` described in docs and migrations | present | adopt | These are the durable normalized tables for cross-system integration. |
| wrapper-spec hook | missing from wrapper spec set | missing | create and wire | This is the missing contract-level integration point. |

## Current main drift summary

### Present on main

- fractal wrapper scaffold at parent, child, and harness layers
- seven-gate wrapper concept
- schema-hardening direction
- parent-child bridge concept

### Missing on main

- schema package
- source package
- valid and invalid example package
- expected-failure registry
- evaluation package
- promotion package
- translation map
- explicit prompt-schema hook in the wrapper contract docs
- explicit InfraNodus hook in the wrapper contract docs
- explicit Pixeltable hook in the wrapper contract docs
- document contract tests
- explicit wrapper-level success criteria derived from evidence
- reconciliation of `meta/harness/GOAL.md`, `MEMORY.md`, and `golden_path.md`
  with the newer FRE contract lineage

## Immediate adoption order

1. adopt the source and provenance discipline from the FRE worktree
2. adopt the document-contract discipline from the FRE worktree
3. adopt the expected-failure discipline
4. adopt the evaluation and promotion separation
5. adopt the translation-map discipline
6. make the prompt-schema hook explicit in the wrapper contract docs
7. make the InfraNodus comparison hook explicit in the wrapper contract docs
8. make the Pixeltable substrate hook explicit in the wrapper contract docs
9. create the first reusable schema family package on `main`
10. only then reconcile `meta/harness/GOAL.md`, `MEMORY.md`, and
   `golden_path.md`
11. only then define the next downstream gate implementation

## Recommended first concrete port

The first concrete port from the worktree into `main` should be:

1. source inventory stub
2. front matter schema
3. bottom matter schema
4. gate progress schema
5. expected-failures file
6. document-contract test
7. evaluation and promotion artifact inventory
8. explicit InfraNodus comparison inventory and wrapper hook

That is the smallest honest slice that moves `main` from wrapper philosophy
toward verifiable wrapper contract.

---bottom-matter---
status_summary:
  completeness: 0.9
  confidence: high
  doc_state: draft
gate_progress:
  harvest:
    status: green
    notes: Notion pages, sibling worktree, and current main surfaces are compared directly.
  registry:
    status: green
    notes: The major contract families and runtime surfaces are named and categorized.
  manifest:
    status: green
    notes: Adopt, translate, mirror, and historical decisions are explicitly assigned for major surfaces.
  verification:
    status: amber
    notes: The mapping is explicit, but no schema or test port has landed on main yet.
  state:
    status: amber
    notes: Main is now accurately labeled as scaffold-plus-concept, not contract-complete.
  health:
    status: green
    notes: The real source of drift is now visible as worktree versus main divergence.
  promotion:
    status: amber
    notes: The next safe move is identified, but not yet implemented.
open_questions:
  - Should the restored reusable contract live under `meta/harness/fre/` on main or under a new wrapper-specific namespace?
  - Which evaluation-only fixtures should remain historical instead of being promoted into the reusable wrapper package?
pending_validations:
  - Port the first schema family package
  - Port document-contract tests
  - Reconcile live `meta/harness/GOAL.md`, `MEMORY.md`, and `golden_path.md`
promotion_criteria:
  - First schema family lands on main
  - Expected-failure discipline lands on main
  - Translation-map discipline lands on main
blocked_by: []
next_iteration:
  owner: meta-wrapper-agent
  objective: Port the first reusable schema family, its document-contract tests, and the explicit InfraNodus comparison hook from the worktree lineage into main.
