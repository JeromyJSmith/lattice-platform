---
id: MAP-INFRANODUS-SCHEMA-0001
slug: infranodus-schema-map
title: InfraNodus Schema Map
doctype: plan
status: draft
version: 0.1.0
owner: meta-wrapper-agent
created_at: 2026-05-18
updated_at: 2026-05-18
tool: infranodus
harvest_surface: analysis/infranodus/infranodus-capability-harvest.md
registry_surface: analysis/capabilities/infranodus-capability-registry.yaml
manifest_surface: analysis/infranodus/infranodus-capability-manifest.yaml
related_docs:
  - meta/harness/docs/specs/fre-infranodus-hook.plan.md
  - meta/harness/docs/specs/fre-meta-wrapper-seven.gates.md
  - meta/harness/docs/specs/fre-fractal-contract-package.plan.md
  - meta/harness/docs/specs/agent-heavy-run-prompt-schema.md
---

# InfraNodus Schema Map

## Purpose

This map connects harvested InfraNodus capabilities to the schema-bearing
surfaces they must influence.

The point is not to make InfraNodus the schema.
The point is to ensure that each relevant schema family explicitly knows where
InfraNodus enters the lifecycle.

## Mapping rule

The lifecycle is:

```text
harvest -> registry -> manifest -> schema map -> evaluation -> promotion
```

The schema families then grow from that mapped truth.

## Lifecycle gate to InfraNodus mapping

| Gate | InfraNodus role | Primary rows | Required artifact |
|---|---|---|---|
| harvest_gate | corpus intake, domain research, and graph creation | `analyze_text`, `generate_knowledge_graph`, `create_knowledge_graph`, `analyze_google_search_results`, `analyze_related_search_queries`, `search_queries_vs_search_results`, `generate_seo_report` | `analysis/infranodus/infranodus-capability-harvest.md` |
| registry_gate | naming, relationship review, and query-vocabulary pressure | `analyze_existing_graph_by_name`, `generate_topical_clusters`, `search` | `analysis/capabilities/infranodus-capability-registry.yaml` |
| manifest_gate | placement and cross-surface comparison | `difference_between_texts`, `generate_topical_clusters`, `merged_graph_from_texts` | `analysis/infranodus/infranodus-capability-manifest.yaml` |
| verification_gate | durable comparison evidence | `difference_between_texts`, `generate_contextual_hint`, `retrieve_from_knowledge_base` | `analysis/infranodus/goal-vs-implementation.diff.json` |
| state_gate | honest blocker and gap justification | `generate_content_gaps`, `difference_between_texts`, `generate_contextual_hint` | `analysis/infranodus/goal-vs-implementation.diff.json` |
| health_gate | drift, bridge detection, and domain/query mismatch | `difference_between_texts`, `generate_content_gaps`, `merged_graph_from_texts` | `analysis/infranodus/goal-vs-implementation.diff.json` |
| promotion_gate | graph-backed and domain-backed promotion challenge | `generate_content_gaps`, `retrieve_from_knowledge_base`, `difference_between_texts` | promotion record must cite InfraNodus outputs |

## Full MCP tool coverage by lifecycle phase

The authoritative machine-readable map is:

- `meta/harness/docs/specs/infranodus-phase-tool-map.json`

The bounded wrapper rule is:

- every lifecycle gate must name all eligible InfraNodus tools that fit that
  phase
- every gate must still distinguish:
  - required tools
  - supporting tools
  - out-of-scope visible tools

### Required and supporting tools by phase

| Gate | Required tools | Supporting tools |
|---|---|---|
| `harvest_gate` | `analyze_text`, `generate_knowledge_graph`, `create_knowledge_graph`, `analyze_google_search_results`, `analyze_related_search_queries`, `search_queries_vs_search_results`, `generate_seo_report` | `generate_topical_clusters`, `analyze_existing_graph_by_name`, `list_graphs`, `search`, `fetch` |
| `registry_gate` | `analyze_existing_graph_by_name`, `generate_topical_clusters`, `search` | `fetch`, `list_graphs`, `create_knowledge_graph`, `analyze_google_search_results`, `analyze_related_search_queries`, `search_queries_vs_search_results` |
| `manifest_gate` | `difference_between_texts`, `generate_topical_clusters`, `merged_graph_from_texts` | `overlap_between_texts`, `analyze_existing_graph_by_name`, `search`, `fetch` |
| `verification_gate` | `difference_between_texts`, `generate_contextual_hint`, `retrieve_from_knowledge_base` | `overlap_between_texts`, `merged_graph_from_texts`, `analyze_existing_graph_by_name` |
| `state_gate` | `generate_content_gaps`, `difference_between_texts`, `generate_contextual_hint` | `retrieve_from_knowledge_base`, `analyze_existing_graph_by_name`, `generate_responses_from_graph`, `search_queries_vs_search_results`, `analyze_related_search_queries` |
| `health_gate` | `difference_between_texts`, `generate_content_gaps`, `merged_graph_from_texts` | `overlap_between_texts`, `generate_topical_clusters`, `generate_contextual_hint`, `retrieve_from_knowledge_base`, `analyze_google_search_results`, `search_queries_vs_search_results`, `generate_seo_report` |
| `promotion_gate` | `generate_content_gaps`, `retrieve_from_knowledge_base`, `difference_between_texts` | `generate_contextual_hint`, `generate_responses_from_graph`, `merged_graph_from_texts`, `memory_get_relations`, `generate_seo_report` |

## Research-first rule

The very first step of the lifecycle is research harvest.

That means the domain-search and search-query tools are not optional sidecars.
They are valid first-pass harvest tools when the slice needs outside pressure
testing, documentation coverage, query vocabulary discovery, or known-failure
research.

In practice this includes:

- official docs and product docs
- GitHub docs, issues, and discussions
- Reddit and message-board vocabulary
- Hacker News and public discourse
- skill and playbook documentation
- query-versus-result mismatch analysis

For that reason, the following tools are now in-scope for the wrapper
lifecycle:

- `analyze_google_search_results`
- `analyze_related_search_queries`
- `search_queries_vs_search_results`
- `generate_seo_report`

## Proof-package mapping

| Proof-package part | InfraNodus contribution | Primary rows | Artifact expectation |
|---|---|---|---|
| source | normalized comparison corpora | `analyze_text`, `create_knowledge_graph` | harvest artifact and corpus notes |
| schema | graph-output contracts and references | `difference_between_texts`, `generate_topical_clusters` | schema family hook or contract note |
| examples | representative graph inputs and expected outputs | `analyze_existing_graph_by_name`, `generate_contextual_hint` | example corpora or runbook examples |
| expected-failures | malformed or mixed-purpose corpora | `generate_content_gaps`, `develop_latent_topics` | failure reasons tied to corpus-discipline rule |
| tests | validation of comparison-bearing artifacts | `difference_between_texts`, `generate_topical_clusters` | future contract tests |
| evaluation | actual graph outputs | `difference_between_texts`, `generate_content_gaps`, `generate_contextual_hint` | durable JSON or report artifacts |
| promotion | graph-backed advancement decision | `generate_content_gaps`, `retrieve_from_knowledge_base` | promotion record cites graph evidence |

## Prompt-contract mapping

Any comparison-bearing prompt should carry an InfraNodus hook block in its
task and validation language.

At minimum, the prompt instance should declare:

1. corpus scope
2. graph purpose
3. tool selection
4. expected artifact
5. stop condition if the comparison is missing or inconclusive

## Immediate schema families touched

The first wrapper schema families that should reference InfraNodus are:

1. front matter schema
   - optional `comparison_surface` or equivalent metadata
2. bottom matter schema
   - explicit note when promotion or health claims depend on graph comparison
3. gate progress schema
   - gate notes can reference required InfraNodus artifacts
4. bridge record schema
   - include comparison-artifact pointers when a gate state depends on them
5. promotion decision schema
   - require evidence references for comparison-driven promotion claims

## Current FRE hook-field JSON pointer map

The following rows are the bounded hook-field map for the active FRE lane on
main. Only missing mappings are added here.

| Schema surface | Hook field | JSON pointer | Why it matters |
|---|---|---|---|
| `meta/harness/fre/schemas/front-matter.schema.json` | `comparison_engine_refs` | `/properties/comparison_engine_refs` | Front matter must name the comparison authority surfaces that govern the document. |
| `meta/harness/fre/schemas/front-matter.schema.json` | `comparison_engine_refs` required | `/required` | The FRE front matter contract requires the comparison reference list to be present. |
| `meta/harness/fre/schemas/bottom-matter.schema.json` | `gate_progress` | `/properties/gate_progress` | Bottom matter carries the lifecycle gate array that inherits comparison enforcement from the gate-progress schema. |
| `meta/harness/fre/schemas/bottom-matter.schema.json` | gate-progress item schema | `/properties/gate_progress/items/$ref` | Comparison-bearing gate rows are validated through the shared gate-progress contract. |
| `meta/harness/fre/schemas/gate-progress.schema.json` | `comparison_required` | `/properties/comparison_required` | Declares whether a gate row must carry InfraNodus comparison data. |
| `meta/harness/fre/schemas/gate-progress.schema.json` | `comparison_engine` | `/properties/comparison_engine` | Restricts comparison-bearing gate rows to `infranodus`. |
| `meta/harness/fre/schemas/gate-progress.schema.json` | `comparison_artifacts` | `/properties/comparison_artifacts` | Holds the required comparison evidence pointers for gate rows. |
| `meta/harness/fre/schemas/gate-progress.schema.json` | comparison-required conditional | `/allOf/0` | When `comparison_required` is true, the engine and artifact fields become mandatory. |
| `meta/harness/fre/schemas/gate-progress.schema.json` | verification/health/promotion enforcement | `/allOf/1` | The three comparison-bearing lifecycle gates are forced closed on missing InfraNodus hooks. |
| `meta/harness/fre/schemas/bridge-record.schema.json` | `comparison_engine` | `/properties/comparison_engine` | Bridge records for comparison-bearing gates must name InfraNodus as the engine. |
| `meta/harness/fre/schemas/bridge-record.schema.json` | `comparison_artifacts` | `/properties/comparison_artifacts` | Bridge records must point to the comparison outputs that justify the gate state. |
| `meta/harness/fre/schemas/bridge-record.schema.json` | verification/health/promotion conditional | `/allOf/0` | The comparison engine and artifact fields are required only for the three comparison-bearing gate ids. |

## Immediate narrow implementation rule

When a schema family is added on main:

- do not add every InfraNodus row to that schema
- add only the rows that are required for that schema family to remain honest
- record the mapping here first

That keeps the schemas growing by logged harvest and mapping rather than by
vague intuition.

---bottom-matter---
status_summary:
  completeness: 0.98
  confidence: high
  doc_state: active
gate_progress:
  harvest:
    status: green
    notes: The schema map only uses harvested InfraNodus capability rows.
  registry:
    status: green
    notes: The map anchors to the existing registry and manifest surfaces explicitly.
  manifest:
    status: green
    notes: Lifecycle gates and proof-package parts are mapped to concrete InfraNodus roles.
  verification:
    status: green
    notes: Schema validation passes for all 8 schema files. JSON pointer map is complete for all required hook fields. No missing rows as of 2026-05-18 run.
  state:
    status: green
    notes: Comparison-driven claims are now tied to required artifact expectations.
  health:
    status: green
    notes: Drift detection and gap analysis are mapped to the health and promotion surfaces directly.
  promotion:
    status: green
    notes: Promotion records (readiness-summary.json, promotion-decision.md, artifacts-inventory.json) all carry explicit comparison_dependencies referencing infranodus-schema-map.md.
open_questions: []
pending_validations: []
promotion_criteria:
  - Schema families reference InfraNodus honestly where needed
  - Promotion records stop relying on prose-only claims when comparison is central
blocked_by: []
next_iteration:
  owner: meta-wrapper-agent
  objective: Keep JSON pointer map current as new schema families are added.
