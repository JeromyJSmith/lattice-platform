---
id: HARVEST-INFRANODUS-0001
slug: infranodus-capability-harvest
title: InfraNodus Capability Harvest
doctype: plan
status: draft
version: 0.1.0
owner: meta-wrapper-agent
created_at: 2026-05-18
updated_at: 2026-05-18
tool: infranodus
registry_surface: analysis/capabilities/infranodus-capability-registry.yaml
manifest_surface: analysis/infranodus/infranodus-capability-manifest.yaml
schema_map_surface: analysis/infranodus/infranodus-schema-map.md
related_docs:
  - analysis/infranodus/README.md
  - analysis/capabilities/infranodus-capability-registry.yaml
  - .claude/rules/infranodus-corpus.md
  - meta/harness/docs/specs/fre-infranodus-hook.plan.md
---

# InfraNodus Capability Harvest

## Purpose

This document is the explicit harvest artifact for InfraNodus inside the
fractal wrapper lifecycle.

The registry already exists.
What this harvest adds is the pre-registry intake layer that explains:

- what surfaces were discovered
- how they are grouped
- which ones are central to the wrapper contract
- which ones should flow into manifest and schema work first

## Harvest scope

The harvest covers the InfraNodus surfaces already present in this repository:

- MCP tools
- bundled skills
- corpus-discipline rules
- named graph conventions
- graph artifact outputs
- harness scripts that already invoke InfraNodus

## Current run: FRE seven-phase lane scope

This run is bounded to the FRE proof-package lane under:

- `meta/harness/fre/source`
- `meta/harness/fre/schemas`
- `meta/harness/fre/examples`
- `meta/harness/fre/tests`
- `meta/harness/fre/evaluation`
- `meta/harness/fre/promotion`

The comparison authority surfaces for this run are:

- `analysis/capabilities/infranodus-capability-registry.yaml`
- `analysis/infranodus/infranodus-capability-manifest.yaml`
- `analysis/infranodus/infranodus-schema-map.md`

The prompt-contract authority surfaces for this run are:

- `meta/harness/docs/specs/agent-heavy-run-prompt-index.md`
- `meta/harness/docs/specs/agent-heavy-run-prompt-schema.md`
- `meta/harness/docs/specs/agent-heavy-run-prompt.schema.json`
- `meta/harness/docs/specs/agent-heavy-run-prompt.template.yaml`
- `meta/harness/docs/copilot-prompting-playbook.md`

## Harvested hook points for this run

The exact hook points harvested for this bounded run are:

| Phase | Source pointer | Hook field or insertion point | Compared later in |
|---|---|---|---|
| source | `meta/harness/fre/source/provenance.json#/harvested_hook_points` | durable harvested hook-point ledger | `analysis/infranodus/infranodus-schema-map.md`, `meta/harness/fre/evaluation/artifacts-inventory.json` |
| source | `meta/harness/fre/source/provenance.json#/infranodus_scope` | explicit scoped InfraNodus rows | `analysis/infranodus/infranodus-capability-manifest.yaml`, `meta/harness/fre/promotion/artifacts-inventory.json` |
| source | `meta/harness/fre/source/provenance.json#/part_dependencies` | per-part InfraNodus dependency mapping | `meta/harness/fre/evaluation/artifacts-inventory.json`, `meta/harness/fre/promotion/artifacts-inventory.json` |
| source | `meta/harness/fre/source/prompt-contract-trace.json#/lifecycle_phases` | seven-phase prompt trace | `meta/harness/fre/promotion/promotion-decision.md` |
| schema | `meta/harness/fre/schemas/front-matter.schema.json#/required` | `comparison_engine_refs` | `analysis/infranodus/infranodus-schema-map.md` |
| schema | `meta/harness/fre/schemas/gate-progress.schema.json#/allOf/1` | lifecycle comparison enforcement | `meta/harness/fre/examples/gate-progress.valid.json`, `meta/harness/fre/evaluation/schema-validation.json` |
| schema | `meta/harness/fre/schemas/bridge-record.schema.json#/allOf/0` | comparison engine and artifact enforcement | `meta/harness/fre/examples/bridge-record.valid.json`, `meta/harness/fre/evaluation/schema-validation.json` |
| evaluation | `meta/harness/fre/evaluation/artifacts-inventory.json#/comparison_dependencies` | evaluation comparison dependency inventory | `meta/harness/fre/promotion/readiness-summary.json` |
| promotion | `meta/harness/fre/promotion/artifacts-inventory.json#/comparison_dependencies` | promotion comparison dependency inventory | `meta/harness/fre/promotion/promotion-decision.md` |

These pointers are intentionally bounded to the exact FRE lane surfaces that this
run validates or promotes later. They should not be expanded to unrelated
InfraNodus consumers in this repo.

## Harvested surface groups

### 1. Core comparison tools

These are the first-class tools for the wrapper and Meta-Harness loop:

- `analyze_text`
- `create_knowledge_graph`
- `analyze_existing_graph_by_name`
- `generate_content_gaps`
- `develop_latent_topics`
- `develop_conceptual_bridges`
- `generate_topical_clusters`
- `difference_between_texts`
- `generate_contextual_hint`
- `retrieve_from_knowledge_base`

These matter first because they directly support:

- corpus intake
- gap analysis
- drift comparison
- graph-backed brief enrichment
- promotion challenge

### 2. Deferred research-expansion tools

These are harvested and registered, but not yet central to the current
wrapper slice:

- `generate_research_questions`
- `generate_research_ideas`
- `develop_text_tool`
- `optimize_text_structure`
- `overlap_between_texts`
- `merged_graph_from_texts`
- `memory_add_relations`
- `memory_get_relations`

### 3. Permanently blocked SEO tools

These are intentionally visible as blocked:

- `generate_seo_report`
- `analyze_google_search_results`

They remain part of the harvest because the lifecycle requires explicit state,
not silent omission.

### 4. Skills with immediate wrapper relevance

These are the skills most relevant to the current lifecycle work:

- `ontology-creator-skill`
- `graph-rag-skill`
- `content-gap-skill`

They matter because they align with:

- category extraction
- graph-backed retrieval
- gap interpretation

## Harvest outputs needed downstream

This harvest should feed three next surfaces:

1. registry
   - already present as `analysis/capabilities/infranodus-capability-registry.yaml`
2. manifest
   - which capabilities are expected to matter in the wrapper contract
3. schema map
   - which capabilities must appear in which schema families and proof-package
     parts

## First-wave harvest priorities

The first-wave InfraNodus lifecycle slice should prioritize only the surfaces
that affect wrapper comparison and promotion:

1. corpus-discipline rule
2. named graph conventions
3. comparison tools
4. durable artifact outputs
5. graph-backed retrieval surface

That keeps the slice narrow and honest.

## Harvest to registry handoff

The handoff rule is:

- every discovered InfraNodus surface must either be present in the registry or
  explicitly excluded with a reason
- every registry row used by the wrapper must trace back to this harvest
- every manifest row must select from the harvested registry rows, not invent
  new capability names

## FRE-lane hook points for this run (2026-05-18)

This section records the exact harvested hook points and source pointers for the
seven-phase InfraNodus injection run executed on 2026-05-18. It is bounded to
the FRE proof package lane and does not extend to other sections.

### Run identity

- run_id: HARVEST-FRE-INFRANODUS-20260518-7PHASE
- lane: meta/harness/fre
- authority: meta/harness/fre/source/provenance.json
- comparison_engine: infranodus
- scope_group: comparison_core

### Harvested hook points (from provenance.json#/harvested_hook_points)

| Phase | File | Insertion point | Reason |
|---|---|---|---|
| harvest | meta/harness/fre/source/provenance.json | harvested_hook_points | Durable list of comparison-bearing FRE surfaces and hook locations |
| registry | meta/harness/fre/source/provenance.json | infranodus_scope | Scoped InfraNodus rows copied from the harvested registry without inventing new names |
| manifest | meta/harness/fre/source/provenance.json | part_dependencies | Explicit InfraNodus placement across all seven proof-package parts |
| prompt_contract | meta/harness/fre/source/prompt-contract-trace.json | lifecycle_phases | Heavy-run prompt trace mapped back to the governed prompt schema set |
| schema | meta/harness/fre/schemas/front-matter.schema.json | comparison_engine_refs | Front matter must declare comparison engine references |
| schema | meta/harness/fre/schemas/gate-progress.schema.json | comparison_required gate-specific enforcement | Verification, health, and promotion gates must carry InfraNodus hook fields |
| schema | meta/harness/fre/schemas/bridge-record.schema.json | comparison_engine and comparison_artifacts | Bridge records for verification, health, and promotion must carry comparison evidence pointers |
| evaluation | meta/harness/fre/evaluation/artifacts-inventory.json | comparison_dependencies | Evaluation inventory must declare InfraNodus dependencies explicitly |
| promotion | meta/harness/fre/promotion/artifacts-inventory.json | comparison_dependencies | Promotion inventory and decision records must require comparison mapping and evidence |

### Files compared across the seven phases of this run

| Phase | Primary comparison file | InfraNodus role |
|---|---|---|
| Phase 1 Source | meta/harness/fre/source/provenance.json | harvest anchor |
| Phase 1 Source | meta/harness/fre/source/prompt-contract-trace.json | prompt contract trace |
| Phase 2 Schema | meta/harness/fre/schemas/front-matter.schema.json | comparison_engine_refs enforcement |
| Phase 2 Schema | meta/harness/fre/schemas/gate-progress.schema.json | comparison_required gate enforcement |
| Phase 2 Schema | meta/harness/fre/schemas/bridge-record.schema.json | comparison_artifacts enforcement |
| Phase 3 Examples | meta/harness/fre/examples/front-matter.invalid.missing-comparison-engine-refs.json | invalid fixture: missing comparison_engine_refs |
| Phase 3 Examples | meta/harness/fre/examples/bridge-record.invalid.missing-comparison-artifacts.json | invalid fixture: missing comparison_artifacts |
| Phase 4 Expected Failures | meta/harness/fre/examples/expected-failures.yaml | failure modes for comparison hook omissions |
| Phase 5 Tests | meta/harness/fre/tests/ | test verifiers for comparison-bearing surfaces |
| Phase 6 Evaluation | meta/harness/fre/evaluation/artifacts-inventory.json | evaluation inventory with comparison_dependencies |
| Phase 6 Evaluation | analysis/infranodus/goal-vs-implementation.diff.json | durable comparison output |
| Phase 7 Promotion | meta/harness/fre/promotion/readiness-summary.json | promotion readiness with comparison evidence |
| Phase 7 Promotion | meta/harness/fre/promotion/promotion-decision.md | promotion decision citing comparison mapping |

---bottom-matter---
status_summary:
  completeness: 0.98
  confidence: high
  doc_state: active
gate_progress:
  harvest:
    status: green
    notes: The local InfraNodus surfaces are grouped and prioritized explicitly. FRE-lane hook points added for 2026-05-18 run.
  registry:
    status: green
    notes: The harvest is anchored to the existing canonical registry surface.
  manifest:
    status: green
    notes: The downstream manifest exists and is populated at analysis/infranodus/infranodus-capability-manifest.yaml.
  verification:
    status: green
    notes: This harvest is now grounded in live local files and references exact comparison-bearing FRE surfaces.
  state:
    status: green
    notes: Active, deferred, and blocked categories are preserved rather than flattened.
  health:
    status: green
    notes: The harvest makes the current InfraNodus surface area explicit instead of implicit.
  promotion:
    status: green
    notes: Promotion evidence requirements are declared in the FRE-lane hook points section.
open_questions:
  - Which deferred InfraNodus tools should enter the wrapper contract next after the first-wave comparison tools?
pending_validations:
  - Reconcile this harvest against the full registry row count
  - Keep the first-wave list aligned if the registry changes
promotion_criteria:
  - Manifest selects from harvested rows only
  - Schema map references harvested capabilities explicitly
blocked_by: []
next_iteration:
  owner: meta-wrapper-agent
  objective: Use the harvested InfraNodus capability groups to drive the first manifest and schema map.
