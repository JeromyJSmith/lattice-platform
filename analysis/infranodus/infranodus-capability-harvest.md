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

---bottom-matter---
status_summary:
  completeness: 0.95
  confidence: high
  doc_state: draft
gate_progress:
  harvest:
    status: green
    notes: The local InfraNodus surfaces are grouped and prioritized explicitly.
  registry:
    status: green
    notes: The harvest is anchored to the existing canonical registry surface.
  manifest:
    status: amber
    notes: The next downstream manifest has defined inputs but is only created in the next artifact.
  verification:
    status: amber
    notes: This harvest is grounded in live local files but does not itself run proofs.
  state:
    status: green
    notes: Active, deferred, and blocked categories are preserved rather than flattened.
  health:
    status: green
    notes: The harvest makes the current InfraNodus surface area explicit instead of implicit.
  promotion:
    status: amber
    notes: Promotion depends on schema mapping and evaluation artifacts defined downstream.
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
