# LATTICE Architecture

The one authoritative architecture document. When other docs and this one disagree, this one is right and the others are stale.

Last verified against live state: 2026-05-11 (migration 0012 applied, runtime console green, 217 issues tracked).

---

## 1. Stack table (pinned, verified)

| Layer | Choice | Version | Verified |
|---|---|---|---|
| **Platform** | macOS / Apple Silicon | Darwin 25.5 | ✅ |
| **JS runtime** | Bun | 1.3.11 | ✅ |
| **Python** | CPython | 3.11.10 | ✅ |
| **Python pkg mgmt** | uv | latest | ✅ |
| **Operator UI** | TanStack Start | 1.167.65 | ✅ |
| **Framework** | React | 19 | ✅ |
| **Bundler** | Vite | 8 | ✅ |
| **Styling** | Tailwind CSS | 4 | ✅ |
| **State** | TanStack Store / Query / Form / Router / Table / Virtual / Hotkeys / Pacer | latest | ✅ |
| **Auth** | Better Auth | 1.5.3 | ✅ |
| **Sidecar HTTP** | FastAPI | ≥0.116 | ✅ |
| **Sidecar ASGI** | uvicorn[standard] | ≥0.34 | ✅ |
| **Data layer** | Pixeltable | 0.6.0 (pinned) | ✅ |
| **Embedded PG** | PostgreSQL | 16 (inside Pixeltable) | ✅ |
| **Spatial ext** | PostGIS | 3.5.2 (inside Pixeltable) | ✅ |
| **Vector ext** | pgvector | 0.8.1 (inside Pixeltable) | ✅ |
| **3D engine A** | `@thatopen/components` + `@thatopen/components-front` + `@thatopen/fragments` | 3.4.6 / 3.4.3 / 3.4.5 | ✅ |
| **Three.js** | three | 0.184.0 | ✅ |
| **WASM IFC** | web-ifc | 0.0.77 | ✅ |
| **Analytics B** | `@deck.gl/core` + `@deck.gl/layers` | 9.3.2 | ✅ |
| **Browser SQL** | DuckDB WASM | 1.33.1-dev45.0 (pinned) | ⏳ install pending |
| **Basemap** | MapLibre GL + react-map-gl/maplibre | 5.24.0 / 8.1.1 | ⏳ |
| **Globe** | Cesium + resium + `@deck.gl/cesium` | ^1.125 / ^1.19 / 9.3.2 | ⏳ |
| **Point cloud** | potree-core | 2.0.15 | ⏳ |
| **iTwin (Tier 1)** | `@itwin/core-geometry`, `@itwin/core-common`, `@itwin/core-quantity` | 5.9.2 | ⏳ install pending issue #167 |
| **IFC parse** | ifcopenshell | ≥0.8.5 | ✅ |
| **DXF parse** | ezdxf | ≥1.4.3 | ⏳ |
| **Real agent** | `claude -p --output-format stream-json --include-partial-messages` | CLI 2.1.138 | ✅ |
| **Local LLM** | Ollama | latest | ⏳ |
| **Local image/3D** | ComfyUI | latest | ⏳ |
| **Local cost DB** | Qdrant (in OrbStack VM) | latest | ⏳ |
| **Render** | Cinema 4D + Redshift | Maxon licensed | ⏳ |

✅ = installed and verified live · ⏳ = scaffolded in docs/Issues, not yet installed

The locked versions live in [`package.json`](../package.json) and [`pixeltable/pyproject.toml`](../pixeltable/pyproject.toml). The pinned version is what's tested in CI; floating ranges (`^x.y.z`) are accepted for non-core deps.

---

## 2. The two rendering contexts (Context A vs Context B — never conflate)

LATTICE has two distinct rendering surfaces. Mixing them is the most common architectural mistake.

### Context A — full 3D scene (`/viewer`)

Three.js + React Three Fiber + `@thatopen/components` 3.4.6 + `@thatopen/fragments` 3.4.5.

This is the digital twin. Full orbit, fly-through, mesh fidelity, Cinema 4D output. Element selection wired to property panels. Plant geometry at LOD 100 (placeholders) or LOD 300 (botanical meshes). Cinematic lighting via `PostproductionRenderer`.

- **Coordinate system:** iTwin local + iTwin `Point3d` / `Transform`. WGS84 is converted at the boundary.
- **Geometry source:** ThatOpen `.frag` Fragment binaries, served from Pixeltable as cached blobs.
- **Use this for:** spatial review, client walkthrough, element selection, GLTF/C4D export.

### Context B — analytical layer (`/analysis`)

deck.gl 9.3.2 + luma.gl + loaders.gl + DuckDB WASM + MapLibre (no API key needed).

This is data-driven, map-projected, georeferenced. ScatterplotLayer for plant positions, ColumnLayer for density / cost, HeatmapLayer for irrigation demand, GeoJsonLayer for zone polygons and shadow segmentation output.

- **Coordinate system:** WGS84 longitude/latitude, real-world projection on a basemap.
- **Geometry source:** Parquet exports of `lattice/bridge/ifc/ifc_elements` and related tables, loaded zero-copy via `loaders.gl` ParquetLoader.
- **Use this for:** quantity takeoff, cost analysis, irrigation zoning, solar / shadow analysis, plant density studies.

### A third surface — globe (`/globe`)

CesiumJS + resium + `@deck.gl/cesium`. Different from both A and B: real terrain at planet scale, MARPA project pins, click-to-fly-to, lazy-load IFC Fragment models draped at correct lat/lon, deck.gl analytical layers floating on top.

This is **not a viewer** in the Context A sense — it's a portfolio map. Once you've clicked into a project and zoomed in past 100 m, you transition into Context A (the ThatOpen viewer) for that project.

See [`meta/CESIUM_SETUP.md`](CESIUM_SETUP.md) for the coordinate bridge.

---

## 3. Data flow

```
                  Vectorworks 2026 (Mac, GUI)
                            │
                            │  VW C++ plugin
                            │  "Generate LATTICE Placeholders" (LOD 100)
                            │  "Export IFC" (IFC4.3 with georeferencing)
                            │  vwx-mcp Python `vs.*` API
                            ▼
                  IFC4.3 file on disk
                            │
                            │  POST /v1/vw/sidecars (sidecar)
                            │  ifcopenshell parse, coord normalize (EPSG:4326 WGS84)
                            ▼
   ┌──────────── Pixeltable (PG 16 + PostGIS + pgvector) ─────────────────┐
   │                                                                       │
   │  lattice/bridge/vw/vectorworks_exports          (the boundary record)│
   │  lattice/bridge/ifc/ifc_elements                (the element catalog)│
   │       └── geom_point_wkt, lat/lon/elev, BIS class, DDC admin,        │
   │           asset_id, lod_level, glb_path …  (migration 0012)          │
   │  lattice/bridge/ifc/ifc_property_sets                                 │
   │  lattice/bridge/plant_assets                    (species → GLB)      │
   │  lattice/bridge/marpa_projects                  (portfolio registry) │
   │  lattice/bridge/site_zones                      (PostGIS polygons)   │
   │  lattice/bridge/reference_images                (geo-tagged photos)  │
   │  lattice/bridge/semantic/*                      (DDC skills + pgvec) │
   │  lattice/bridge/{itwin,marpa,evidence,health}/* (cross-system refs)  │
   │                                                                       │
   │  lattice/execution/{agent_threads,messages,runs,stream_events,        │
   │                     artifacts,outcomes}         (the runtime ledger) │
   │                                                                       │
   │  lattice/genai/{comfyui_jobs,model_registry,training_runs}            │
   └─────────────────────┬────────────────────────────────────────────────┘
                         │
                         │ Pixeltable client (in-process inside sidecar)
                         ▼
   ┌─────── FastAPI sidecar @ 127.0.0.1:7770 ─────────────────────────────┐
   │                                                                       │
   │  Auth:  require_local_socket_or_token  (UDS / X-Bridge-Token)        │
   │  Routes:                                                              │
   │    POST /v1/runtime/events                bulk-ingest RuntimeEvents  │
   │    GET  /v1/runtime/runs                  list agent_runs            │
   │    GET  /v1/runtime/stream-events         poll stream events         │
   │    GET  /v1/runtime/stream-events/sse     EventSource push           │
   │    POST /v1/vw/sidecars                   VW IFC ingest              │
   │    POST /v1/ingest/reference-image        geo-tagged photo ingest    │
   │    POST /v1/erp/boq           (future)    OpenConstructionERP BOQ    │
   │    POST /v1/erp/cost-search   (future)    CWICR semantic search      │
   │    POST /v1/genai/infer       (future)    Local model dispatch       │
   │    GET  /v1/genai/models      (future)    Model registry             │
   │                                                                       │
   │  Worker loop:  poll agent_runs WHERE status='pending'                │
   │                claim → emit run.started (status='running')           │
   │                spawn claude -p subprocess, parse stream-json deltas  │
   │                emit stream.delta rows (+ SSE pub/sub fan-out)        │
   │                final run.completed                                    │
   └──────────────────────┬──────────────────────────────────────────────┘
                          │  HTTPS / SSE
                          ▼
   ┌─── Operator browser (TanStack Start @ localhost:3000) ───────────────┐
   │                                                                       │
   │  Routes:                                                              │
   │    /                home                                              │
   │    /runtime        Operator Console (runs table + EventTimeline)     │
   │    /viewer         Context A — ThatOpen 3D                           │
   │    /analysis       Context B — deck.gl + DuckDB WASM                 │
   │    /globe          Cesium MARPA portfolio + iTwin overlay            │
   │    /admin          DDC dashboard (cost, BOQ, schedule, skills)       │
   │    /notebooks      Marimo (DuckDB WASM cells + local LLM agent)      │
   │    /threads /agents /runs /evidence /replay /settings (placeholders) │
   │                                                                       │
   │  Server functions (TanStack Start):                                  │
   │    dispatchRun → SidecarClient → POST /v1/runtime/events             │
   │    listRuns / listStreamEvents → GET                                  │
   │    useStreamEvents hook → EventSource SSE                            │
   └───────────────────────────────────────────────────────────────────────┘
```

---

## 4. MCP server topology

LATTICE participates in an MCP-rich ecosystem; every external runtime exposes its tools via MCP rather than ad-hoc HTTP.

| MCP server | Lives at | Purpose in LATTICE |
|---|---|---|
| `vicquick/vwx-mcp` | (TCP socket, in VW process) | VW document automation, plant record reads, IFC export trigger |
| `claude-peers` | (per-user) | Cross-session Claude Code agent coordination |
| `chrome-devtools` | (per-user) | Browser automation for UI testing |
| `browser-harness` | (per-user) | Headless Playwright + CDP, runs `scripts/screenshot-all-routes.ts` |
| `infranodus` | (per-user) | Knowledge graph + content gap analysis (research agent) |
| `pencil` | (per-user) | Design-doc editor (`.pen` files) |
| `claude.ai Notion` etc. | (per-user) | Connectors not owned by LATTICE |

The LATTICE FastAPI sidecar is **not currently an MCP server itself** — it exposes plain REST. Adding an MCP wrapper around the sidecar so other agent runtimes can call LATTICE endpoints via MCP is on the backlog.

---

## 5. Agent role map

Each `agents/<role>/` directory documents what its role owns. Specialised agents are invoked by the orchestrator (when it's wired) or directly by an operator.

| Role | Owns | Pixeltable tables (write) |
|---|---|---|
| `orchestrator/` | Task routing, dispatch loop | `lattice/execution/agent_runs` (status transitions) |
| `vw-bridge/` | VW → IFC4.3 → Pixeltable ingestion | `lattice/bridge/vw/*`, `lattice/bridge/ifc/*` |
| `ifc-enrichment/` | BIS classification, geo-normalization, property cleanup | `lattice/bridge/ifc/ifc_elements` (updates) |
| `geometry/` | Plant geometry, LOD 100 → 300 swap, GLTF/C4D handoff | `lattice/bridge/plant_assets`, `lattice/genai/comfyui_jobs` |
| `reality-capture/` | LiDAR + drone + 360° pipelines | `lattice/bridge/point_clouds` (future) |
| `research/` | Knowledge retrieval, DDC skill search | `lattice/bridge/semantic/*` |
| `analytics/` | Cost, schedule, BOQ, deck.gl layer specs | `lattice/bridge/ifc/ifc_elements` (DDC columns) |

The active runtime today is the worker in `pixeltable/service/worker.py` — it always routes to `claude-cli` (no role specialisation yet). The role split lives in the docs and folder structure ahead of the runtime; the orchestrator will materialise it.

---

## 6. Pixeltable schema overview

26 tables across 3 owned namespaces, post migration 0012.

```
lattice/
├── execution/                      ← runtime ledger (own)
│   ├── agent_threads
│   ├── agent_messages
│   ├── agent_runs                  ← worker polls WHERE status='pending'
│   ├── agent_stream_events         ← token deltas live here
│   ├── agent_artifacts
│   └── agent_outcomes
│
├── bridge/                         ← cross-system bridges (own)
│   ├── plant_assets                ← NEW (0012): species → GLB / C4D paths
│   ├── marpa_projects              ← NEW (0012): portfolio registry
│   ├── site_zones                  ← NEW (0012): PostGIS polygons
│   ├── reference_images            ← NEW (0012): geo-tagged site photos
│   ├── vw/vectorworks_exports
│   ├── ifc/ifc_elements            ← + 26 cols in 0012
│   ├── ifc/ifc_property_sets
│   ├── itwin/itwin_sync_jobs
│   ├── itwin/itwin_changed_elements
│   ├── itwin/connector_versions
│   ├── marpa/marpa_parse_runs
│   ├── semantic/semantic_sidecars  ← pgvector embedding index (0011)
│   ├── semantic/landscape_entities ← pgvector embedding index (0011)
│   ├── evidence/promotion_events
│   ├── evidence/harness_run_refs
│   ├── health/schema_drift_events
│   └── health/bridge_gap_matrix
│
└── genai/                          ← NEW (0012): local AI registry (own)
    ├── comfyui_jobs                ← 2D→3D pipeline jobs
    ├── model_registry              ← Ollama + ComfyUI + GeoAI checkpoints
    └── training_runs               ← GeoAI fine-tune runs

marpa/                              ← OWNED BY MARPA_PLATFORM (read-only here)
lattice/{source,qa,budget,worksheet}/   ← other bodies (FORBIDDEN to write)
```

The ownership invariant is enforced in `pixeltable/migrations/_helpers.py::assert_ownership` and tested at every migration apply. Snapshot of the live schema is at [`pixeltable/.schema-snapshot.yaml`](../pixeltable/.schema-snapshot.yaml); `make verify` diffs live state against it.

---

## 7. PostGIS spatial model

Pixeltable 0.6.0 has no native geometry type, but the embedded PG 16 instance has the PostGIS 3.5.2 extension installed. LATTICE bridges the gap by storing WKT in `pxt.String` columns and running spatial queries at the raw-SQL layer.

**Convention:** every spatial table has the same three companion columns:

| Column | Type | Format |
|---|---|---|
| `geom_*_wkt` | `pxt.String` | OGC Well-Known Text, e.g. `POINT(-122.4194 37.7749)` |
| `longitude`, `latitude` | `pxt.Float` | WGS84 decimal degrees |
| `epsg_code` | `pxt.String` | `EPSG:4326` (canonical) unless explicitly different |
| `elevation_m` | `pxt.Float` (where relevant) | metres above WGS84 ellipsoid |

Spatial queries layer on top via raw SQL:

```sql
-- "what zone is this element in?"
SELECT e.source_element_id, z.zone_id
FROM ifc_elements e
JOIN site_zones z ON ST_Within(
    ST_GeomFromText(e.geom_point_wkt, 4326),
    ST_GeomFromText(z.geom_polygon_wkt, 4326)
)
WHERE e.project_id = $1;
```

Once the PostGIS extension is enabled at the PG layer (issue #185), we'll add Pixeltable computed columns that materialise `geom_point geometry` from `ST_GeomFromText(geom_point_wkt, 4326)`, and queries become first-class.

---

## 8. iTwin usage tier

LATTICE uses iTwin as a **type system + vocabulary**, not as a viewer or cloud service. The full 84-repo map lives in [`meta/ITWIN_MAPPING.md`](ITWIN_MAPPING.md).

Quick summary:

| Tier | Repos | LATTICE stance |
|---|---|---|
| 1 — actively use | `itwinjs-core`, `bis-schemas`, `presentation`, `imodel-transformer`, `changed-elements-react`, `saved-views`, `insights-client` | Install, verify against current stack ([#167](https://github.com/JeromyJSmith/lattice-platform/issues/167)) |
| 2 — reference patterns | `connector-framework`, `imodel-reporter`, `agent-starter`, `iot-demo`, others | Read for design patterns; never import |
| 3 — Cesium integration | `cesium-native`, `itwin-cesium-tutorial-app`, `3d-tiles-samples` | Use for `/globe` route patterns |
| 4 — SKIP (cloud-bound) | `viewer`, `imodels-clients`, `reality-capture`, `mobile-*`, all `platform-api/*` | Never install |
| 5 — tooling | `bis-schema-validation`, `ecjson2md`, `eslint-plugin`, `codemods` | Use as needed |

The one-line insight: LATTICE takes the **schema language** (`bis-schemas`) + the **geometry math** (`@itwin/core-geometry`) + the **iModel ETL** (`@itwin/imodel-transformer`) and ignores the rest.

---

## 9. DDC integration map

LATTICE wraps four pieces of the DataDrivenConstruction ecosystem (full detail in [`meta/DDC_MAPPING.md`](DDC_MAPPING.md)):

| Piece | LATTICE home | Status |
|---|---|---|
| 221 SKILL.md patterns | `skills/ddc/` + indexed in `lattice/bridge/semantic/semantic_sidecars` | Backlog (#172) |
| CWICR cost database | `ddc/cwicr/` (Qdrant in OrbStack VM) | Backlog (#168) |
| OpenConstructionERP | `ddc/erp/` + `pixeltable/service/routes/erp.py` | Backlog (#169) |
| n8n workflow patterns | `ddc/n8n/` (translated to FastAPI handlers) | Backlog (#171) |
| `/admin` dashboard | `ddc/admin/` (DuckDB WASM SQL + ERP REST) | Backlog (#170) |
| Linux .deb converters | `ddc/converters/` (OrbStack Ubuntu VM, fallback only) | On-demand |

The DDC philosophy for LATTICE: **the value is the patterns + cost data, not the file converters.** LATTICE handles IFC/DXF natively via IfcOpenShell + ezdxf on Mac. The Linux .deb converters are fallbacks for edge cases.

---

## 10. The 3D plant asset pipeline (Phase 3)

The end-to-end loop that solves LATTICE's missing-plant-catalog problem. Full diagram in [`genai/3d-asset-pipeline/PIPELINE.md`](../genai/3d-asset-pipeline/PIPELINE.md).

Compressed:

```
geo-tagged photo on /globe pin   ──→  lattice/bridge/reference_images
        (3+ photos per species)
                                        │  PXT trigger
                                        ▼
                                  lattice/genai/comfyui_jobs
                                        │  job-dispatcher.py polls
                                        ▼
                                  ComfyUI workflow plant-2d-to-3d.json
                                        │  output: textured 3D mesh
                                        ▼
                                  assets/plants/lod-300/{species}.glb
                                  assets/plants/c4d/{species}.c4d  (Redshift-ready)
                                        │  human review @ /admin
                                        ▼  (quality_score >= 0.7)
                                  VW Plant Style Manager (via vwx-mcp)
                                  ALL instances update globally
                                        │
                                        ▼
                                  ThatOpen viewer: LOD100 spike → LOD300 mesh
                                  Cesium pin thumbnail updated
```

Every step writes evidence to `lattice/execution/evidence`; the chain is auditable in `/admin`.

---

## 11. Where everything lives

| If you want… | Look at… |
|---|---|
| Project rules | `AGENTS.md`, `CLAUDE.md` (root) |
| Stack table (this doc, section 1) | `meta/ARCHITECTURE.md` |
| 5-minute boot | `meta/AGENT_ONBOARDING.md` |
| Phased plan | `meta/ROADMAP.md` |
| Multi-platform agent handoff | `meta/HANDOFF.md` |
| Backlog | `meta/FEATURE_BACKLOG.md` |
| iTwin / Cesium / DDC integration plans | `meta/ITWIN_MAPPING.md`, `meta/CESIUM_SETUP.md`, `meta/DDC_MAPPING.md` |
| Worktree layout | `meta/WORKTREES.md` |
| Linear setup steps | `meta/LINEAR_SETUP.md` |
| UI screenshots | `meta/UI_SCREENSHOTS.md` |
| Pixeltable migrations | `pixeltable/migrations/00*.py` (numbered) |
| Schema snapshot | `pixeltable/.schema-snapshot.yaml` |
| Sidecar routes | `pixeltable/service/routes/*.py` |
| Worker / agent runtime | `pixeltable/service/worker.py` |
| TanStack Start server fns | `src/server/runtime/*.ts` |
| Sidecar client (TS) | `src/runtime/pixeltable/sidecar-client.ts` |
| Frontend routes | `src/routes/*.tsx` |
| C++ VW plugin | `vw-plugin/` |
| VW Python (`vs.*`) examples | `vw-python/examples/` |
| iTwin integration code | `itwin/` |
| DDC integration code | `ddc/` |
| GenAI (LLM/ComfyUI/GeoAI/3D pipeline) | `genai/` |
| Asset library layout | `assets/` |
| Agent role docs | `agents/<role>/` |
| Skill library | `skills/ddc/`, `skills/lattice/` |
| Scripts | `scripts/` |
| CI workflows | `.github/workflows/` |

---

## 12. Drift detection

This document is current as of commit `e385691` (post-HANDOFF.md, pre-this-doc). To check drift:

```bash
git log --oneline meta/ARCHITECTURE.md      # when was this last touched?
git log --oneline pixeltable/migrations/    # what has the schema gained since?
make verify                                  # live schema vs snapshot
```

If the schema has advanced past the version of this doc, update section 6 (schema overview) and section 7 (PostGIS model) in your PR. The other sections rarely drift — they describe the *shape* of the system, which is the thing we deliberately fix in place.
