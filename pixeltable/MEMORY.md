# Schema Section Harness — MEMORY.md

## Open Decisions

- **PostGIS at the Pixeltable layer.** Should migrations enable PostGIS extension on the embedded PG backend for native spatial indexing and ST_* queries? Current: spatial queries layer at the DuckDB WASM level downstream. Phase 1 DoD requires decision by 2026-06-01.
- **Plant entity split.** Should `landscape_entities` split into `existing_plants` (reality-capture derived) and `proposed_plants` (VW design) for cleaner queries and audit trails? Current: unified table. Trade: query clarity vs. denormalization cost.
- **Embedding index generalization.** The 2 embedding indices on `landscape_entities` (label embedding + class embedding) work well. Should we adopt the same pattern for other high-cardinality tables like `ifc_elements` (100+ elements per project)?

## Failed Experiments

_Nothing logged yet — this section will accumulate as the ratchet runs._

## Session Handoff Notes

- **Current state timestamp.** 2026-05-13 (last harness control files written).
- **Live migration count.** 14 (0001–0014 after harness landing).
- **Live table count.** 40 (36 current + 4 new in 0014 harness migration).
- **Owned namespaces.** `lattice/execution`, `lattice/bridge`, `lattice/genai`, `lattice/reality`, `lattice/harness` (5 total).
- **Pixeltable version pinned.** 0.6.0 (see `pixeltable/pyproject.toml`).
- **Geometry column pattern.** Always `pxt.String` storing WKT (e.g., `POINT(-122.4 37.8)`) or GeoJSON. No `pxt.Geometry` type exists in 0.6.x.
- **Migration path.** `pixeltable/migrations/` (NOT `pixeltable/service/migrations/`).
- **Helpers location.** `pixeltable/migrations/_helpers.py` — contains `ensure_namespace`, `ensure_table`, `ensure_column`, `assert_ownership`, `OWNED_PARENTS` tuple, `FORBIDDEN_PREFIXES` tuple.
- **Docs sync.** The `scripts/pre-commit-docs-check.sh` script enforces that schema docs match code. Must run before commit.
- **Next action.** Harness bootstrap should propose one enhancement to the embedding index strategy or post-GIS decision path.
