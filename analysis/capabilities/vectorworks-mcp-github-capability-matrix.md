# Capability Matrix - vectorworks-mcp-github

| Capability ID | Harness | Value | Risk | Decision | Evidence | Registry state | Verification target | Tracking |
|---|---|---|---|---|---|---|---|---|
| `cli-vectorworks-github-mcp-server` | `agent-runtime` | `high` | `low` | `promote` | `.mcp.json`, local `cargo build --release` output | `ACTIVE` | Binary launches through MCP config entry | `analysis/capabilities/vectorworks-mcp-github-capability-registry.yaml` |
| `mcp-vectorworks-read-write-tools` | `vw-actuation` | `high` | `medium` | `block` | Startup warning indicates bridge not connected | `BLOCKED` | Load VW plugin bridge and verify at least one tool call | `analysis/capabilities/vectorworks-mcp-github-capability-registry.yaml` |

## First Active Slice

```text
Treat this integration as installed and launchable, but not yet actuating.
All Vectorworks drawing/script tools remain blocked until the SDK plugin bridge
is loaded in a live Vectorworks session and the Unix socket is connected.
```
