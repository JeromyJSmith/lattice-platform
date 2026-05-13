# InfraNodus Runbook

Codifies the 2026-05-13 run as a repeatable proof contract for InfraNodus
gap analysis over the LATTICE corpus.

## Auth

```bash
# Set in ~/.zshrc or ~/.bashrc (never commit):
export INFRANODUS_API_KEY="21813:<your-key>"

# Restart Claude Code so the MCP server inherits the env var:
# Quit → reopen, or kill the MCP process and let it restart.
```

Verify: `mcp__infranodus__analyze_text` should respond without auth error.

## Standard Run (Gap Analysis Cycle)

### 1. Ingest goals corpus

```
mcp__infranodus__analyze_text(
  text="<contents of meta/harness/GOAL.md>",
  graphName="lattice-goals"
)
```

### 2. Ingest implementation corpus

```
mcp__infranodus__analyze_text(
  text="<contents of meta/harness/CURRENT-STATE.md>",
  graphName="lattice-implementation"
)
```

### 3. Goal vs. implementation diff

```
mcp__infranodus__difference_between_texts(
  text1="<GOAL.md contents>",
  text2="<CURRENT-STATE.md contents>"
)
```

Save output to `analysis/infranodus/goal-vs-implementation.diff.json`.

### 4. Surface gaps

```
mcp__infranodus__generate_content_gaps(
  graphName="lattice-goals",
  useSeveralGaps=true,
  gapDepth=2
)
```

### 5. Cluster analysis

```
mcp__infranodus__generate_topical_clusters(
  graphName="lattice-goals"
)
```

### 6. Develop conceptual bridges

```
mcp__infranodus__develop_conceptual_bridges(
  graphName="lattice-goals"
)
```

## Automated CLI Path

```bash
# Dry run (stub JSON, no API calls):
uv run meta/harness/bootstrap/build-gap-analysis.py --dry

# Live run (requires INFRANODUS_API_KEY):
uv run meta/harness/bootstrap/build-gap-analysis.py
```

## Named Graph Conventions

| Graph name | Source | Refresh |
|---|---|---|
| `lattice-goals` | `meta/harness/GOAL.md` | per sprint |
| `lattice-implementation` | `meta/harness/CURRENT-STATE.md` | per sprint |
| `lattice-capabilities` | all `analysis/capabilities/*.yaml` flattened | per registry update |
| `lattice-section-<name>` | section HARNESS.md + score script | per autoresearch cycle |

## Output Artifact Contract

Every InfraNodus run produces:

1. **`analysis/infranodus/goal-vs-implementation.diff.json`** — `difference_between_texts` output, committed as proof
2. **`analysis/infranodus/gap-analysis-<YYYY-MM-DD>.json`** — `generate_content_gaps` output (date-stamped, committed)

Artifacts are proof evidence for:
- `infranodus / difference_between_texts` (registry row)
- `infranodus / generate_content_gaps` (registry row)

## 2026-05-13 Run Notes

- Auth was blocked during session (API key not inherited by MCP server)
- Dry-run stub was written to `analysis/infranodus/goal-vs-implementation.diff.json`
- API key: set `INFRANODUS_API_KEY` in shell rc, restart Claude Code, then re-run
- Next run: verify `mcp__infranodus__analyze_text` works first before full cycle

## Troubleshooting

**MCP returns auth error**: Key not in environment. Restart Claude Code after setting env var.

**Rate limit**: InfraNodus has per-minute limits. Space calls by 2s between graph operations.

**Graph already exists**: `analyze_existing_graph_by_name` instead of `analyze_text` for subsequent runs.

**Large corpus**: Split GOAL.md into sections, ingest each with a section-specific graph name, then merge via `merged_graph_from_texts`.
