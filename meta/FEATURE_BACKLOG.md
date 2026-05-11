# LATTICE Feature Backlog
# Updated: May 2026 | This file is the single source of truth for planned work.
# Format: [ ] = not started | [~] = in progress | [x] = done

---

## PRIORITY QUEUE (do next, in order)

- [x] SSE push endpoint for stream events — landed 2026-05-11. In-process pub/sub in worker.py, FastAPI StreamingResponse, useStreamEvents hook on EventSource. Replays history on connect, lives until `event: end`.
- [x] Clickable run rows — landed 2026-05-11. `onRowClick` on RunsTable wires to `runtimeStore.activeRunId`; active row gets a highlight class; SSE subscription auto-rewires when activeRunId changes.
- [x] Rename nav from "TanStack Start" to "LATTICE" — landed 2026-05-11 (header, footer, document title)

---

## OPERATOR CONSOLE (runtime/)

- [x] Run ID display — truncated to last 8 chars in the table, full ID in tooltip on hover (landed 2026-05-11)
- [ ] Task column overflow — truncate long task strings with ellipsis, full text on hover
- [ ] Status badges — color-coded chips instead of plain text (pending=yellow, running=blue, completed=green, failed=red)
- [ ] EventTimeline — render markdown in delta text (bold, bullets, code blocks)
- [ ] EventTimeline — show timestamps per delta, not just seq number
- [ ] EventTimeline — "Copy full response" button that concatenates all deltas for a run
- [ ] Active run indicator — pulse animation on the status line while streaming=true
- [ ] Task input — Cmd+Enter to submit (in addition to Submit button)
- [ ] Empty state — meaningful message when no runs exist yet

---

## AGENT RUNTIME (worker / sidecar)

- [ ] TTFT optimization — optional anthropic SDK path (shaves ~5s off first-token when API key present, CLI is fallback)
- [ ] Failed run handling — if claude CLI exits non-zero, write status=failed + error message as seq 9999 delta
- [ ] Run cancellation — ability to kill an in-flight CLI subprocess and write status=cancelled
- [ ] Concurrent runs — worker currently processes one run at a time; add configurable concurrency limit
- [ ] System prompt management — editable LATTICE system prompt stored in Pixeltable, not hardcoded in worker.py
- [ ] Task routing — route tasks to different agent_kind based on keywords or explicit prefix (e.g., "ifc:" → IFC enrichment agent)

---

## DATA LAYER (Pixeltable / sidecar)

- [ ] IFC ingestion endpoint — POST /v1/ingest/ifc, reads IFC file, writes to lattice/bridge/ifc_elements
- [ ] DXF ingestion endpoint — POST /v1/ingest/dxf, reads DXF via ezdxf, writes to lattice/bridge/dwg_entities
- [ ] .bim ingestion — POST /v1/ingest/bim, reads SQLite via @pxt.udf, merges into lattice/bridge/ifc_elements
- [ ] Parquet export endpoint — GET /v1/export/ifc_elements returns Parquet for DuckDB WASM consumption
- [ ] Georeferencing — normalize all coordinates through IfcSite matrix before writing latitude/longitude to Pixeltable
- [ ] Evidence writes — all MCP tool calls write artifacts to lattice/execution/evidence
- [ ] Schema drift detection — make verify run on sidecar startup and log warnings if live schema diverges from snapshot

---

## 3D VIEWER (viewer/)

- [ ] ThatOpen viewer route — src/routes/viewer/index.tsx with OrthoPerspectiveCamera + PostproductionRenderer
- [ ] IFC load from Pixeltable — fetch IFC bytes from sidecar and load via @thatopen/components IfcLoader
- [ ] Orbit / fly-through / plan camera modes — wired to keyboard shortcuts
- [ ] Snapshot export — capture canvas as PNG and write to lattice/execution/evidence
- [ ] Section plane tool
- [ ] Element selection — click element → show IFC properties panel from ifc_elements row
- [ ] GLTF export button — exports scene for Cinema 4D

---

## ANALYTICAL LAYER (analysis/)

- [ ] deck.gl route — src/routes/analysis/index.tsx
- [ ] ScatterplotLayer — plant positions from ifc_elements Parquet via DuckDB WASM
- [ ] ColumnLayer — plant density by zone
- [ ] HeatmapLayer — irrigation demand overlay
- [ ] MapLibre basemap — self-hosted tiles, no API key
- [ ] DuckDB WASM spatial queries — ST_Within, ST_Distance for zone analysis

---

## POINT CLOUD (pointcloud/)

- [ ] Potree viewer route — src/routes/pointcloud/index.tsx
- [ ] PotreeConverter integration — CLI wrapper in sidecar that converts .las → public/potree/{project_id}/
- [ ] Potree + ThatOpen shared scene — add point cloud to the ThatOpen Three.js scene
- [ ] LiDAR ingest endpoint — POST /v1/ingest/lidar, runs Laspy + PDAL pipeline, writes to lattice/bridge/point_clouds
- [ ] Existing tree extraction — Open3D DBSCAN on vegetation returns, writes to lattice/bridge/existing_trees

---

## VECTORWORKS BRIDGE (vw/)

- [ ] vicquick/vwx-mcp connection — wire vw.* MCP tools to VW bridge agent
- [ ] Layer/class listing — read VW document structure via MCP
- [ ] Plant record extraction — read all Plant Style instances from active document
- [ ] IFC export trigger — command VW to export IFC4.3 via MCP, then auto-ingest
- [ ] C++ plugin scaffold — PlaceholderCmd.cpp, MCPBridge.cpp, GeometryUtils.cpp

---

## PLANT GEOMETRY PIPELINE

- [ ] LOD 100 placeholder creation — one menu button in VW that creates colored spikes for all landscape element categories
- [ ] Placeholder rules config — vw-plugin/config/placeholder_rules.json with category/color/height per AGENTS.md spec
- [ ] Plant Style Manager assignment — never hardcode geometry into instances
- [ ] Plant asset library table — lattice/bridge/plant_assets with species → GLB path mapping
- [ ] Asset swap workflow — replace LOD 100 spike with LOD 300 GLB in ThatOpen viewer

---

## MARIMO / BROWSER AGENT

- [ ] Marimo notebook route or iframe embed
- [ ] DuckDB WASM cells querying Pixeltable Parquet exports
- [ ] ifcmcp embedded (Pyodide) for in-browser IFC manipulation
- [ ] Browser agent — Claude via @tanstack/ai in a Marimo cell

---

## DEVEX / INFRASTRUCTURE

- [x] LATTICE nav rename (TanStack Start → LATTICE) — landed 2026-05-11
- [ ] Auth — wire Better Auth for session management
- [ ] make dev target — single command that starts sidecar + frontend together
- [ ] make restart-sidecar target — kills and restarts with correct PIXELTABLE_HOME
- [ ] Hot reload for sidecar — uvicorn --reload mode (needs PYTHONPATH and PIXELTABLE_HOME set)
- [ ] CI — GitHub Actions: lint + test-no-pxt on every push
- [ ] OpenConstructionERP integration — BOQ linked to ifc_elements via source_element_id

---

## DDC INTEGRATION (data-layer + admin)
# The administrative/cost intelligence layer is as important as the 3D viewer.
# DDC value = the 221 skill patterns + CWICR cost database methods. Not the file converters.

- [ ] OpenConstructionERP BOQ — link every ifc_elements row to a BOQ line item via source_element_id; POST /v1/erp/boq endpoint that calls OpenConstructionERP REST API
- [ ] OpenConstructionERP 4D/5D — schedule phases linked to ifc_elements; timeline view in operator console
- [ ] CWICR cost search — semantic search against 55,719 cost items via Qdrant (OrbStack Ubuntu VM); POST /v1/erp/cost-search endpoint
- [ ] DDC skill patterns — extract all 221 SKILL.md patterns from DDC_Skills repo and index them in Pixeltable lattice/bridge/semantic as agent-callable tools
- [ ] DDC n8n workflow patterns — convert DDC n8n JSON workflow templates into LATTICE FastAPI pipeline equivalents; store as lattice/execution/pipeline_templates
- [ ] Cost overlay in Context B — deck.gl ColumnLayer showing cost-per-element as height; ColorScale driven by CWICR unit costs joined to ifc_elements
- [ ] BOQ export — generate Excel/CSV BOQ from ifc_elements + CWICR costs via OpenConstructionERP export API
- [ ] Quantity takeoff agent — LATTICE agent task that reads ifc_elements, queries CWICR for unit costs, writes BOQ rows, posts results to Evidence
- [ ] Admin dashboard route — src/routes/admin/index.tsx showing: project cost summary, element count by BIS class, BOQ status, schema health, sidecar status
- [ ] Cost-per-zone analysis — PostGIS ST_Within query joining ifc_elements to irrigation/planting zones; output to Parquet for DuckDB WASM

---

## RENDERING CONTEXT A — FULL 3D SCENE (Digital Twin / Cinematic)
# Three.js + React Three Fiber + @thatopen/components 3.4.6 + @thatopen/fragments 3.4.5
# This is the digital twin. Full orbit, fly-through, mesh fidelity, Cinema 4D output.
# NEVER conflate with Context B.

- [ ] ThatOpen viewer route — src/routes/viewer/index.tsx; OrthoPerspectiveCamera + PostproductionRenderer; web-ifc WASM at public/wasm/
- [ ] IFC load from Pixeltable — GET /v1/export/ifc-bytes -> IfcLoader.load(); Fragment cache in Pixeltable as blob column
- [ ] Camera modes — Orbit (default), FirstPerson, Plan view; keyboard shortcuts O/F/P
- [ ] Fly-through path — keyframe-based camera-controls interpolation; record/play path; export as MP4 via canvas capture
- [ ] Snapshot capture — canvas.toDataURL() -> write to lattice/execution/evidence as PNG artifact
- [ ] Section plane tool — horizontal + vertical cut planes; save section state to Pixeltable
- [ ] Element selection + properties panel — click element -> fetch ifc_elements row -> show BIS class, IFC properties, cost data side panel
- [ ] DDC cost data as 3D layer toggle — color-code mesh materials by cost range; toggle button in viewer toolbar; driven by ifc_elements.unit_cost column
- [ ] Plant density as 3D instanced mesh — 700 identical plant meshes as one GPU draw call via Fragment instancing
- [ ] LOD switching — LOD 100 spike visible at distance; LOD 300 GLB mesh at close range; Fragment LOD mode
- [ ] GLTF export — Three.js GLTFExporter -> public/exports/{project_id}.glb; write path to lattice/execution/evidence
- [ ] Cinema 4D handoff — GLTF export with IFC property extras; Y-up meters confirmed; coordinate system notes in meta/CINEMA4D_HANDOFF.md
- [ ] Potree point cloud in shared Three.js scene — potree-core 2.0.15 + ThatOpen renderer sharing one canvas; toggle layer button
- [ ] iTwin geometry types — use @itwin/core-geometry Point3d/Transform for all geometry math in viewer; never raw arrays
- [ ] PostproductionRenderer effects — GTAO ambient occlusion, SMAA, edge highlighting, outline on selected element
- [ ] WebGPU flag — feature-flag opt-in for WebGPU renderer; WebGL2 default; test on Apple Silicon

---

## RENDERING CONTEXT B — ANALYTICAL LAYER (Data / Plans / Site Analysis)
# deck.gl 9.3.2 + luma.gl + loaders.gl + DuckDB WASM + MapLibre
# Georeferenced, data-driven, map-projected. NOT a 3D scene renderer.
# NEVER conflate with Context A.

- [ ] Analytical layer route — src/routes/analysis/index.tsx; deck.gl canvas + MapLibre basemap (react-map-gl/maplibre, no API key)
- [ ] Parquet pipeline — GET /v1/export/ifc_elements -> public/data/ifc_elements.parquet; DuckDB WASM loads it zero-copy
- [ ] ScatterplotLayer — plant positions from ifc_elements; color by bis_subclass; radius by crown_radius_m
- [ ] ColumnLayer — plant density per zone as extruded columns; height = count; color = density
- [ ] HeatmapLayer — irrigation demand overlay; weight = irrigation_demand_l_per_day from ifc_elements
- [ ] PathLayer — site circulation routes from DXF/VW path geometry
- [ ] DDC cost overlay — ColumnLayer with height=unit_cost, color scale red->green; toggled layer
- [ ] DuckDB WASM spatial queries — ST_Within zones, ST_Distance buffers, ST_Intersects; spatial extension loaded in browser
- [ ] Shadow analysis layer — sun angle + element height -> shadow polygon GeoJSON -> GeoJsonLayer
- [ ] Layer toggle panel — sidebar with checkboxes per layer; persisted to TanStack Store
- [ ] Parquet export endpoint — GET /v1/export/{table} returns Parquet for any bridge table; used by both Context B and Marimo
- [ ] Tooltip on hover — deck.gl picking -> show element name, BIS class, cost, species from ifc_elements row
- [ ] Context A<->B shared selection state — clicking element in Context A sets TanStack Store selectedElementId; Context B ScatterplotLayer highlights same element

---

## DATA LAYER — DuckDB WASM + Apache Arrow + Parquet
# Zero-copy pipeline: Pixeltable -> Parquet -> Arrow -> DuckDB WASM -> browser queries
# This feeds BOTH rendering contexts and Marimo notebooks.

- [ ] DuckDB WASM init — load @duckdb/duckdb-wasm 1.33.1, INSTALL spatial, LOAD spatial; singleton worker in src/lib/duckdb.ts
- [ ] Parquet loader — loaders.gl ParquetLoader for Arrow-native zero-copy reads
- [ ] ifc_elements query hook — useDuckDBQuery('SELECT * FROM ifc_elements WHERE bis_subclass = ?') custom hook
- [ ] Plant density query — GROUP BY zone_id, COUNT(*) with ST_Within spatial join
- [ ] Cost summary query — SUM(unit_cost * quantity) GROUP BY bis_subclass
- [ ] Marimo notebook DuckDB cells — notebook reads same Parquet files; agent manipulates data in browser
- [ ] Arrow IPC streaming — sidecar streams Arrow IPC format for large tables instead of full Parquet download

---

## C++ VECTORWORKS PLUGIN — Menu Button + Geometry Actuator
# vw-plugin/src/ — VWSDK, Mac + Windows build targets
# This is the physical geometry creation layer. Without this, nothing exists in 3D.

- [ ] Plugin scaffold — CMakeLists.txt, VWSDK linkage, Mac + Windows build targets in vw-plugin/
- [ ] PlaceholderCmd.cpp — single menu button "Generate LATTICE Placeholders" that reads all landscape elements from the active document and creates LOD 100 placeholder geometry for every category
- [ ] Placeholder geometry per category — cone/sphere/disc/box per AGENTS.md spec; color from placeholder_rules.json; height from placeholder_rules.json
- [ ] placeholder_rules.json — vw-plugin/config/; all category/color/height rules; Claude-editable via MCP without recompile
- [ ] MCPBridge.cpp — Unix socket IPC to MCP server; sends PlaceholderCreated events to LATTICE sidecar
- [ ] GeometryUtils.cpp — parametric shape builders: cone, hemisphere, disc, box, ellipsoid, slab
- [ ] Plant Style Manager assignment — all placeholder geometry assigned to Plant Style, never individual instances; swapping style updates all instances globally
- [ ] Menu command: Export IFC — triggers VW IFC4.3 export then auto-POSTs to /v1/ingest/ifc
- [ ] Menu command: Sync to LATTICE — reads current document state, writes all records to sidecar via MCP bridge
- [ ] Menu command: Load Plant Assets — reads lattice/bridge/plant_assets from Pixeltable, populates VW Plant Style Manager with available GLB assets

---

## PLANT GEOMETRY PIPELINE
# LOD 100 -> LOD 300. Spikes first, botanical meshes second.
# Plant Style Manager is the single point of control for all instances.

- [ ] Plant asset library — lattice/bridge/plant_assets table: species_code, common_name, glb_path, lod_level, crown_radius_m, height_m, source (manual/laubwerk/blender)
- [ ] LOD 100 spike creation — PlaceholderCmd generates spike per AGENTS.md spec; data complete before geometry is realistic
- [ ] LOD 300 GLB import — Plant Style Manager UI in VW: browse plant_assets table, select species, assign GLB; all instances update globally
- [ ] Asset swap in ThatOpen — Fragment edit API: replace LOD 100 spike geometry with LOD 300 GLB for selected plant type
- [ ] Procedural Blender pipeline — Blender Python script that generates parametric tree/shrub mesh from species parameters; outputs GLB to plant_assets store
- [ ] Species matching agent — LATTICE agent task: given plant name from VW record, find best matching asset in plant_assets; if none, flag for creation
- [ ] Plant categories covered — ground cover, shrubs, perennials, flowers, proposed trees, existing trees, boulders, pool, stepping stones, flagstones, fencing, gates, outdoor kitchen, outdoor furniture

---

## iTWIN OPEN-SOURCE LAYER (Self-Hosted, BIS Vocabulary + Geometry Types)
# @itwin/core-geometry 5.9.2 + @itwin/core-common 5.9.2
# BIS class names are column values in Pixeltable. No Bentley cloud. No core-backend.

- [ ] BIS vocabulary constants — src/lib/bis-constants.ts mapping all LATTICE landscape element types to BIS class/subclass strings
- [ ] @itwin/core-geometry usage — use Point3d, Transform, Arc3d for all geometry math in viewer and plant geometry pipeline; never raw float arrays
- [ ] .bim source ingestion — @pxt.udf SQLite reader for .bim files; merge ECInstanceId/ECClassId/UserLabel/JsonProperties into lattice/bridge/ifc_elements
- [ ] BIS schema validation — check bis_class + bis_subclass on every ifc_elements insert; log warnings for unmapped types
- [ ] iTwin geometry in C++ plugin — use @itwin/core-geometry equivalent C++ types (Bentley DGNPlatform geometry) for precise placement math in VW plugin

---

## MARIMO + BROWSER AGENT EXTENDED

- [ ] Marimo server — `marimo serve` as a separate process; route in LATTICE at /notebooks; iframe or dedicated tab
- [ ] DuckDB WASM in Marimo cells — same Parquet files as Context B; zero-copy via mo.sql() DuckDB cells
- [ ] Agent in browser — Claude via @tanstack/ai in a reactive Marimo cell; can read ifc_elements, trigger agent runs, inspect evidence
- [ ] ifcmcp embedded (Pyodide WASM) — in-browser IFC manipulation via IfcOpenShell compiled to WASM; plant element queries without sidecar roundtrip
- [ ] Notebook templates — starter notebooks for: plant quantity takeoff, cost analysis, shadow analysis, point cloud stats

---

## CINEMA 4D + REDSHIFT PIPELINE

- [ ] GLTF handoff — ifcconvert or Three.js GLTFExporter -> .glb; Y-up meters; IFC properties in extras
- [ ] Cinema 4D import guide — meta/CINEMA4D_HANDOFF.md: coordinate system, scale, material mapping from IFC type to C4D material
- [ ] Redshift material library — starter material set for landscape: grass, bark, stone, water, concrete, wood
- [ ] Render output evidence — PNG/EXR renders written back to lattice/execution/evidence via drag-drop or watched folder
- [ ] Fly-through -> Cinema 4D camera — export ThatOpen fly-through keyframes as FBX camera animation for Cinema 4D

---

## CESIUM GLOBE — MARPA PROJECT PORTFOLIO VIEW
# /globe route — CesiumJS globe with all MARPA projects georeferenced on real terrain.
# Click project pin -> lazy-load iTwin IFC model draped at correct lat/lon.
# deck.gl analytical layers float on top as toggleable overlays.
# This is the executive dashboard AND the field operations view.

### Core Globe Setup
- [ ] CesiumJS route — src/routes/globe/index.tsx; Cesium globe with terrain (Cesium World Terrain or self-hosted Cesium ion)
- [ ] Self-hosted Cesium option — evaluate cesium-terrain-builder + quantized-mesh tiles to avoid Cesium ion dependency; document in meta/CESIUM_SETUP.md
- [ ] MARPA project registry — lattice/bridge/marpa_projects Pixeltable table: project_id, name, address, lat, lon, status (active/complete/prospect), phase, project_manager, start_date, end_date, ifc_path, thumbnail_url
- [ ] Project pins on globe — CesiumJS entity per MARPA project; color by status (green=active, blue=complete, yellow=prospect); label = project name
- [ ] Lazy load on click — click project pin -> load only that project's IFC/Fragment model; unload previous project on navigation away; never load all projects simultaneously
- [ ] Fly-to animation — smooth CesiumJS camera fly-to on project select; configurable flight duration
- [ ] Project info card — sidebar panel showing project name, phase, PM, schedule status, thumbnail on pin click

### iTwin Georeferenced Overlay
- [ ] iTwin model draped on terrain — position IFC model at project lat/lon/elevation using @itwin/core-geometry Transform; align to real-world north
- [ ] ThatOpen Fragment loader in globe context — load .frag model at georeferenced position over Cesium terrain
- [ ] Coordinate system bridge — convert between Cesium ECEF/WGS84 and iTwin/IFC local coordinate systems via IfcSite georeferencing matrix; write transform util to src/lib/geo-transform.ts
- [ ] LOD by camera distance — show project pin at globe scale; switch to IFC model when camera within 500m; switch to full Fragment detail within 100m
- [ ] Multiple projects visible simultaneously — if zoomed to city scale, show all project pins; if zoomed to neighborhood, show simplified IFC outlines for nearby projects

### deck.gl Analytical Layers on Globe
- [ ] Task status layer — deck.gl IconLayer at each project position; icon = checkmark/clock/warning based on Linear/project status
- [ ] Schedule progress layer — ColumnLayer extruded by % complete; color = on-track (green) / delayed (red) / complete (grey)
- [ ] Cost layer — ScatterplotLayer radius = total project value; color = under/over budget from DDC BOQ
- [ ] Phase layer — GeoJsonLayer showing project site boundary polygon per project; fill opacity by phase
- [ ] Layer toggle panel — sidebar checkboxes to show/hide each analytical layer; state persisted to TanStack Store

### Project Management Integration
- [ ] Linear sync — pull Linear project/issue status into marpa_projects via LINEAR_WEBHOOK_URL; update task_count, open_issues, last_activity columns
- [ ] DDC admin overlay — per-project BOQ status, estimated vs actual cost, quantity takeoff progress from OpenConstructionERP
- [ ] Schedule timeline — click project -> show Gantt-style mini timeline in sidebar using project phase dates
- [ ] Photo/document evidence — project photos and key documents stored in lattice/execution/evidence with project_id FK; thumbnail gallery in project info card
- [ ] Field status updates — mobile-friendly view at /globe/field that shows current project with large status buttons (on-site/off-site, today's tasks, issues to flag)

### Lazy Loading + Performance
- [ ] Fragment cache per project — .frag binary cached in Pixeltable as blob column; check cache before re-converting IFC; invalidate on IFC update
- [ ] Tile-based project loading — only fetch projects within current Cesium camera frustum + 20% buffer; unload projects outside 2x frustum
- [ ] Progressive detail — project loads in 3 stages: (1) pin only, (2) site boundary polygon, (3) full IFC Fragment model
- [ ] Web Worker for Fragment loading — load .frag bytes off main thread; post to main thread when ready; prevent globe camera jank during load

### MARPA Project Data Seed
- [ ] Seed script — scripts/seed-marpa-projects.ts that reads a CSV/JSON of MARPA project locations and POSTs to /v1/ingest/marpa-projects
- [ ] Project thumbnail generation — capture ThatOpen snapshot of each loaded IFC model and store as project thumbnail in Pixeltable
- [ ] Historical projects — completed projects shown with greyed-out pins and archive badge; accessible for reference and portfolio
- [ ] Prospect projects — show prospect pins with dashed boundary; click -> show proposal status and estimated value from OpenConstructionERP

---

## PIXELTABLE EXTENDED SCHEMA (migration 0012)
# ALL data has a PostGIS location. ALL BIM data has BIS classification.
# Migration 0012 applied 2026-05-11; this section tracks downstream work.

- [x] Migration 0012 — applied: PostGIS-ish columns on ifc_elements, marpa_projects, site_zones, reference_images, plant_assets, comfyui_jobs, model_registry, training_runs
- [ ] ifc_elements WKT geometry — populate `geom_point_wkt` from VW IFC export + IfcSite georeferencing; backfill existing rows
- [ ] ifc_elements BIS columns — populate `bis_class` / `bis_subclass` via IfcOpenShell type mapping (see `itwin/bis-schemas/`)
- [ ] ifc_elements DDC admin columns — populate from BOQ adapter (cross-references the DDC integration section)
- [ ] PostGIS spatial extension at the PG layer — `CREATE EXTENSION IF NOT EXISTS postgis` in a sidecar startup hook
- [ ] WKT-to-PostGIS computed columns — once the extension is on, add `geom_point geometry` computed from `ST_GeomFromText(geom_point_wkt, 4326)`
- [ ] Spatial join computed column — `ST_Within(ifc_elements.geom_point, site_zones.geom_polygon)` resolves `site_zone_id`
- [ ] marpa_projects seed script — see `scripts/seed-marpa-projects.ts` + Cesium section
- [ ] site_zones authoring UI — `/admin` panel to draw zone polygons on the Cesium globe; writes `geom_polygon_wkt`
- [ ] reference_images embedding — Pixeltable computed column with a vision embedding model

---

## 3D PLANT ASSET CREATION PIPELINE
# geo-tagged reference image -> ComfyUI -> GLB -> VW Plant Style Manager -> Cesium pin
# See genai/3d-asset-pipeline/PIPELINE.md for the full diagram.

- [ ] Reference image collection UI — `/globe` map pin drop + photo upload -> `lattice/bridge/reference_images`
- [ ] Species matching via spatial proximity — nearest `ifc_elements` row via `ST_DWithin` on the photo's `geom_point_wkt`
- [ ] ComfyUI job dispatch — Pixeltable trigger when `enough_images_for_species(species_code) >= 3` -> insert into `lattice/genai/comfyui_jobs`
- [ ] ComfyUI dispatcher process — `genai/comfyui/job-dispatcher.py` polls pending rows, runs workflow, writes output paths back
- [ ] GLB conversion — output mesh -> `assets/plants/lod-300/{species_code}.glb`
- [ ] Cinema 4D project skeleton — `genai/3d-asset-pipeline/c4d-exporter.py` writes `assets/plants/c4d/{species_code}.c4d` with Redshift materials assigned
- [ ] VW Plant Style assignment — `vw-style-importer.py` pushes the GLB to VW Plant Style Manager via `vwx-mcp` -> all instances update globally
- [ ] Pixeltable cascade trigger — when `comfyui_jobs.status='complete'`, update `plant_assets.lod_300_glb` + `ifc_elements.asset_id`
- [ ] ThatOpen LOD swap — Fragment edit API replaces LOD100 spike geometry with new GLB on next viewer reload
- [ ] Cesium pin thumbnail — capture ThatOpen snapshot of new asset, write to `marpa_projects.thumbnail_url`
- [ ] Quality review gate — present generated assets in `/admin` for human score (`quality_score >= 0.7`) before promoting to VW

---

## LOCAL AI / GENAI / GEOAI / ML
# All models run locally on Apple Silicon. The model router picks per task.

- [ ] Ollama install + 4 models — llama3.3:70b, qwen2.5-coder:32b, mistral-nemo:12b, nomic-embed-text
- [ ] Model registry sync — `genai/llm/model-router.py --sync-registry` populates `lattice/genai/model_registry` from `ollama list`
- [ ] Model router runtime — `genai/llm/model-router.py route()` picks per task type, falls back to `claude -p` for unrouted complex tasks
- [ ] ComfyUI install on Apple Silicon — MPS backend, listen on `:8188`
- [ ] ComfyUI plant-2d-to-3d workflow — 3-6 reference images -> textured 3D mesh
- [ ] ComfyUI tree-crown-gen workflow — species params -> procedural crown texture
- [ ] ComfyUI texture-from-photo workflow — site photo -> tiling PBR texture set
- [ ] ComfyUI Python client — `genai/comfyui/comfyui-client.py` wraps `/prompt`, `/history/{id}`, websocket progress
- [ ] GeoAI tree detection — detect crowns from LiDAR + orthophoto -> write to future `lattice/bridge/existing_trees`
- [ ] GeoAI species classifier — classify plant species from reference photos -> write `reference_images.species_tag`
- [ ] GeoAI shadow segmentation — shadow polygons from orthophoto -> deck.gl `GeoJsonLayer` in `/analysis`
- [ ] ML training pipeline — `genai/geoai/tree-detection/train.py` fine-tunes on MARPA project data, writes `lattice/genai/training_runs`
- [ ] Pixeltable text embedding column — nomic-embed-text on `ifc_elements.user_label || ' ' || bis_subclass`
- [ ] Pixeltable image embedding column — CLIP-like model on `reference_images.image` for visual similarity search
- [ ] Local inference endpoint — `POST /v1/genai/infer` on the sidecar, routes via the model registry
- [ ] Browser agent in Marimo — `@tanstack/ai` connector pointing at local Ollama (no API key)
