<!-- spec-verified: code.claude.com/docs 2026-05-11 -->
# Capability Lifecycle

Every external tool integration moves through the same lifecycle:

1. **Capability Harvest** - raw inventory of every surface the tool exposes.
2. **Capability Matrix** - normalized decision table: use now, defer, block, or reject.
3. **Proof Run** - first successful invocation with verifier output and evidence.
4. **Capability Manifest** - machine-readable harness intent for proven capability rows.
5. **Capability Registry** - canonical per-tool YAML under this directory.
6. **Verification Tracking** - local and CI checks keep registry rows honest over time.

Harvest and matrix artifacts describe possibility space. The manifest and registry
are for capabilities that have crossed the proof-run gate, or for explicit
`DEFERRED` / `BLOCKED` rows that must remain visible. An `ACTIVE` row means the
capability has already produced a desired outcome at least once and has evidence
attached.

Schema is enforced by `.claude/rules/capability-harvest-protocol.md` and audited by `scripts/audit-dead-dna.sh`.

IndyDevDan / Disler repositories selected for LATTICE are incorporated as doctrine and harness capabilities, not treated as opaque vendor drops. Keep source URL and commit provenance in the registry.

## Files

| Registry | Tool | Source |
|---|---|---|
| `agent-sandbox-skill-capability-registry.yaml` | Disler E2B sandbox skill workflow for CLI agents | github.com/disler/agent-sandbox-skill |
| `agent-sandboxes-capability-registry.yaml` | Disler E2B sandbox CLI/MCP/parallel fork workflows | github.com/disler/agent-sandboxes |
| `agentic-drop-zones-capability-registry.yaml` | Disler file-triggered agentic workflow pattern | github.com/disler/agentic-drop-zones |
| `benchy-capability-registry.yaml` | Disler live model benchmarking pattern | github.com/disler/benchy |
| `bash-damage-from-within-capability-registry.yaml` | Disler bash safety ladder for Claude Code and Pi | github.com/disler/bash-damage-from-within |
| `claude-code-hooks-mastery-capability-registry.yaml` | Disler Claude Code hook lifecycle patterns | github.com/disler/claude-code-hooks-mastery |
| `claude-code-hooks-multi-agent-observability-capability-registry.yaml` | Disler multi-agent hook observability dashboard pattern | github.com/disler/claude-code-hooks-multi-agent-observability |
| `claude-code-is-programmable-capability-registry.yaml` | Disler programmable Claude Code examples | github.com/disler/claude-code-is-programmable |
| `fork-repository-skill-capability-registry.yaml` | Disler fork-terminal delegation skill | github.com/disler/fork-repository-skill |
| `install-and-maintain-capability-registry.yaml` | Disler executable install/maintenance docs pattern | github.com/disler/install-and-maintain |
| `pi-vs-claude-code-capability-registry.yaml` | Disler Pi extension and Pi-vs-Claude routing patterns | github.com/disler/pi-vs-claude-code |
| `single-file-agents-capability-registry.yaml` | Disler uv single-file agents pattern | github.com/disler/single-file-agents |
| `the-verifier-agent-capability-registry.yaml` | Disler Pi top-down observer verifier pattern | github.com/disler/the-verifier-agent |
| `the-library-capability-registry.yaml` | Disler private-first agentics catalog pattern | github.com/disler/the-library |
| `claude-code-capability-registry.yaml` | Claude Code docs, hooks, MCP, settings, and CLI surfaces | code.claude.com/docs |
| `deck-gl-capability-registry.yaml` | deck.gl analytical rendering layer | deck.gl/docs |
| `pixeltable-capability-registry.yaml` | Pixeltable data store and computed-column runtime | docs.pixeltable.com |
| `web-ifc-capability-registry.yaml` | web-ifc browser IFC parser surface | thatopen.github.io/engine_web-ifc |
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
    proof:
      command: string
      evidence: path
      verified_at: date
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
- Empty bootstrap registries are allowed only with `spec-verified: false`; they must be populated before the tool is declared integrated
- Registry rows should trace back to a harvest/matrix/manifest artifact when the integration is substantial enough to affect a harness
- ACTIVE rows must be backed by proof-run evidence before they enter the manifest or registry
- ACTIVE rows must eventually be covered by docs substrate chunks and harness verification; until docs ingestion is live, `audit-dead-dna.sh` enforces parseability and required state fields

## Templates

- `capability-harvest.template.md` - raw discovery table
- `capability-matrix.template.md` - decision matrix for harness use
- `capability-manifest.template.yaml` - machine-readable harness intent
