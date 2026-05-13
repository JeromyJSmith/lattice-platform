<!-- spec-verified: code.claude.com/docs 2026-05-11 -->
# Capability Harvest Protocol

**Standard #1 of 3 introduced by Phase 0.6** (see `meta/harness/PLAN/06-CAPABILITY-HARVEST-AMENDMENT.md`).

## The rule

Before any external tool (MCP server, CLI binary, language-level library that exposes hooks/skills/agents) is declared "integrated", it must move through the capability lifecycle:

1. **Harvest** — raw discovery table of every surface the tool ships.
2. **Matrix** — harness decision table: use, defer, block, or reject.
3. **Manifest** — machine-readable statement of which harness uses which capability and how it is verified.
4. **Registry** — canonical YAML under `analysis/capabilities/<tool>-capability-registry.yaml`.
5. **Verification** — local/CI checks and harness evidence.

The registry must enumerate every capability surface the tool ships:

- MCP tools (one row per tool name)
- CLI commands / subcommands (one row each)
- Slash commands (one row each)
- Bundled skills (one row each)
- Bundled subagents (one row each)
- Hook integration points (one row each)
- Prompts shipped (one row each)

For every registered row, the registry assigns one of three states:

| State | Meaning | Required fields |
|---|---|---|
| `ACTIVE` | wired into LATTICE; invoked from at least one place | `wired_at:` (file:line refs), `invoked_by:` (script/skill/agent name) |
| `DEFERRED` | not wired yet; deliberate; will be wired later | `reason:`, `target_phase:`, `tracking_issue:` (GH #) |
| `BLOCKED` | external blocker prevents wiring | `blocker:`, `blocker_resolution_path:` |

**No registered row may be marked UNKNOWN or have a missing required field.** CI gate (`scripts/audit-dead-dna.sh`) enforces registry parseability and required state fields. Harness and docs-substrate gates enforce coverage once those pipelines are live.

## When the protocol fires

- Tool first installed → harvest and bootstrap registry committed in same commit as the install line
- Tool declared integrated → harvest, matrix, manifest, and registry all exist
- Tool upgraded with new capabilities → harvest/matrix/manifest/registry updated in same commit as the version bump
- Capability moved from DEFERRED → ACTIVE → registry row updated in same commit as the wiring code and verification evidence

## What the registry is NOT

- Not a marketing brochure. State terse capability descriptions; one line per row.
- Not a substitute for the tool's own docs. Link to the canonical doc in a `doc_url:` field rather than repeating prose.
- Not version-locked. Drop a `tool_version:` field at the top of each registry; bump on upgrades.
- Not the full decision trail. Harvests, matrices, and manifests explain the decision; the registry records the current committed state.

## Pre-flight before writing a registry

1. Read the tool's official docs (locally cached if available — see `/Users/ojeromyo/.claude-code-docs/` and `/Users/ojeromyo/.vectorworks-docs/` for what we have)
2. Inventory by running the tool's `--help` / list-tools command and capturing complete output
3. Cross-reference the tool's repo to find bundled skills/agents/hooks/prompts (often in `.claude/` or `skills/` subdirs)
4. For MCP servers, run `ListMcpResourcesTool` and inspect the `tools[]` array

## Required header for every registry

```yaml
# spec-verified: code.claude.com/docs 2026-05-11
tool: <name>
tool_version: <semver or git-sha>
canonical_docs: <url>
last_harvested: <YYYY-MM-DD>
harvested_by: <agent name | human handle>
capabilities:
  - id: <slug>
    surface: mcp_tool | cli_command | slash_command | skill | subagent | hook | prompt
    name: <verbatim from tool>
    state: ACTIVE | DEFERRED | BLOCKED
    description: <one line>
    # state-specific fields below
```

## Bootstrap exception

An empty registry is allowed only as an explicit bootstrap stub:

```yaml
spec-verified: false
tool: <name>
tool_version: null
canonical_docs: <url>
last_harvested: null
harvested_by: null
capabilities: []
```

Bootstrap stubs mean "known dependency, not harvested yet." They do not mean the tool is integrated.
