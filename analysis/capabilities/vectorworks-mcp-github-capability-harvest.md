# Capability Harvest - vectorworks-mcp-github

| Field | Value |
|---|---|
| Source repo | `https://github.com/mako-357/vectorworks-mcp` |
| Reviewed version | `git c4b8c48` |
| Harvest date | `2026-05-17` |
| LATTICE owner | Capability research |

## Live Wiring Seen In This Repo

| Path | Role |
|---|---|
| `.mcp.json` | Repo-local MCP entry `vectorworks-github` using launcher script |
| `scripts/run-vectorworks-github-mcp.sh` | Clones/builds upstream server into `.cache/` and launches stdio MCP binary |

## Harvest Inputs

- `README.md` tool table from upstream repo
- `mcp-server/Cargo.toml` binary metadata (`vectorworks-mcp-server`)
- Local build/test run output: server starts and reports bridge-not-connected warning when VW plugin socket is unavailable

## Harvested MCP Tool Surface

| Capability | Description | Current repo stance |
|---|---|---|
| `get_drawing_info` | Retrieve drawing metadata from active Vectorworks document | blocked |
| `list_layers` | List layers from active Vectorworks document | blocked |
| `create_line` | Draw line geometry | blocked |
| `create_rect` | Draw rectangle geometry | blocked |
| `create_circle` | Draw circle geometry | blocked |
| `run_script` | Execute VectorScript or Python script in Vectorworks | blocked |

## Build/Runtime Notes

- Rust MCP server builds successfully on this host.
- Runtime warning shows expected blocker without an active Vectorworks plugin socket:
  - `Vectorworks bridge: not connected (plugin may not be loaded)`
