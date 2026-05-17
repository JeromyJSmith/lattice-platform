# Capability Harvest - infranodus

| Field | Value |
|---|---|
| Source repo | `https://github.com/infranodus/mcp-server-infranodus` |
| Reviewed surface | session-exposed MCP tool catalog plus repo-local proof docs |
| Harvest date | `2026-05-14` |
| LATTICE owner | Capability research |

## Live Wiring Seen In This Repo

| Path | Role |
|---|---|
| `.mcp.json` | Repo-local InfraNodus MCP entry using `npx -y infranodus-mcp-server` |
| `meta/capability-research/tools/infranodus-gap-analysis-2026-05-13.md` | First controlled gap-analysis artifact using local InfraNodus MCP |
| `meta/capability-research/tools/infranodus-skills-master-audit.md` | Audit of vendored InfraNodus-adjacent skill material |
| `meta/capability-research/tools/READINESS.md` | Readiness contract for InfraNodus first-pass use |

## Harvested MCP Surface

| Capability | Present in live tool catalog | Current repo stance |
|---|---|---|
| `search` | yes | deferred |
| `fetch` | yes | deferred |
| `list_graphs` | yes | deferred |
| `get_more_tools` | yes | deferred |
| `retrieve_from_knowledge_base` | yes | deferred |
| `analyze_text` | yes | deferred |
| `generate_content_gaps` | yes | active |
| `generate_topical_clusters` | yes | deferred |
| `develop_text_tool` | yes | deferred |
| `optimize_text_structure` | yes | active |
| `develop_latent_topics` | yes | deferred |
| `develop_conceptual_bridges` | yes | deferred |
| `difference_between_texts` | yes | active |
| `overlap_between_texts` | yes | deferred |
| `merged_graph_from_texts` | yes | deferred |
| `generate_contextual_hint` | yes | deferred |
| `analyze_google_search_results` | yes | blocked |
| `analyze_related_search_queries` | yes | blocked |
| `search_queries_vs_search_results` | yes | blocked |
| `generate_seo_report` | yes | blocked |
| `memory_add_relations` | yes | deferred |
| `memory_get_relations` | yes | deferred |
| `generate_research_questions` | yes | deferred |
| `generate_research_ideas` | yes | deferred |
| `generate_knowledge_graph` | yes | deferred |
| `generate_responses_from_graph` | yes | deferred |

## Important Corrections From Live Harvest

- The current session-exposed InfraNodus tool surface is broader than the old registry captured.
- The old registry missed utility tools such as `search`, `fetch`, `list_graphs`, and `get_more_tools`.
- The old registry also missed active analysis tools such as `generate_knowledge_graph`, `generate_responses_from_graph`, `analyze_related_search_queries`, and `search_queries_vs_search_results`.
- The only currently evidenced active slice in committed repo artifacts is the curated-doc gap-analysis flow using `optimize_text_structure`, `generate_content_gaps`, and `difference_between_texts`.
