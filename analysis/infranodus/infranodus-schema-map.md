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
| harvest_gate | corpus intake and graph creation | `analyze_text`, `create_knowledge_graph` | `analysis/infranodus/infranodus-capability-harvest.md` |
| registry_gate | naming and relationship review | `analyze_existing_graph_by_name`, `generate_topical_clusters` | `analysis/capabilities/infranodus-capability-registry.yaml` |
| manifest_gate | placement and cross-surface comparison | `difference_between_texts`, `generate_topical_clusters` | `analysis/infranodus/infranodus-capability-manifest.yaml` |
| verification_gate | durable comparison evidence | `difference_between_texts`, `generate_contextual_hint` | `analysis/infranodus/goal-vs-implementation.diff.json` |
| state_gate | honest blocker and gap justification | `generate_content_gaps`, `difference_between_texts` | `analysis/infranodus/goal-vs-implementation.diff.json` |
| health_gate | drift and bridge detection | `difference_between_texts`, `develop_latent_topics`, `develop_conceptual_bridges` | `analysis/infranodus/goal-vs-implementation.diff.json` |
| promotion_gate | graph-backed promotion challenge | `generate_content_gaps`, `retrieve_from_knowledge_base` | promotion record must cite InfraNodus outputs |

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

## Immediate narrow implementation rule

When a schema family is added on main:

- do not add every InfraNodus row to that schema
- add only the rows that are required for that schema family to remain honest
- record the mapping here first

That keeps the schemas growing by logged harvest and mapping rather than by
vague intuition.

---bottom-matter---
status_summary:
  completeness: 0.95
  confidence: high
  doc_state: draft
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
    status: amber
    notes: The mapping is explicit, but future schema families and tests still need implementation.
  state:
    status: green
    notes: Comparison-driven claims are now tied to required artifact expectations.
  health:
    status: green
    notes: Drift detection and gap analysis are mapped to the health and promotion surfaces directly.
  promotion:
    status: amber
    notes: The map defines promotion evidence requirements, but downstream promotion records still need to adopt them.
open_questions:
  - Which wrapper schema family should formalize InfraNodus evidence references first?
pending_validations:
  - Port the first schema family and reflect these hook fields
  - Add tests that require comparison evidence for comparison-bearing promotion claims
promotion_criteria:
  - Schema families reference InfraNodus honestly where needed
  - Promotion records stop relying on prose-only claims when comparison is central
blocked_by: []
next_iteration:
  owner: meta-wrapper-agent
  objective: Use this map to add InfraNodus-aware fields to the first reusable wrapper schema families on main.
