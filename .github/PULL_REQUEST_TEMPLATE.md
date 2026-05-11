# Summary

<!-- 1-3 sentences. What changed and why. -->

## LATTICE Area

- [ ] vw-bridge (Vectorworks plugin / IFC ingest)
- [ ] 3d-viewer (ThatOpen / Three.js / R3F — Context A)
- [ ] analytics-layer (deck.gl / DuckDB WASM — Context B)
- [ ] data-layer (Pixeltable schema / sidecar routes)
- [ ] agent-runtime (worker, dispatch, streaming)
- [ ] operator-console (`/runtime` UI)
- [ ] plant-geometry (LOD 100 → LOD 300 pipeline)
- [ ] point-cloud (Potree / PDAL / Open3D)
- [ ] devex / infra / CI

## Tests run

- [ ] `make test-no-pxt`
- [ ] `make test-pxt`
- [ ] `bun run build`
- [ ] Manual smoke test at `/runtime`
- [ ] (other — describe below)

## Pixeltable schema changes

- [ ] Yes — new migration file in `pixeltable/migrations/`
- [ ] Yes — `.schema-snapshot.yaml` regenerated via `make snapshot`
- [ ] No

## Breaking changes

- [ ] Yes — describe migration path below
- [ ] No

## Related issues

<!-- e.g. "Closes #42, refs #17" -->
