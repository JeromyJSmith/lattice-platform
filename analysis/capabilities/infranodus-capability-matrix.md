# Capability Matrix - infranodus

| Capability ID | Harness | Value | Risk | Decision | Evidence | Registry state | Verification target | Tracking |
|---|---|---|---|---|---|---|---|---|
| `mcp-optimize-text-structure` | `capability-research` | `high` | `low` | `promote` | `meta/capability-research/tools/infranodus-gap-analysis-2026-05-13.md` | `ACTIVE` | rerun curated-doc structural diagnosis | `meta/capability-research/tools/READINESS.md` |
| `mcp-generate-content-gaps` | `capability-research` | `high` | `low` | `promote` | `meta/capability-research/tools/infranodus-gap-analysis-2026-05-13.md` | `ACTIVE` | rerun curated-doc gap extraction | `meta/capability-research/tools/READINESS.md` |
| `mcp-difference-between-texts` | `capability-research` | `high` | `medium` | `promote` | `meta/capability-research/tools/infranodus-gap-analysis-2026-05-13.md` | `ACTIVE` | compare current docs versus desired operator flow | `meta/capability-research/tools/READINESS.md` |
| `mcp-generate-knowledge-graph` | `capability-research` | `medium` | `medium` | `defer` | live tool catalog only | `DEFERRED` | bounded graph build over curated docs | future proof slice |
| `mcp-retrieve-from-knowledge-base` | `graph-memory` | `medium` | `medium` | `defer` | live tool catalog only | `DEFERRED` | bounded graph retrieval against a saved named graph | future proof slice |
| `mcp-memory-add-relations` | `graph-memory` | `medium` | `medium` | `defer` | live tool catalog only | `DEFERRED` | memory persistence policy plus verifier | post knowledge substrate |
| `mcp-generate-seo-report` | `marketing` | `low` | `low` | `block` | live tool catalog only | `BLOCKED` | none until LATTICE has an SEO lane | explicit future product change |

## First Active Slice

```text
Keep InfraNodus grounded in curated-doc gap analysis first. Do not widen it to
memory persistence, SEO tooling, or generalized graph reuse until those paths
have their own bounded proof artifacts.
```
