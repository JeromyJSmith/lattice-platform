# Global Meta-Harness — MEMORY.md

## Open Decisions

- **Wave 2 InfraNodus integration path.** Should InfraNodus connect via Obsidian vault markdown (existing knowledge graph infrastructure) or via a dedicated repo-markdown adapter that reads `meta/` docs directly? Obsidian route reuses the existing `knowledge-index.sqlite` pipeline; repo-markdown route keeps everything in-tree and version-controlled. Decision needed before Phase 2 scheduling work begins.

- **Cross-section coordination channel.** Should subagents share cycle state via `lattice/harness/section_events` (current design — each section appends events) or via a separate lightweight coordination table (e.g., `lattice/harness/cycle_state`) with a single canonical row per active cycle? The events table is append-only and auditable; a state table enables simpler polling but adds a write-contention surface.

- **Global score weighting.** All 7 sections currently carry equal weight (1/7 each). Should sections with more active development (schema, api) carry higher weight to make the global signal more responsive to the work actually happening? Alternatively, sections with lower baseline scores (schema at 46/100) could carry a temporary boost weight until they reach 70, then return to equal weight.

## Failed Experiments

_Nothing logged yet. This section accumulates as the ratchet runs. Each entry should include: date, section, what was tried, why it was rejected (score gate or apply failure), and any lessons for future proposals._

## Session Handoff Notes

- **Date.** 2026-05-13.
- **Baseline global score.** Schema section scored 46/100 at baseline (see `meta/harness/baseline-2026-05-13.json`). Scores for the other 6 sections are not yet captured — their scoring scripts do not exist yet and will be added in Phase 1 continuation.
- **Phase.** Phase 1 in progress. Meta-harness bootstrap (Commit 1) has landed: `meta/harness/GOAL.md`, `meta/harness/MEMORY.md`, `meta/harness/bootstrap/run-autoresearch.sh`, `meta/harness/CLAUDE.md` written.
- **Migration state.** 14 migrations landed (0001–0014). Next migration is 0015.
- **Pixeltable harness tables.** `lattice/harness/health_snapshots`, `lattice/harness/harness_proposals`, `lattice/harness/section_events`, `lattice/harness/global_decisions` — declared in migration 0014. Rows not yet populated (no cycles have run).
- **Next action.** Write the 6 remaining section scoring scripts (`score-api.sh` through `score-ddc.sh`) and `score-global.sh`. Then run first full global cycle: `bash meta/harness/bootstrap/run-autoresearch.sh schema`.
