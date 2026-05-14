# Graph Tool Wiring Status — 2026-05-13

## What became real in this session

### Graphify

- Local binary verified at `/Users/ojeromyo/.local/bin/graphify`
- Bounded graph build completed with output in `graphify-out/`
- `graphify codex install` had already wired:
  - `AGENTS.md` Graphify section
  - `.codex/hooks.json` pre-tool Graphify context hook

### GitNexus

- Local devDependency installed: `gitnexus@1.6.3`
- Bun install needed one manual native-binary repair:
  `node node_modules/@ladybugdb/core/install.js`
- Repo indexed as `lattice-platform-scoped`
- `.mcp.json` now includes a repo-local GitNexus MCP server:

```json
"gitnexus": {
  "command": "node",
  "args": ["node_modules/.bin/gitnexus", "mcp"]
}
```

### InfraNodus

- Existing `.mcp.json` entry remained valid
- Current Codex tool exposure in this session did **not** match the broader
  runbook assumptions (`analyze_text`, `generate_content_gaps`,
  `retrieve_from_knowledge_base` were not directly exposed here)
- A named memory graph `lattice-architecture` was created successfully with the
  available relation-ingest tool

## Verified retrieval from the bounded InfraNodus graph

- `[[FastAPI_sidecar]]` returned:
  - `[[FastAPI_sidecar]] listens_at [[127.0.0.1:7770]].`
  - `[[FastAPI_sidecar]] exposes [[/healthz]].`
- `[[ifc_elements_table]]` returned:
  - `[[ifc_elements_table]] belongs_to [[ifc_namespace]] and stores [[BIS_classification]].`

## Corrections to prior assumptions

- Graphify is not an MCP server in the currently installed CLI.
- `graphify run` is not a valid command in the current installed CLI.
- GitNexus indexing works, and the repo-local binary can be repaired under Bun,
  but its FTS/query layer is not fully healthy yet in this repo-local proof.
- The previous GitNexus hook commands were invalid for `1.6.3`; the working
  pre-hook is `detect-changes --scope unstaged -r lattice-platform-scoped`.
- InfraNodus runbook examples should be treated as target-state guidance, not
  guaranteed live session tooling.
