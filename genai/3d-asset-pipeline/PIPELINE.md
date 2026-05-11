# 3D Plant Asset Pipeline — Step by Step

```
┌────────────────────────────────────────────────────────────────────────┐
│                          /globe Cesium map                              │
│                                                                          │
│  Operator drops a pin at a plant location + uploads 3-6 site photos    │
└────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼  POST /v1/ingest/reference-image
┌────────────────────────────────────────────────────────────────────────┐
│  Pixeltable: lattice/bridge/reference_images                           │
│  - image  (pxt.Image — encoded inline)                                  │
│  - longitude, latitude, geom_point_wkt                                  │
│  - species_tag  (filled by GeoAI species-classifier when confident)     │
└────────────────────────────────────────────────────────────────────────┘
                              │
                              │  Pixeltable computed-column trigger:
                              │  enough_images_for_species(species_code) >= 3
                              ▼
┌────────────────────────────────────────────────────────────────────────┐
│  Pixeltable: lattice/genai/comfyui_jobs   status='pending'             │
└────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼  job-dispatcher.py polls
┌────────────────────────────────────────────────────────────────────────┐
│  ComfyUI server @ localhost:8188                                        │
│  workflow: plant-2d-to-3d.json                                          │
│  input: 3-6 reference images + species hint                             │
│  output: textured 3D mesh -> mesh-generator.py converts to GLB          │
└────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼  c4d-exporter.py
┌────────────────────────────────────────────────────────────────────────┐
│  Cinema 4D project skeleton at  assets/plants/c4d/{species_code}.c4d   │
│  Redshift materials pre-assigned from materials/landscape/              │
└────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼  Write GLB path back to PXT
┌────────────────────────────────────────────────────────────────────────┐
│  Pixeltable: lattice/bridge/plant_assets                                │
│  - lod_300_glb  = "assets/plants/lod-300/{species_code}.glb"            │
│  - lod_300_c4d  = "assets/plants/c4d/{species_code}.c4d"                │
│  - asset_source = "comfyui"                                              │
│  - is_custom    = true                                                   │
└────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼  Human review via /admin quality-reviewer.py
                              │  (score >= threshold to promote)
                              ▼
┌────────────────────────────────────────────────────────────────────────┐
│  vw-style-importer.py → vwx-mcp → VW Plant Style Manager                │
│  - Updates the style record for species_code                            │
│  - ALL instances in the active document update globally                 │
│  - LOD100 spike geometry is replaced by LOD300 mesh                     │
└────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼  In ThatOpen viewer:
┌────────────────────────────────────────────────────────────────────────┐
│  Fragment edit API replaces spike geometry with new GLB on next reload  │
│  Cesium globe pin thumbnail captured from ThatOpen snapshot             │
│  Update marpa_projects.thumbnail_url                                    │
└────────────────────────────────────────────────────────────────────────┘
```

Every step writes evidence to `lattice/execution/evidence` with `tool` tagged by stage (`comfyui.dispatch`, `c4d.export`, `vw.style-import`, etc.) so the entire chain is auditable in `/admin`.

The pipeline is **never automatic past the quality review gate**. Generated assets must be scored by a human in `/admin` before they're pushed to VW. That gate is there because a bad mesh assigned globally would corrupt every drawing it's loaded into.
