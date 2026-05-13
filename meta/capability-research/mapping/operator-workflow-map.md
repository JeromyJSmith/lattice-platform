# Operator Workflow Map

Connects capability registry rows to concrete operator workflow stages.
This is the MAP step — the missing artifact that links "what we can do" to "when the operator needs it."

## Schema

Each entry covers one operator trigger with the full capability chain it activates.

| Field | Meaning |
|---|---|
| `operator_trigger` | What the operator does in Vectorworks or the UI to start the workflow |
| `selected_object_input` | What object/selection the operator acts on |
| `pixeltable_lookup` | Which Pixeltable table(s) the step reads or writes |
| `service_or_adapter` | FastAPI endpoint, MCP tool, or sidecar function involved |
| `panel_output` | What the operator sees in the TanStack/deck.gl panel |
| `editable_fields` | Which fields the operator can change in the panel |
| `evidence_required` | Registry row IDs whose proof must be ACTIVE for this stage |
| `runtime_destination` | Where the output lands (table + field) |

---

## Stage 1 — Planting Plan Ingestion

**operator_trigger**: Export IFC4.3 from Vectorworks Landmark → drop `.ifc` to `drop-zone/`

**selected_object_input**: Entire planting plan layer (all IfcPlant symbols)

**pixeltable_lookup**: `lattice/bridge/ifc_elements` (write)

**service_or_adapter**:
- `POST /v1/ingest/ifc` (pixeltable/service/routes/ingest.py)
- IfcOpenShell `ifcopenshell.open()` → `util.placement` for coordinate normalization
- `@pxt.udf` row insert

**panel_output**: Plant inventory table (species, count, EPSG-normalized lat/lon, BIS class)

**editable_fields**: `user_label`, `bis_subclass`, `ifc_class`

**evidence_required**:
- `ifc-ingest / ifc-open-model` (IfcOpenShell open)
- `ifc-ingest / ifc-coordinate-normalize` (EPSG normalization)
- `pixeltable-bridge / pxt-insert-ifc-elements`

**runtime_destination**: `lattice/bridge/ifc_elements` (project_id, source_element_id, ifc_class, bis_subclass, user_label, latitude, longitude, placement_matrix, vw_export_hash)

---

## Stage 2 — Point Cloud Registration

**operator_trigger**: Drag `.laz` / `.las` file into `drop-zone/`

**selected_object_input**: Raw point cloud file

**pixeltable_lookup**: `lattice/bridge/point_clouds` (write)

**service_or_adapter**:
- `POST /v1/ingest/pointcloud` (pixeltable/service/routes/ingest.py)
- PDAL pipeline: reproject → classify → tile
- PotreeConverter for browser tile generation
- Open3D DBSCAN for existing tree extraction

**panel_output**: Potree viewer overlay in TanStack panel; extracted tree centroids on deck.gl ScatterplotLayer

**editable_fields**: EPSG code override, classification filter, tree-extraction radius

**evidence_required**:
- `point-cloud / pdal-reproject`
- `point-cloud / open3d-dbscan-extract`
- `point-cloud / potree-tile-generate`
- `pixeltable-bridge / pxt-insert-point-cloud`

**runtime_destination**: `lattice/bridge/point_clouds` (tile_manifest, epsg, classification_counts), `lattice/bridge/existing_trees` (centroid_wkt, species_estimate, height_m)

---

## Stage 3 — Plant Style Placeholder Creation

**operator_trigger**: Click "Create placeholders" in TanStack harness panel after ingestion

**selected_object_input**: Rows in `lattice/bridge/ifc_elements` where `bis_subclass LIKE 'Landscape:Plant%'`

**pixeltable_lookup**: `lattice/bridge/ifc_elements` (read)

**service_or_adapter**:
- `POST /v1/vw/create-placeholder` (pixeltable/service/routes/vw.py)
- VW MCP bridge TCP `:9878` → vw.create_placeholder()
- Plant Style Manager lookup (not per-instance geometry)

**panel_output**: Progress toast + updated plant inventory with placeholder status column

**editable_fields**: Plant style override per species group

**evidence_required**:
- `vw-bridge / vw-ping`
- `vw-bridge / vw-create-placeholder`
- `vw-bridge / vw-plant-style-manager`

**runtime_destination**: `lattice/execution/evidence` (event_type=placeholder_created, object_ids)

---

## Stage 4 — IFC Enrichment + Georeferencing

**operator_trigger**: Click "Enrich IFC" after placeholder creation completes

**selected_object_input**: `.ifc` file in `drop-zone/` or last export path

**pixeltable_lookup**: `lattice/bridge/ifc_elements` (read, update georef fields)

**service_or_adapter**:
- `POST /v1/ifc/enrich` (pixeltable/service/routes/ifc.py)
- ifcmcp: `ifc.set_3d_representation`, `ifc.set_georeferencing`
- smartaec/ifcMCP: spatial validation queries

**panel_output**: Georeferenced IFC preview in ThatOpen viewer; validation report panel

**editable_fields**: Site origin EPSG, true north angle, CRS override

**evidence_required**:
- `ifc-enrich / ifc-set-3d-representation`
- `ifc-enrich / ifc-set-georeferencing`
- `ifc-enrich / ifc-spatial-validate`

**runtime_destination**: `lattice/bridge/ifc_elements` (ifc_version=IFC4.3, georef_epsg, georef_origin_wkt updated)

---

## Stage 5 — Reality Capture Deviation Analysis

**operator_trigger**: Click "Compare to point cloud" after both IFC and point cloud are ingested

**selected_object_input**: Paired IFC elements + point cloud session from `lattice/bridge/`

**pixeltable_lookup**: `lattice/bridge/point_clouds`, `lattice/bridge/ifc_elements`, `lattice/bridge/cloud_comparisons` (write)

**service_or_adapter**:
- `POST /v1/reality/compare` (pixeltable/service/routes/reality.py)
- CloudComPy C2C distance analysis
- Open3D ICP registration

**panel_output**: Deviation heatmap layer on deck.gl; volume delta report in side panel

**editable_fields**: Deviation threshold (m), comparison sampling rate

**evidence_required**:
- `reality-capture / cloudcompy-c2c`
- `reality-capture / open3d-icp-registration`
- `pixeltable-bridge / pxt-insert-cloud-comparison`

**runtime_destination**: `lattice/bridge/cloud_comparisons` (c2c_distance_stats, volume_delta_m3, report_path)

---

## Stage 6 — GenAI Proposal Review

**operator_trigger**: Autoresearch cycle fires via `run-autoresearch.sh` or operator clicks "Propose improvements"

**selected_object_input**: Section GOAL.md + current score from scoring script

**pixeltable_lookup**: `lattice/execution/briefs` (write), `lattice/genai/completions` (write)

**service_or_adapter**:
- `POST /v1/harness/proposals` (pixeltable/service/routes/harness.py)
- `claude -p` subprocess in pixeltable/service/worker.py
- Ratchet gate: score_after > score_before → accept

**panel_output**: Diff viewer in harness UI; accept/reject buttons; ratchet score timeline chart

**editable_fields**: Proposal text (manual edit before accept), section target override

**evidence_required**:
- `meta-harness / autoresearch-ratchet`
- `meta-harness / proposal-diff-apply`
- `claude-code-sidecar / claude-p-subprocess`

**runtime_destination**: `lattice/execution/briefs` (diff, score_before, score_after, accepted), `lattice/genai/completions` (prompt, completion, model_id)

---

## Stage 7 — DDC / iTwin Panel Sync

**operator_trigger**: Click "Sync to iTwin" after IFC enrichment is complete

**selected_object_input**: Enriched IFC elements in `lattice/bridge/ifc_elements`

**pixeltable_lookup**: `lattice/bridge/ifc_elements` (read)

**service_or_adapter**:
- `POST /v1/ddc/sync` (pixeltable/service/routes/ddc.py)
- `@itwin/core-geometry` BIS geometry conversion
- OpenConstructionERP integration (CWICR handoff)

**panel_output**: iTwin viewer in TanStack panel (ThatOpen renderer); CWICR export confirmation

**editable_fields**: Export scope (by layer/class), BIS class override

**evidence_required**:
- `itwin-bridge / itwin-geometry-convert`
- `ddc / cwicr-export`
- `pixeltable-bridge / pxt-read-ifc-elements`

**runtime_destination**: DDC export artifact (GLTF/GLB at `exports/<project_id>/<timestamp>.glb`), iTwin changeset record

---

## Capability Row → Stage Cross-Reference

| Registry | Row ID | Stage(s) |
|---|---|---|
| ifc-ingest | ifc-open-model | 1 |
| ifc-ingest | ifc-coordinate-normalize | 1 |
| point-cloud | pdal-reproject | 2 |
| point-cloud | open3d-dbscan-extract | 2 |
| vw-bridge | vw-create-placeholder | 3 |
| ifc-enrich | ifc-set-georeferencing | 4 |
| reality-capture | cloudcompy-c2c | 5 |
| meta-harness | autoresearch-ratchet | 6 |
| ddc | cwicr-export | 7 |
