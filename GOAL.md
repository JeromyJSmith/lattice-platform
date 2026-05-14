# GOAL — Next Session

**One session. One objective: Graphify + GitNexus + InfraNodus fully wired.**

---

## Context

These three tools were identified as the solution to the "agents write before reading" problem. They give any agent a queryable graph of the repo so it understands structure before touching code. Phase 1 of the capability harvest was planned but never executed. This session finishes it.

Current state (as of 2026-05-14):
- **graphify** — binary installed, `graphify.toml` exists, but `graphify-out/` has never been generated and it is NOT in `.mcp.json`
- **gitnexus** — NOT installed (not in `package.json` devDeps), hooks silently fail
- **infranodus** — registered in `.mcp.json` and working, but corpus only covers goals/capabilities — SCHEMA.md, ARCHITECTURE.md, AGENT_ONBOARDING.md are NOT ingested

---

## Task List

### 1. Capability Harvest (do this first — non-negotiable per `.claude/rules/capability-harvest-protocol.md`)

For each tool, produce or update the capability registry at `analysis/capabilities/<tool>-capability-registry.yaml`:

- **graphify** — run `graphify --help` and `graphify list-tools` (or equivalent), enumerate every CLI command/subcommand/MCP tool surface, fill registry rows with ACTIVE/DEFERRED/BLOCKED
- **gitnexus** — run `npx gitnexus --help` after install, enumerate all hook integration points, slash commands, CLI subcommands
- **infranodus** — all 30+ MCP tools are already registered; audit which are ACTIVE vs DEFERRED in `analysis/capabilities/infranodus-capability-registry.yaml`

### 2. Install

```bash
# gitnexus — project-local devDep (never -g)
npm install gitnexus --save-dev

# graphify — already installed; verify with:
graphify --version
```

InfraNodus runs via npx in `.mcp.json` — no install needed, just verify the API key is in `.env`.

### 3. Init / Run / Analyze

**graphify:**
```bash
# Generate the repo graph
graphify run

# Verify output exists
ls graphify-out/

# Install project-local MCP integration
graphify install-integrations --project-local

# Add to .mcp.json if not already present
```

**gitnexus:**
```bash
# Analyze repo after install
npx gitnexus analyze

# Add to .mcp.json
# Wire PreToolUse/PostToolUse hooks in .claude/settings.json or hooks config
```

**InfraNodus — corpus ingestion (most critical):**
Create a named graph `lattice-architecture` from the canonical docs:
- `meta/SCHEMA.md`
- `meta/ARCHITECTURE.md`
- `meta/AGENT_ONBOARDING.md`
- `meta/API.md`
- `CLAUDE.md`

Use `mcp__infranodus__create_knowledge_graph` or `mcp__infranodus__analyze_text` per doc, then merge into a single graph with `mcp__infranodus__merged_graph_from_texts`.

### 4. Verify Everything Works

After wiring:

1. Query InfraNodus: `mcp__infranodus__retrieve_from_knowledge_base` with query "sidecar URL port" — should return `127.0.0.1:7770/healthz`
2. Query InfraNodus: `mcp__infranodus__retrieve_from_knowledge_base` with query "Pixeltable table ifc_elements path" — should return `lattice/bridge/ifc/ifc_elements`
3. graphify MCP: query for a file path and confirm the graph is navigable
4. gitnexus: confirm hooks are wired and fire on a test tool call

---

## Definition of Done

- [ ] `graphify-out/` exists and is non-empty
- [ ] graphify is in `.mcp.json` as an MCP server
- [ ] gitnexus is in `package.json` devDependencies
- [ ] gitnexus is in `.mcp.json` or wired via hooks
- [ ] InfraNodus graph `lattice-architecture` exists with SCHEMA + ARCHITECTURE + AGENT_ONBOARDING + API + CLAUDE.md content
- [ ] InfraNodus retrieval returns correct sidecar URL and table paths
- [ ] All three capability registries have zero UNKNOWN rows
- [ ] `bash scripts/pre-commit-docs-check.sh` passes
- [ ] Everything committed and pushed to main

---

## Files to Read First (mandatory pre-flight)

Per `.claude/rules/read-before-you-wreck.md`:

1. `meta/SCHEMA.md`
2. `meta/ARCHITECTURE.md`
3. `meta/AGENT_ONBOARDING.md`
4. `.mcp.json`
5. `analysis/capabilities/infranodus-capability-registry.yaml`
6. `analysis/capabilities/graphify-parisgroup-capability-registry.yaml`
7. `analysis/capabilities/gitnexus-capability-registry.yaml`
8. `.claude/rules/capability-harvest-protocol.md`
9. `.claude/rules/zero-dead-dna.md`
10. `.claude/rules/dependency-allowlist.md`

Do not write a single line of wiring code before reading all ten.

---

*This file self-destructs after the session — delete it when all checkboxes are checked.*
