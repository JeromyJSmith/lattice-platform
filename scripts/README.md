# LATTICE Scripts

Operational scripts that aren't part of the runtime but are needed for setup, seeding, exports, and one-off pipelines. All scripts run from the repo root (or use absolute paths) and assume the sidecar is up at `127.0.0.1:7770` unless noted.

| Script | What it does |
|---|---|
| [`screenshot-all-routes.ts`](screenshot-all-routes.ts) | Playwright capture of every console route; writes PNGs to `meta/screenshots/` |
| `seed-marpa-projects.ts` (stub) | Reads a CSV/JSON of MARPA projects and POSTs to `/v1/ingest/marpa-projects` |
| `seed-fixtures.py` (stub) | Wrapper for `pixeltable/scripts/load_fixtures.py` — runs from repo root |
| `export-parquet.py` (stub) | Exports all `lattice/bridge/*` tables to `public/data/*.parquet` for DuckDB WASM |
| `potree-convert.sh` (stub) | Wraps PotreeConverter; takes `.las` input and writes Potree octree to `public/potree/<id>/` |

Run any TypeScript script with `bun scripts/<name>.ts`. Python scripts via `uv run python scripts/<name>.py` from the `pixeltable/` directory, or `python3 scripts/<name>.py` from repo root if it only uses stdlib.
