# Capability Matrix - gitnexus

| Capability ID | Harness | Value | Risk | Decision | Evidence | Registry state | Verification target | Tracking |
|---|---|---|---|---|---|---|---|---|
| `cli-analyze` | `capability-research` | `high` | `medium` | `promote` | `meta/capability-research/inventory/gitnexus/2026-05-13-bounded-proof.md` | `ACTIVE` | bounded analyze on known include set | `meta/capability-research/tools/READINESS.md` |
| `cli-mcp` | `agent-runtime` | `high` | `medium` | `promote` | `.mcp.json` | `ACTIVE` | MCP entry resolves repo-local binary | `.mcp.json` |
| `cli-status` | `capability-research` | `high` | `low` | `promote` | bounded proof plus current stale-index result | `ACTIVE` | status reports scoped freshness or drift honestly | `AGENTS.md` |
| `cli-cypher` | `capability-research` | `medium` | `medium` | `promote` | `meta/capability-research/inventory/gitnexus/2026-05-13-bounded-proof.md` | `ACTIVE` | bounded cypher query on a known file node | bounded proof refresh |
| `cli-query` | `capability-research` | `high` | `high` | `block` | current scoped call exits `-1` | `BLOCKED` | refresh index and validate one query | bounded proof refresh |
| `cli-context` | `pre-edit-analysis` | `high` | `high` | `block` | current scoped call exits `-1` | `BLOCKED` | refresh index and validate one symbol context | bounded proof refresh |
| `cli-impact` | `pre-edit-analysis` | `high` | `high` | `block` | current scoped call exits `-1` | `BLOCKED` | refresh index and validate one symbol impact run | bounded proof refresh |
| `cli-detect-changes` | `pre-commit` | `high` | `high` | `block` | current scoped call exits `-1` | `BLOCKED` | validate against a small unstaged diff | bounded proof refresh |

## First Active Slice

```text
Trust GitNexus today for indexing, repo registration visibility, status, and raw
Cypher checks. Do not trust scoped query, context, impact, or detect-changes
until the stale index and code -1 failures are repaired with a new bounded proof.
```
