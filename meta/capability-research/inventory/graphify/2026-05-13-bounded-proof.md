# Graphify Bounded Proof — 2026-05-13

## Scope

Bounded code-graph proof for the current LATTICE repo. This is not a repo-wide
promotion artifact and not a docs-only graph.

Inputs were constrained by:

- `graphify.toml`
- `.graphifyignore`
- repo-local excludes from `meta/capability-research/inventory/corpus-manifest.yaml`

## Commands

```bash
graphify --help
graphify update .
graphify query "harness route" --graph graphify-out/graph.json
```

## Verified outcomes

- The installed CLI does **not** expose `graphify run`, `graphify mcp`, or
  `graphify list-tools`.
- The installed CLI **does** expose `update`, `query`, `explain`, `path`,
  `watch`, `benchmark`, and platform-specific install commands.
- `graphify update .` completed successfully and wrote output to
  `graphify-out/`.
- Output summary from the generated report:
  - 325 files
  - 1647 nodes
  - 2772 edges
  - 209 communities
- `graphify query "harness route"` returned nodes from
  `pixeltable/service/routes/harness.py` and related harness functions, proving
  the graph is navigable.

## Important corrections

- The current installed Graphify build is **hook/instruction based**, not MCP
  based.
- Repo assumptions that require a Graphify MCP entry in `.mcp.json` are stale.
- `GOAL.md` command examples using `graphify run` are stale for the current
  binary.

## Artifacts

- `graphify-out/graph.json`
- `graphify-out/GRAPH_REPORT.md`
- `graphify-out/graph.html`
