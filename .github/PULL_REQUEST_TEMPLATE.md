# Summary

<!-- One sentence: what changed and why. -->

## Linear + Agent Lane

<!-- Required. linear-sync-check CI fails without these. -->

- **Linear issue:** <!-- LAT-XX or MAR-XX -->
- **Agent lane:** <!-- copilot | claude-code | codex | warp-pi | hermes | human-only -->
- **Branch:** <!-- <agent-prefix>/LAT-XX-slug — must match lane prefix in meta/agent-lanes.md -->

## LATTICE Area

- [ ] vw-bridge (Phase D — Vectorworks plugin / IFC ingest)
- [ ] 3d-viewer (Phase F — ThatOpen / Three.js / R3F — Context A)
- [ ] analytics-layer (Phase G — deck.gl / DuckDB WASM — Context B)
- [ ] data-layer (Phase B — Pixeltable schema / sidecar routes)
- [ ] agent-runtime (Phase J — worker, dispatch, streaming)
- [ ] operator-console (Phase J — `/runtime` UI)
- [ ] plant-geometry (Phase H — LOD 100 → LOD 300 pipeline)
- [ ] point-cloud (Phase I — Potree / PDAL / Open3D)
- [ ] cesium / reality-capture (Phase K)
- [ ] ddc-skills (Phase M — DDC skills library integration)
- [ ] knowledge-ops (Phase N — substrate production operations)
- [ ] outreach / pilot (Phases O–P — MARPA engagement)
- [ ] devex / infra / CI
- [ ] meta-harness (docs substrate, 9-section structure, ingestion)

## Tests run

- [ ] `make test-no-pxt`
- [ ] `make test-pxt`
- [ ] `bun run build`
- [ ] Manual smoke test at `/runtime`
- [ ] `docs-sync-check` passes (CI auto-runs)
- [ ] `bash meta/harness/docs/score-docs.sh` reports no critical regressions
- [ ] `uv run python scripts/detect-doc-gaps.py` shows no new severity=critical gaps
- [ ] (other — describe below)

## Pixeltable schema changes

- [ ] Yes — new migration file in `pixeltable/migrations/` (next sequential number; 0001–0016 are write-once; **next = 0017**)
- [ ] Yes — `.schema-snapshot.yaml` regenerated via `make snapshot`
- [ ] No

## Meta-Harness 9-section structure

If this PR touches `meta/harness/docs/`, confirm:

- [ ] Edits stay within the canonical 9 sections (GOAL, MEMORY, AGENT, gold_goals, tutorials, research, docs, api_reference, skills_registry)
- [ ] No new top-level section was added without a doctrine update
- [ ] Any `_gated/` content remains `status: dormant` with `gate_status: not_triggered` frontmatter
- [ ] N/A — this PR does not touch `meta/harness/docs/`

## _gated/ dormancy policy

If this PR touches `meta/harness/docs/research/_gated/`, confirm:

- [ ] All new/edited gated content carries `status: dormant` + `gate_status: not_triggered`
- [ ] No architecture code references gated vendors as live dependencies
- [ ] If a gate has fired, link the human confirmation in this PR body
- [ ] N/A — this PR does not touch `_gated/`

## OSS-self-hosted doctrine

- [ ] No new commercial SaaS dependency introduced
- [ ] If a commercial tier was referenced, it is gated under `_gated/<vendor>-commercial/`
- [ ] Self-hosting path is documented for any new third-party component
- [ ] N/A — this PR does not introduce third-party components

## Phase B status acknowledgement

- [ ] I have NOT proposed code that depends on `search_tutorials`, `search_research`, `search_docs`, `search_api_reference`, or `get_coverage_gaps` returning data (those tables do not exist until Phase B M3 Max bootstrap runs)
- [ ] OR — this PR is the Phase B bootstrap itself and explicitly creates those tables

## Breaking changes

- [ ] Yes — describe migration path below
- [ ] No

## Related issues

<!-- Use Magic Words to link: "Fixes LAT-XX", "Closes LAT-XX", "Refs LAT-XX" -->
<!-- LAT-XX closes the Linear issue on merge. Refs LAT-XX keeps it In Progress. -->

## Agent quality checklist

If this PR was authored by an agent, confirm:

- [ ] Branch prefix matches lane (`copilot/`, `claude/`, `codex/`, `warp-pi/`, `hermes/`)
- [ ] No files were touched outside the lane's allowed paths (see `meta/agent-lanes.md`)
- [ ] `bash scripts/pre-commit-docs-check.sh` passed before commit (Claude Code lane)
- [ ] N/A — this is a human-authored PR
