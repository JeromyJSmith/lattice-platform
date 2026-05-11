# LATTICE Pixeltable Schema Reference

Canonical human-readable reference for the LATTICE Pixeltable schema.

## Overview

- **36 tables applied** + **9 planned** (45 total post-Phase-2-execution) across 6 owned namespaces (`lattice/execution`, `lattice/bridge`, `lattice/genai`, `lattice/reality`, `lattice/harness` *planned*, `lattice/knowledge` *planned*)
- **Migration trail: 0001-0015** (0001-0013 applied; **0014 + 0015 are planning artifacts** committed to `feature/meta-harness` but not yet executed against live Pixeltable; Phase 2 of the Meta-Harness build runs `make migrate-dryrun` then `make migrate` to land them)
- **Pixeltable version: 0.6.0** (pinned via `pixeltable/pyproject.toml`)
- **Geometry type: `pxt.String`** storing WKT or GeoJSON. Pixeltable 0.6.x has no native Geometry type. PostGIS spatial queries layer on at the DuckDB WASM query layer downstream.
- **Migration path: `pixeltable/migrations/`** (NOT `pixeltable/service/migrations/`)
- **Ownership invariant:** see `pixeltable/migrations/_helpers.py::OWNED_PARENTS`. Only namespaces listed there may be created/written by migrations.

## Namespace Map

```
lattice/
├── execution/           # Agent lifecycle (6 tables)
│   ├── agent_threads
│   ├── agent_messages
│   ├── agent_runs
│   ├── agent_stream_events
│   ├── agent_artifacts
│   └── agent_outcomes
├── bridge/              # Source-of-truth bridge layer
│   ├── vw/
│   │   └── vectorworks_exports
│   ├── ifc/
│   │   ├── ifc_elements          # 26 cols added in 0012
│   │   └── ifc_property_sets
│   ├── itwin/
│   │   ├── itwin_sync_jobs
│   │   ├── itwin_changed_elements
│   │   └── connector_versions
│   ├── marpa/
│   │   ├── marpa_parse_runs
│   │   └── marpa_projects
│   ├── semantic/
│   │   ├── semantic_sidecars
│   │   └── landscape_entities    # + 2 embedding indices
│   ├── evidence/
│   │   ├── promotion_events
│   │   └── harness_run_refs
│   ├── health/
│   │   ├── schema_drift_events
│   │   └── bridge_gap_matrix
│   ├── project_georef             # 67 cols — canonical coord authority (0013)
│   ├── plant_assets               # 3D asset registry (0012)
│   ├── site_zones                 # 0012
│   └── reference_images           # 0012
├── genai/               # GenAI pipeline (0012)
│   ├── comfyui_jobs
│   ├── model_registry
│   └── training_runs
└── reality/             # Reality capture (0013)
    ├── drone_flights
    ├── drone_frames               # pxt.Image column
    ├── gaussian_splats
    ├── point_cloud_sessions
    └── mirror_state               # 7 sync flags + divergence score
```

## Migration Trail

| Migration | Purpose |
|---|---|
| 0001 | Create `lattice` root namespace |
| 0002 | Create `lattice/execution/*` (agent lifecycle tables) |
| 0003 | Create `lattice/bridge/*` sub-namespaces |
| 0004 | Create VW tables (`vectorworks_exports`) |
| 0005 | Create IFC tables (`ifc_elements`, `ifc_property_sets`) |
| 0006 | Create iTwin tables (sync jobs, changed elements, connector versions) |
| 0007 | Create MARPA tables (`marpa_parse_runs`) |
| 0008 | Create semantic tables + embedding configuration |
| 0009 | Create evidence tables (`promotion_events`, `harness_run_refs`) |
| 0010 | Create health tables (`schema_drift_events`, `bridge_gap_matrix`) |
| 0011 | Add embedding indices to `landscape_entities` |
| 0012 | Extended schema: 26 cols on `ifc_elements`, `plant_assets`, `marpa_projects`, `site_zones`, `reference_images`, full `lattice/genai/*` namespace |
| 0013 | Georef + reality + mirror: `project_georef` (67 cols), `lattice/reality/*` namespace (5 tables) |

## Table Reference

### lattice/execution

| Table | Migration | Purpose |
|---|---|---|
| `agent_threads` | 0002 | Top-level conversation thread per agent run |
| `agent_messages` | 0002 | User/assistant message history per thread |
| `agent_runs` | 0002 | Run lifecycle (pending → running → completed/failed) |
| `agent_stream_events` | 0002 | Token-level stream deltas for live UI |
| `agent_artifacts` | 0002 | Files/blobs produced by a run |
| `agent_outcomes` | 0002 | Final success/failure summary + metrics |

### lattice/bridge/vw

| Table | Migration | Purpose |
|---|---|---|
| `vectorworks_exports` | 0004 | One row per VW IFC/DXF export with `vw_export_hash` |

### lattice/bridge/ifc

| Table | Migration | Purpose |
|---|---|---|
| `ifc_elements` | 0005, extended 0012 | Parsed IFC entities; 26 added cols carry georef + classification |
| `ifc_property_sets` | 0005 | Pset/Qto attached to elements |

### lattice/bridge/itwin

| Table | Migration | Purpose |
|---|---|---|
| `itwin_sync_jobs` | 0006 | Connector sync job records |
| `itwin_changed_elements` | 0006 | Changed-element manifest per sync |
| `connector_versions` | 0006 | Connector + iTwin core version tracking |

### lattice/bridge/marpa

| Table | Migration | Purpose |
|---|---|---|
| `marpa_parse_runs` | 0007 | MARPA grammar parse runs |
| `marpa_projects` | 0012 | Per-project MARPA project registry |

### lattice/bridge/semantic

| Table | Migration | Purpose |
|---|---|---|
| `semantic_sidecars` | 0008 | NLP sidecar outputs per source artifact |
| `landscape_entities` | 0008 | Extracted landscape entities (+ 2 embedding indices, 0011) |

### lattice/bridge/evidence

| Table | Migration | Purpose |
|---|---|---|
| `promotion_events` | 0009 | QA harness promotion events |
| `harness_run_refs` | 0009 | Pointers to external harness runs |

### lattice/bridge/health

| Table | Migration | Purpose |
|---|---|---|
| `schema_drift_events` | 0010 | Detected drift between expected and live schema |
| `bridge_gap_matrix` | 0010 | Gap matrix per VW export hash |

### lattice/bridge (top-level)

| Table | Migration | Purpose |
|---|---|---|
| `project_georef` | 0013 | **Canonical coordinate authority** — 67 cols: survey, IFC site, VW internal origin, OSM, KML/Shapefile, GeoTIFF DEM, transforms, what3words, plus_code |
| `plant_assets` | 0012 | 3D plant asset registry with LOD tier (100/200/300/400) |
| `site_zones` | 0012 | Project site zones / planting areas |
| `reference_images` | 0012 | Reference imagery (photos, renderings) attached to project/element |

### lattice/genai

| Table | Migration | Purpose |
|---|---|---|
| `comfyui_jobs` | 0012 | ComfyUI 2D→3D / image-gen job records |
| `model_registry` | 0012 | Local model registry (Ollama, ComfyUI checkpoints, embedding models) |
| `training_runs` | 0012 | Fine-tune / LoRA training run records |

### lattice/reality

| Table | Migration | Purpose |
|---|---|---|
| `drone_flights` | 0013 | One row per drone flight (mission, pilot, weather, georef) |
| `drone_frames` | 0013 | Per-frame row with `pxt.Image` column + GPS/IMU + computed CLIP/YOLO/blur columns |
| `gaussian_splats` | 0013 | .ply / .splat sessions with alignment-to-georef matrix |
| `point_cloud_sessions` | 0013 | .las / .laz capture sessions with PDAL processing state |
| `mirror_state` | 0013 | Per-project digital-twin sync state: 7 platform sync flags + divergence score + warnings |

## Key Rules

- **All coordinates EPSG-normalized before write.** No raw VW internal coordinates anywhere in Pixeltable.
- **`project_georef` is the single coordinate authority** per project. Every other spatial row references its `project_id` to resolve to a canonical frame.
- **`mirror_state.design_reality_divergence_m`** tracks sync health across the 7 platform layers (VW design, iTwin BIM, reality capture, DDC ERP, Cesium globe, ThatOpen viewer, deck.gl, Potree).
- **`plant_assets.lod`** ladder: `100`=concept, `200`=schematic, `300`=construction, `400`=fabrication.
- **`ifc_elements` extended in 0012** with 26 columns covering georef + BIS classification (`bis_class`, `bis_subclass`, `geom_point_wkt`, `latitude`, `longitude`, etc.).
- **Geometry is always `pxt.String`** (WKT or GeoJSON). There is no `pxt.Geometry` type in 0.6.x.
- **Write-once migrations.** Never edit a landed migration — always increment the number.
- **Owned parents.** Before creating tables in a new namespace, `pxt.create_dir()` every ancestor first and add the namespace to `OWNED_PARENTS` in `pixeltable/migrations/_helpers.py`.

## Idempotency Helpers

All migrations use the helpers in `pixeltable/migrations/_helpers.py`:

- `ensure_namespace(pxt, path)` — `create_dir(if_exists='ignore')` guarded by `OWNED_PARENTS`
- `ensure_table(pxt, path, schema, ...)` — create-or-skip
- `ensure_column(pxt, table, col, type, default=...)` — add-or-skip
- `ensure_embedding_index(pxt, table, col, name, embed_fn)` — add-or-skip

See `pixeltable/migrations/_helpers.py` for the canonical implementations.
