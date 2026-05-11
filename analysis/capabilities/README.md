<!-- spec-verified: code.claude.com/docs 2026-05-11 -->
# Capability Registries

One YAML per external tool. Schema enforced by `.claude/rules/capability-harvest-protocol.md`. Audited by `scripts/audit-dead-dna.sh` (Phase 7 → CI Job 12).

## Files

| Registry | Tool | Source |
|---|---|---|
| `infranodus-capability-registry.yaml` | InfraNodus MCP server + skills bundle | github.com/infranodus/mcp-server-infranodus + github.com/infranodus/skills |
| `graphify-parisgroup-capability-registry.yaml` | Graphify (Rust CLI + MCP + slash + skills + agents) | github.com/parisgroup-ai/graphify |
| `gitnexus-capability-registry.yaml` | GitNexus (MCP + group tools + skills + hooks) | github.com/abhigyanpatwari/GitNexus |
| `graphify-safishamsi-capability-registry.yaml` | Graphifyy (Python multi-format + YouTube ingestion) | github.com/safishamsi/graphify |

## Schema reference

```yaml
tool: string
tool_version: string
canonical_docs: url
last_harvested: date
harvested_by: string
capabilities:
  - id: slug
    surface: mcp_tool | cli_command | slash_command | skill | subagent | hook | prompt
    name: string
    state: ACTIVE | DEFERRED | BLOCKED
    description: one-line
    # if ACTIVE:
    wired_at: [file:line refs]
    invoked_by: [script/skill/agent names]
    # if DEFERRED:
    reason: enum (see zero-dead-dna.md allowed reasons)
    target_phase: string
    tracking_issue: int (GH issue #)
    # if BLOCKED:
    blocker: string
    blocker_resolution_path: string
```

## Operating rules

- Every row's `state` MUST be one of three; no UNKNOWN
- `DEFERRED` rows MUST have `reason` from the curated list in `.claude/rules/zero-dead-dna.md`
- `BLOCKED` rows MUST have non-empty `blocker_resolution_path`
- On tool upgrade, `tool_version` bumps and `last_harvested` updates same commit
