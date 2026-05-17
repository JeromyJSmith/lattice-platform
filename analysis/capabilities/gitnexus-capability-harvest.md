# Capability Harvest - gitnexus

| Field | Value |
|---|---|
| Source repo | `https://github.com/abhigyanpatwari/GitNexus` |
| Reviewed version | `1.6.3` |
| Harvest date | `2026-05-14` |
| LATTICE owner | Capability research |

## Live Wiring Seen In This Repo

| Path | Role |
|---|---|
| `.mcp.json` | Repo-local GitNexus MCP entry using `node_modules/.bin/gitnexus mcp` |
| `AGENTS.md` | Repo guidance currently expects `analyze`, `query`, `context`, `impact`, and `detect_changes` |
| `CLAUDE.md` | Same GitNexus guidance block mirrored for Claude |
| `meta/capability-research/inventory/gitnexus/2026-05-13-bounded-proof.md` | Current bounded-proof evidence for `analyze`, `status`, `list`, and `cypher` |

## Harvested CLI Surface

### Top-level commands

| Capability | Verified from live help | Current repo stance |
|---|---|---|
| `gitnexus setup` | yes | deferred |
| `gitnexus analyze` | yes | active |
| `gitnexus index` | yes | deferred |
| `gitnexus serve` | yes | deferred |
| `gitnexus mcp` | yes | active |
| `gitnexus list` | yes | active |
| `gitnexus status` | yes | active |
| `gitnexus clean` | yes | deferred |
| `gitnexus remove` | yes | deferred |
| `gitnexus wiki` | yes | deferred |
| `gitnexus augment` | yes | blocked |
| `gitnexus query` | yes | blocked |
| `gitnexus context` | yes | blocked |
| `gitnexus impact` | yes | blocked |
| `gitnexus cypher` | yes | active |
| `gitnexus detect-changes` | yes | blocked |
| `gitnexus eval-server` | yes | deferred |

### Group subcommands

| Capability | Verified from live help | Current repo stance |
|---|---|---|
| `gitnexus group create` | yes | deferred |
| `gitnexus group add` | yes | deferred |
| `gitnexus group remove` | yes | deferred |
| `gitnexus group list` | yes | deferred |
| `gitnexus group status` | yes | deferred |
| `gitnexus group sync` | yes | deferred |
| `gitnexus group impact` | yes | blocked |
| `gitnexus group query` | yes | blocked |
| `gitnexus group contracts` | yes | deferred |

## Important Corrections From Live Harvest

- `gitnexus status` currently reports the `lattice-platform-scoped` index as stale at commit `37e9185` while repo `HEAD` is `8bcc380`.
- Current scoped `query`, `context`, `impact`, and `detect-changes` attempts exit with code `-1` in this environment.
- Repo guidance in `AGENTS.md` and `CLAUDE.md` still assumes those broken scoped calls are ready for mandatory use.
- The current trustworthy active surface is narrower than the old registry claimed: `analyze`, `mcp`, `list`, `status`, and `cypher`.
