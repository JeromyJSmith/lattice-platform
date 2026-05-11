---
paths:
  - "analysis/infranodus/**"
  - "analysis/gaps/**"
  - "analysis/desires/**"
---
<!-- spec-verified: code.claude.com/docs 2026-05-11 -->
<!-- Path-scoped rule: only loads when Claude works with the paths above. -->

# InfraNodus Corpus Discipline

Rules that apply when working with any file under `analysis/infranodus/`, `analysis/gaps/`, or `analysis/desires/`. Originally specified in Amendment 05; the full MCP tool catalog + preferred tool map added in Amendment 06.

## 6-point input checklist (catches 90% of graph failures)

1. **Define purpose** — each corpus serves ONE graph purpose. Never mix desires + goals + failures in one graph.
2. **Validate source quality** — minimum 30 statements per corpus; no raw log dumps.
3. **Normalize language** — strip implementation jargon; normalize entity names; one statement per line.
4. **Shape the corpus** — 150-500 word documents per entry; group related entries; remove duplicates.
5. **Preflight pass** — check for `modularity < 0.3` (undifferentiated blob) or `betweenness > 0.8` (single bottleneck node).
6. **InfraNodus-ready packaging** — UTF-8, no binary content, no embedded code blocks.

## Full MCP tool catalog (Amendment 06 addition)

Authoritative list of 20 InfraNodus MCP tools shipped via `infranodus-mcp-server`. Per the Capability Harvest Protocol, each tool's current state lives in `analysis/capabilities/infranodus-capability-registry.yaml`. Use this catalog as the quick-reference lookup; consult the registry for live state.

| Tool name | Primary use | State (at Amendment 06) |
|---|---|---|
| `analyze_text` | Raw text → graph | ACTIVE |
| `create_knowledge_graph` | Named persistent graph | ACTIVE |
| `analyze_existing_graph_by_name` | Re-read prior graph | ACTIVE |
| `generate_content_gaps` | Structural gap detection (primary proposer signal) | ACTIVE |
| `develop_latent_topics` | Underrepresented topics (`optimize=latent`) | ACTIVE |
| `develop_conceptual_bridges` | Cross-context bridging | ACTIVE |
| `generate_topical_clusters` | Cluster detection | ACTIVE |
| `generate_research_questions` | Clarifying questions from gaps | DEFERRED → Issue #19 |
| `generate_research_ideas` | Research ideas from latent topics | DEFERRED → Issue #19 |
| `develop_text_tool` | Combined develop+optimize+bridges | DEFERRED (redundant) |
| `optimize_text_structure` | Auto bias/focus/dispersion fix | DEFERRED → Phase 5 |
| `difference_between_texts` | Goal-vs-implementation diff | ACTIVE |
| `overlap_between_texts` | Cross-corpus overlap | DEFERRED |
| `merged_graph_from_texts` | Combined multi-corpus graph | DEFERRED → Global Meta-Harness rollup |
| `generate_contextual_hint` | Lightweight summary for briefs | ACTIVE |
| `retrieve_from_knowledge_base` | GraphRAG retrieval | ACTIVE (used by Amendment 07 substrate) |
| `generate_seo_report` | SEO report | BLOCKED (no SEO surface) |
| `analyze_google_search_results` | SERP analysis | BLOCKED (no SEO surface) |
| `memory_add_relations` | Persist relations to InfraNodus memory | DEFERRED |
| `memory_get_relations` | Retrieve persisted relations | DEFERRED |

## Preferred tool map (decision shortcuts)

When you have a specific task and don't want to think about which tool to reach for:

| If you want… | Use… | Mode |
|---|---|---|
| Build a graph from raw corpus for the first time | `analyze_text` | — |
| Re-analyze a corpus you've already built | `analyze_existing_graph_by_name` | — |
| Find blind spots in the proposer's current view | `generate_content_gaps` | `optimize=gaps` |
| Detect when discourse is getting too narrow | `develop_latent_topics` | `optimize=latent` |
| Connect to broader context (cross-section synthesis) | `develop_conceptual_bridges` | — |
| Decide whether to split a section into multiple harnesses | `generate_topical_clusters` | — |
| Compute drift between accepted goals and live code | `difference_between_texts` | — |
| Build a proposer brief with light context | `generate_contextual_hint` | — |
| GraphRAG retrieval for substrate-backed queries | `retrieve_from_knowledge_base` | `includeGraphSummary=true` |

## Operating mode selector

| Symptom | Switch to mode |
|---|---|
| Default starting state — reducing blind spots | `optimize=gaps` |
| Coverage uneven across topics | `optimize=develop` |
| Stuck in narrow local optimum (3+ iterations no improvement) | `optimize=reinforce` |
| Harness overfocuses on single area | `optimize=latent` |

The autoresearch loop's escalation policy (defined in `meta/harness/bootstrap/run-autoresearch.sh` from Phase 4): start `gaps`, escalate to `reinforce` after 3 plateau iterations, escalate to `latent` after 5.

## Cross-references

- `.claude/rules/capability-harvest-protocol.md` — why this catalog exists and what governs it
- `.claude/rules/zero-dead-dna.md` — what we do when a tool sits unused
- `.claude/rules/dependency-allowlist.md` — install path + scope for InfraNodus MCP + skills
- `analysis/capabilities/infranodus-capability-registry.yaml` — live state of every row above
