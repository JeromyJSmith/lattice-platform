# Capability Matrix - graphify

| Capability ID | Harness | Value | Risk | Decision | Evidence | Registry state | Verification target | Tracking |
|---|---|---|---|---|---|---|---|---|
| `cli-update` | `capability-research` | `high` | `low` | `promote` | `meta/capability-research/inventory/graphify/2026-05-13-bounded-proof.md` | `ACTIVE` | rerun `graphify update .` on bounded corpus | `meta/capability-research/tools/READINESS.md` |
| `cli-query` | `capability-research` | `high` | `medium` | `promote` | `meta/capability-research/inventory/graphify/2026-05-13-bounded-proof.md` | `ACTIVE` | bounded query against known harness route | `meta/capability-research/tools/READINESS.md` |
| `cli-codex-install` | `agent-guidance` | `medium` | `low` | `promote` | `AGENTS.md` graphify section | `ACTIVE` | AGENTS guidance remains present and accurate | `AGENTS.md` |
| `cli-extract` | `capability-research` | `high` | `medium` | `defer` | live help only | `DEFERRED` | semantic pass with explicit API-key-backed proof | future docs-first semantic pass |
| `cli-hook-install` | `automation` | `medium` | `medium` | `defer` | live help only | `DEFERRED` | bounded hook install and teardown proof | future graph refresh automation |
| `cli-tree` | `operator-surface` | `medium` | `low` | `defer` | live help only | `DEFERRED` | deterministic HTML artifact check | future graph views |
| `cli-export-callflow-html` | `operator-surface` | `medium` | `low` | `defer` | live help only | `DEFERRED` | deterministic HTML artifact check | future graph views |

## First Active Slice

```text
Refresh the bounded graph with `graphify update .`, query the graph for one
known harness route, and keep the Codex AGENTS guidance aligned with that real
surface.
```
