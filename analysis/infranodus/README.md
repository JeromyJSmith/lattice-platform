# analysis/infranodus

InfraNodus knowledge graph workspace for LATTICE gap analysis.

## What lives here

| File | Produced by | Consumed by |
|------|-------------|-------------|
| `goal-vs-implementation.diff.json` | `build-gap-analysis.py` (`difference_between_texts`) | harness proposer, gap-analysis briefs |
| `gap-analysis-<date>.json` | `build-gap-analysis.py` (`generate_content_gaps`) | section harness proposals |
| `infranodus-capability-harvest.md` | hand-authored harvest pilot | registry, manifest, schema-map consolidation |
| `infranodus-capability-manifest.yaml` | hand-authored manifest pilot | wrapper schema mapping, future gate-scoring work |
| `infranodus-schema-map.md` | hand-authored schema map | wrapper schema families, prompt hook, promotion logic |
| `README.md` | hand-authored | `create_knowledge_graph`, `analyze_existing_graph_by_name` |

## Named graphs in InfraNodus workspace

| Graph name | Corpus | Refresh cadence |
|------------|--------|-----------------|
| `lattice-goals` | `meta/harness/GOAL.md` | per-sprint |
| `lattice-implementation` | `meta/harness/CURRENT-STATE.md` | per-sprint |
| `lattice-capabilities` | all `analysis/capabilities/*.yaml` | per-registry-update |

## Running gap analysis

```bash
# Dry run (no API calls, writes stub JSON):
uv run meta/harness/bootstrap/build-gap-analysis.py --dry

# Live run (requires INFRANODUS_API_KEY):
export INFRANODUS_API_KEY="<your-key>"
uv run meta/harness/bootstrap/build-gap-analysis.py
```

## Auth

Set `INFRANODUS_API_KEY` in your shell rc (`.zshrc` / `.bashrc`).
The MCP server (`mcp__infranodus__*` tools) reads the same env var.
Restart Claude Code after setting it so the MCP server inherits the key.

## Fractal lifecycle pilot

InfraNodus is now the first explicit pilot slice for the fractal lifecycle:

1. capability harvest
2. registry
3. manifest
4. schema mapping
5. evaluation
6. promotion

The local artifacts for that slice are:

- `analysis/capabilities/infranodus-capability-registry.yaml`
- `analysis/infranodus/infranodus-capability-harvest.md`
- `analysis/infranodus/infranodus-capability-manifest.yaml`
- `analysis/infranodus/infranodus-schema-map.md`

The point is to exercise the exact same lifecycle that the broader wrapper
contract requires, but with one real tool that already has:

- an MCP server
- a harvested capability set
- corpus-discipline rules
- durable graph artifacts
- clear promotion value in Meta-Harness comparison work
