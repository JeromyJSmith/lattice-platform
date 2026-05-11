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
