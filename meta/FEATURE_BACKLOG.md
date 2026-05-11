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
