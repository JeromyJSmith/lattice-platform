# Pixeltable Operational Substrate

Pixeltable is the LATTICE substrate. Git is the bootstrapping and review surface for now, but the long-term LATTICE system of record is Pixeltable.

## Doctrine

Pixeltable eventually holds everything operational:

- capability harvests, matrices, manifests, and registry rows
- scripts and script metadata
- prompt and agent definitions
- verification runs
- evidence artifacts
- model benchmarks
- task and workpad state
- docs and diagram snapshots
- relationships between files, capabilities, agents, tasks, and evidence

This does not mean every source file disappears from git. Git remains the auditable change surface. Pixeltable indexes, relates, verifies, and serves the operational graph.

## Browser Analytics

DuckDB WASM is the analytical browser surface. The intended flow is:

```text
Pixeltable
  -> Arrow / Parquet export or serving layer
  -> DuckDB WASM in browser
  -> dashboards, Marimo, deck.gl, Meta-Harness views
```

Pixeltable owns persistence and computed data. DuckDB WASM owns fast browser-side analytical querying.

## Staged Integration

| Stage | Behavior |
|---|---|
| 0 | Git files define docs, scripts, configs, migrations, and capability registries |
| 1 | Meta-Harness gives every artifact stable IDs, provenance, and verification outputs |
| 2 | Pixeltable tables ingest the registries, scripts, jobs, evidence, and benchmark rows |
| 3 | Pixeltable serves Arrow/Parquet slices for browser analytics |
| 4 | Meta-Harness decisions query Pixeltable first and write evidence back to Pixeltable |
| 5 | Portable Meta-Harness can snap into another repo with project config and a Pixeltable backend |

## First Schema Targets

Next migration: `0017`.

Candidate namespaces:

```text
lattice/harness/capabilities
lattice/harness/capability_manifests
lattice/harness/scripts
lattice/harness/jobs
lattice/harness/verification_runs
lattice/harness/evidence
lattice/harness/model_benchmarks
lattice/harness/task_state
```

The first migration should be conservative: create tables that mirror committed YAML and evidence files before adding derived views or computed columns.

## Integration Rule

Do the slow integration. Every new file-based harness artifact should already be shaped for Pixeltable ingestion:

- stable `id`
- source path or source URL
- provenance
- state
- verification command
- output artifact path
- relationships to capability rows or jobs

That lets LATTICE move from file-backed harness to Pixeltable-backed harness without redesigning every artifact.
