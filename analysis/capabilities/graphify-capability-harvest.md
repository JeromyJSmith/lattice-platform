# Capability Harvest - graphify

| Field | Value |
|---|---|
| Source repo | `https://github.com/safishamsi/graphify` |
| Reviewed version | `graphifyy 0.7.18` |
| Harvest date | `2026-05-14` |
| LATTICE owner | Capability research |

The installed package is `graphifyy`, and it exposes the `graphify` executable.
The capability surface below was harvested from the live `graphify --help`
output and the installed `graphifyy-0.7.18.dist-info` metadata.

## Live Wiring Seen In This Repo

| Path | Role |
|---|---|
| `.mcp.json` | Repo-local Graphify wrapper entry invoking `scripts/run-graphify-mcp.sh` |
| `scripts/run-graphify-mcp.sh` | Launches `python -m graphify.serve graphify-out/graph.json` |
| `AGENTS.md` | Codex guidance to run `graphify update .` and use `graphify extract .` when keys exist |
| `meta/capability-research/inventory/graphify/2026-05-13-bounded-proof.md` | Current bounded-proof evidence for `update` and `query` |

## Harvested CLI Surface

### Core graph operations

| Capability | Verified from live help | Current repo stance |
|---|---|---|
| `graphify path` | yes | deferred |
| `graphify explain` | yes | deferred |
| `graphify add` | yes | deferred |
| `graphify watch` | yes | deferred |
| `graphify update` | yes | active |
| `graphify cluster-only` | yes | deferred |
| `graphify query` | yes | active |
| `graphify save-result` | yes | deferred |
| `graphify check-update` | yes | deferred |
| `graphify tree` | yes | deferred |
| `graphify extract` | yes | deferred |
| `graphify benchmark` | yes | deferred |
| `graphify export callflow-html` | yes | deferred |

### Repo and graph management

| Capability | Verified from live help | Current repo stance |
|---|---|---|
| `graphify clone` | yes | deferred |
| `graphify merge-driver` | yes | deferred |
| `graphify merge-graphs` | yes | deferred |
| `graphify global add` | yes | deferred |
| `graphify global remove` | yes | deferred |
| `graphify global list` | yes | deferred |
| `graphify global path` | yes | deferred |
| `graphify hook install` | yes | deferred |
| `graphify hook uninstall` | yes | deferred |
| `graphify hook status` | yes | deferred |

### Platform installers

| Capability | Verified from live help | Current repo stance |
|---|---|---|
| `graphify install` | yes | deferred |
| `graphify uninstall` | yes | deferred |
| `graphify gemini install` / `uninstall` | yes | deferred |
| `graphify cursor install` / `uninstall` | yes | deferred |
| `graphify claude install` / `uninstall` | yes | deferred |
| `graphify codex install` / `uninstall` | yes | codex install active, uninstall deferred |
| `graphify opencode install` / `uninstall` | yes | deferred |
| `graphify aider install` / `uninstall` | yes | deferred |
| `graphify copilot install` / `uninstall` | yes | deferred |
| `graphify vscode install` / `uninstall` | yes | deferred |
| `graphify claw install` / `uninstall` | yes | deferred |
| `graphify droid install` / `uninstall` | yes | deferred |
| `graphify trae install` / `uninstall` | yes | deferred |
| `graphify trae-cn install` / `uninstall` | yes | deferred |
| `graphify antigravity install` / `uninstall` | yes | deferred |
| `graphify hermes install` / `uninstall` | yes | deferred |
| `graphify kiro install` / `uninstall` | yes | deferred |
| `graphify pi install` / `uninstall` | yes | deferred |

## Important Corrections From Live Harvest

- The installed package name is `graphifyy`, not `graphify`.
- The live `graphify` executable resolves into the `uv` tool environment `graphifyy`.
- There is no installed Python distribution named `graphify`; the backing dist-info is `graphifyy-0.7.18.dist-info`.
- The current CLI does not expose `graphify run`.
- The current CLI does not expose `graphify mcp`.
- The repo-local MCP server is a local wrapper around `python -m graphify.serve`, not an upstream CLI command.
- The repo already has active guidance for `graphify update .`, so `update` should be treated as a live capability, not a speculative one.
