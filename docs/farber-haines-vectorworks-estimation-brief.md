# Farber-Haines Vectorworks Estimation Brief

Date: 2026-05-16

## Objective

Build and validate the Farber-Haines Vectorworks-to-estimating workflow:

- map model classes and objects to budget pricing
- expose quantity-driven cost data in Vectorworks and worksheets
- define the 3D plant asset workflow
- define the IFC and georeference export path into the downstream stack
- prepare a meeting-ready focus for Henry on the Vectorworks-to-spreadsheet loop

## Proven Now

### 1. Budget-to-Vectorworks pricing loop

Source model:

- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/projects/vectorworks project files/_Farber-Haines [2521].vwx`
- active destructive-safe working copy:
  - `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/projects/vectorworks project files/_Farber-Haines [2521]__ESTIMATION_WORKING_COPY__2026-05-16.vwx`

Source budget:

- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/MARPA_CONSTRUCTION_ESTIMATING 2/2026-04.22_Farber-Haines_SD_Budget1 copy.xlsx`

Applied tooling:

- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/vw-python/examples/apply_estimation_mapping_csv.py`
- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/vw-python/examples/export_project_cost_summary.py`
- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/vw-python/examples/export_project_cost_object_rows.py`
- whole-file working-copy runners:
  - `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/vw-python/examples/run_farber_haines_apply_estimation_working_copy.py`
  - `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/vw-python/examples/run_farber_haines_export_cost_summary_working_copy.py`
  - `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/vw-python/examples/run_farber_haines_export_cost_object_rows_working_copy.py`
- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/vw-python/examples/scan_class_price_info.py`
- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/pixeltable/scripts/ingest_farber_haines_estimates.py`
- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/pixeltable/scripts/ingest_farber_haines_georef.py`
- operator sequence:
  - `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/docs/farber-haines-working-copy-operator-sequence.md`

Validation artifacts:

- `/Users/ojeromyo/Desktop/vw_cost_lookup_active_apply.csv`
- `/Users/ojeromyo/Desktop/vw_cost_estimate_summary.csv`
- `/Users/ojeromyo/Desktop/vw_class_price_scan.csv`

Current status:

- the copied VWX is now the primary destructive-safe operator surface
- `Project Cost` record is being written onto mapped objects
- count-based rows (`ea`) are validated
- area-based rows (`sf`) are validated at the current script level
- linear rows (`lf` / `ff`) are now converted from Vectorworks raw inches to linear feet before pricing
- volume and mass rows (`yd`, `cy`, `ton`) are intentionally held as `Manual Review`

Representative validated outputs from `vw_cost_estimate_summary.csv`:

| Class | Unit | Quantity | Unit Cost | Total Cost |
| --- | --- | ---: | ---: | ---: |
| `L-Plant-Proposed` | `ea` | 17.0 | 49 | 833.0 |
| `L-Tree-Proposed` | `ea` | 20.0 | 930 | 18600.0 |
| `L-Drainage-Area Drain` | `ea` | 9.0 | 500 | 4500.0 |
| `L-Fence-Proposed 3'H` | `lf` | 72.0 | 55 | 3952.0 |
| `L-Fence-Proposed 6'H` | `lf` | 732.0 | 64 | 46773.0 |
| `L-Wall-Proposed` | `lf` | 224.0 | 374 | 83537.0 |

Known gap:

- some linear classes still return `0.0` because their geometry is not exposed through simple `vs.HLength()` calls and need object-type-specific extraction logic

### 1c. Georef solve path is now fail-closed

The selected-reference export and fit-apply path are now hardened so stale or
synthetic georef artifacts cannot be promoted silently.

Current safeguards:

- the Vectorworks selected-reference export now stamps:
  - source VWX path
  - source VWX basename
  - export timestamp
  - export version
  - object-signature hash
- the selected-to-authoritative matcher rejects payloads that:
  - are not marked as real Vectorworks selected-reference exports
  - do not point to a real `.vwx` file on disk
  - look synthetic or mock-derived
  - declare a selected count that does not match the object list
- the fit-apply script refuses to write into `lattice.bridge.project_georef`
  unless the fit passes quality thresholds:
  - `rmse <= 5.0`
  - `max_residual <= 15.0`

What this means operationally:

- the current georef blocker is now honestly narrowed to one thing:
  a real selected-reference export from the active Farber-Haines working copy
- once that export exists, the post-export runner and cycle runner are ready to
  process it without the old packaging failure or synthetic-data footgun

### 1b. Pixeltable landing is now live

Verified writes on 2026-05-16:

- `lattice/bridge/project_georef`
  - inserted rows for `project_id = farber-haines-2521`: `1`
- `lattice/projects/farber-haines-2521/vw_estimate_rows`
  - inserted rows: `33`
- `lattice/projects/farber-haines-2521/vw_estimate_objects`
  - inserted rows: `313`

What those tables currently represent:

- `project_georef` holds the first provisional Farber-Haines parcel-corner georef seed from GROVE control points
- `vw_estimate_rows` holds the grouped `vw_cost_estimate_summary.csv` data now proven in Pixeltable
- `vw_estimate_objects` now holds the object-level Project Cost export from the active VWX

Important constraint:

- the current Pixeltable estimate landing is honest about granularity
- grouped class-level summary is in Pixeltable now
- object-level estimate rows are now in Pixeltable with Vectorworks object UUIDs
- object-level estimate rows still cannot be safely merged into `ifc_elements` until the Vectorworks object UUID to IFC GlobalId crosswalk is proved
- the current IFC probe only contains `IfcProject` and `IfcSite`, so there is not yet an IFC-side element population rich enough to test that crosswalk honestly

### 2. Class and mapping coverage

- `435` classes were exported from the Farber-Haines file
- `54` classes have a first-pass budget mapping
- `33` grouped summary rows are currently represented in the active estimate export

## Plant 3D Workflow

### Working-copy strategy

For this project we do not need a second sandbox design layer unless a specific
experiment benefits from it. The copied VWX file is the safe destructive
boundary:

1. open `_Farber-Haines [2521]__ESTIMATION_WORKING_COPY__2026-05-16.vwx`
2. run pricing, class updates, plant-style edits, and export tests directly in that file
3. preserve the architect-provided `_Farber-Haines [2521].vwx` as the untouched baseline

That is cleaner than duplicating geometry into a sandbox layer because it avoids
double-counting risks in worksheets and keeps all experimental edits contained in
one disposable working document.

### Vectorworks-native path

The current Vectorworks 2026 contract is style-driven, not instance-driven:

- Plant Style Manager is the batch control surface
- 2D and 3D plant graphics belong to the plant style
- editing or replacing style graphics affects all instances using that style

Relevant docs:

- `/Users/ojeromyo/.vectorworks-docs/docs/vw-help/2026_eng_VW2026_Guide_Plants1_Plant_Style_Manager.htm.md`
- `/Users/ojeromyo/.vectorworks-docs/docs/vw-help/2026_eng_VW2026_Guide_Plants1_Replacing_plant_style_graphics.htm.md`
- `/Users/ojeromyo/.vectorworks-docs/docs/vw-help/2026_eng_VW2026_Guide_Plants1_Editing_plant_style_graphics.htm.md`

Recommended production path:

1. Use Plant Style Manager as the hub.
2. Batch replace 3D graphics for selected plant styles.
3. Keep Top/Plan graphics stable for documentation clarity.
4. Use one of four 3D sources per style:
   - generated 3D graphics
   - Maxon plant graphics
   - existing 3D model
   - image prop from image

### Fast placeholder option

For immediate 3D visibility and location QA:

1. Create a tiny centered 3D marker or pin symbol.
2. Use `Replace 3D Graphics` with `Existing 3D Model`.
3. Apply across selected plant styles in Plant Style Manager.

This gives reliable 3D presence and coordinate visibility even before final plant meshes exist.

### Final asset option

For presentation or rendering quality:

1. Prepare a plant-specific GLB or 3D symbol.
2. Replace the style's 3D graphic with that model.
3. Use style-level replacement so all instances update together.

### Local image-to-3D lane

The local plant asset pipeline already exists outside this repo:

- `/Volumes/PixelTable/MARPA_918_JUNIPER`

Evidence of the active mesh/asset lane:

- `pyproject.toml` includes `trimesh`
- viewer and GLB placement surfaces exist under `/Volumes/PixelTable/MARPA_918_JUNIPER/viewer/`
- project extraction code already emits mesh and GLTF artifacts under `/Volumes/PixelTable/MARPA_918_JUNIPER/src/python/extract/phase1_extract.py`

Recommended workflow:

1. collect accurate plant reference image
2. run local image-to-3D generation in the `MARPA_918_JUNIPER` lane
3. review mesh / GLB quality
4. import or convert to a VW-usable 3D symbol
5. batch replace plant style 3D graphics in the active VW file

## IFC and Georeference Export Path

### Vectorworks IFC contract

Relevant docs:

- `/Users/ojeromyo/.vectorworks-docs/docs/vw-help/2026_eng_VW2026_Guide_IFC_Workflow_IFC_export.htm.md`
- `/Users/ojeromyo/.vectorworks-docs/docs/vw-help/2026_eng_VW2026_Guide_Georeference_Specifying_document_georeferencing.htm.md`
- `/Users/ojeromyo/.vectorworks-docs/docs/vw-help/2026_eng_VW2026_Guide_Georeference_Specifying_design_layer_georeferencing.htm.md`

Working-copy runners now exist for the export-readiness path:

- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/vw-python/examples/run_farber_haines_georef_audit_working_copy.py`
- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/vw-python/examples/run_farber_haines_georef_dryrun_working_copy.py`
- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/vw-python/examples/run_farber_haines_ifc_assignment_audit_working_copy.py`
- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/vw-python/examples/run_farber_haines_ifc_probe_working_copy.py`

Vectorworks guidance that matters here:

- use layers for story or major export structure, classes for categorization
- use Data Manager to attach IFC entities and PSets where objects do not already have them
- verify layer elevations and vertical alignment
- verify phasing if phasing is in use
- verify exports in an IFC viewer after export

### Local automation already present

Read-only georef and IFC audit tools:

- `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/vw_plugins/audit_georeference.py`
- `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/vw_plugins/audit_ifc_assignment.py`

Controlled georef apply tool:

- `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/vw_plugins/apply_document_georef.py`

IFC export trigger in this repo:

- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/vw-python/examples/export_ifc_trigger.py`

Georeference CRS assets:

- `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/georef/crs/epsg_2876.wkt`
- `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/georef/crs/epsg_3857.wkt`
- `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/georef/document_georef_binding.json`

### Live Farber-Haines audit results

Live audit outputs captured on 2026-05-16:

- `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/data/vw_extract/_audit_georeference_last_run.json`
- `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/data/vw_extract/_audit_ifc_assignment_last_run.json`
- `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/data/vw_exports/farber-haines-2521/georeference_audit.csv`
- `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/data/vw_exports/farber-haines-2521/ifc_assignment_audit.csv`

Georeference findings:

- `document_georeferenced = 0`
- no survey point anchor found
- no stake anchor found
- review reason: `document_not_georeferenced;no_survey_point_or_stake_anchor;no_model_extents`
- the working-copy operator path intentionally uses audit + dry-run first because:
  - `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/georef/document_georef_binding.json`
  - still says `binding_status = unresolved`
  - and `allow_apply = false`

IFC findings:

- `6563` objects collected
- initial audit: `6561` objects `unmapped`, `2` objects `ok`
- after a conservative first-pass IFC entity apply: `6497` objects `unmapped`, `66` objects `ok`
- exportable families detected include plant, existing tree, hardscape, boulder, curb edging, and landscape area

First-pass IFC entity apply artifact:

- `/Users/ojeromyo/Desktop/farber_haines_ifc_entity_update_report.csv`
- `/Users/ojeromyo/Desktop/farber_haines_ifc_actionable_families.csv`

What the first-pass apply proved:

- `IfcSlab` assignments stuck successfully for hardscape concrete, gravel, and lawn classes
- `IfcGeographicElement` did **not** stick for plant, existing tree, or boulder objects through this simple scripted path
- `IfcKerb` did **not** stick for the metal edging class through this simple scripted path

Direct diagnostic evidence:

- sampled plant objects on `L-Plant-Proposed` returned `false` from both `IFC_SetIFCEntity2` and `IFC_SetIFCEntity`
- sampled existing tree objects on `L-Tree-Existing` and `L-Tree-Removed` returned `false` from both setters
- sampled boulder objects on `L-Boulder` returned `false` from both setters
- sampled edging objects on `L-Edge-Roll Top Metal` returned `false` from both setters
- artifact: `/Users/ojeromyo/Desktop/fh_ifc_diag.json`

Interpretation of that result:

- some IFC entity correction is script-fixable right now
- plant/site-object IFC assignment likely needs Data Manager mapping or object-type-specific workflows rather than a generic class walker
- the updater should treat those families as alternate-path cases, not as ordinary scripted retries

### 2a. New working-copy IFC4x3 export is real, but still incomplete

New export artifact:

- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/_Farber-Haines [2521]__ESTIMATION_WORKING_COPY__2026-05-16.ifc`

Assessment surfaces:

- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/pixeltable/scripts/assess_farber_haines_ifc_export.py`
- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/docs/farber-haines-ifc-export-assessment.json`
- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/docs/farber-haines-ifc-export-assessment.md`

Verified current state from that export:

- schema: `IFC4X3_ADD2`
- file description includes:
  - `ReferenceView_V4.3`
  - `QuantityTakeOffAddOnView`
- entity counts:
  - `IfcProject = 1`
  - `IfcSite = 1`
  - `IfcBuilding = 1`
  - `IfcBuildingStorey = 1`
  - `IfcGeographicElement = 1034`
  - `IfcSlab = 0`
- georef constructs are now present in the IFC itself:
  - `IfcProjectedCRS('EPSG:3857 WGS 84 / Pseudo-Mercator', ...)`
  - `IfcMapConversion(...)`

Important interpretation:

- this is materially stronger than the earlier thin IFC4 probe
- but it is still not the target-state export because:
  - the current exported CRS is `EPSG:3857`, not the expected Farber-Haines
    local/project CRS
  - hardscape/site families are still landing too coarsely
  - `Project Cost` and `VwPset_MARPA_*` payloads are not visible in the IFC

### Alternate-path Data Manager artifacts

To turn that blocker into a concrete workflow, the repo now has a portable Farber-Haines starter set:

- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/vw-python/examples/bootstrap_farber_haines_marpa_psets.py`
- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/vw-python/examples/build_farber_haines_data_manager_spec.py`
- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/vw-python/examples/farber_haines_data_manager_sync.py`

What this set is for:

- bootstrap record-backed custom IFC Psets in the active VWX file
- generate a starter Data Manager spec for `Plant` and `Existing Tree`
- run Data Manager audit, dry run, and apply passes without the older `/Users/admin/...` path assumptions

Measured results from the live Farber-Haines file on 2026-05-16:

- bootstrap created `VwPset_MARPA_Object`, `VwPset_MARPA_Plant`, `VwPset_MARPA_Cost`, `VwPset_MARPA_Maintenance`, `VwPset_MARPA_Source`, and `VwPset_MARPA_ExportQA`
- Data Manager apply successfully enabled `Plant` and `Existing Tree` and added `IfcGeographicElement` entries with the custom MARPA Psets
- `Pset_VegetationCommon` still failed through the scripted Data Manager path
- after Data Manager apply, sampled live `Plant` and `Existing Tree` objects still returned blank entity state through `IFC_GetIFCEntity`

Validation artifacts for that pass:

- `/tmp/farber_haines_marpa_pset_bootstrap.json`
- `/tmp/farber_haines_data_manager_sync_dryrun.json`
- `/tmp/farber_haines_data_manager_sync_apply.json`
- `/tmp/fh_post_dm_object_ifc_probe.json`

What it still does not claim:

- automatic creation of new criteria-based Data Manager rows for generic class-only families such as `L-Boulder` and `L-Edge-Roll Top Metal`
- solved document georeference binding

Interpretation:

- the pricing loop is ahead of the IFC export-readiness loop
- the active Farber-Haines model is **not** yet export-ready for reliable downstream IFC/DDC ingestion
- the immediate blockers are document georeferencing and IFC entity assignment coverage, especially for plants and site objects
- the next meaningful validators are:
  - broader IFC export plus IFC readback
  - a solved control-point georef transform
  - the IFC crosswalk from Vectorworks object UUIDs to real exported element identity

### 2b. Object identity evidence

Live export artifact:

- `/Users/ojeromyo/Desktop/vw_cost_estimate_object_rows.csv`

What it proved:

- `313` object estimate rows were exported from the active Farber-Haines VWX
- all `313` rows carry nonblank `vs.GetObjectUuid()` values
- those IDs are standard 36-character UUIDs

Current IFC-side comparison:

- the first successful IFC probe still only contains:
  - `IfcProject = 1`
  - `IfcSite = 1`
  - `IfcSlab = 0`
  - `IfcGeographicElement = 0`
- sample IFC `GlobalId` values are 22-character compressed IFC IDs, not UUID strings

Meaning:

- the current VW object-row export path is working
- the current IFC export is still too thin to support an honest object-level pricing join

### Recommended export strategy

Do not treat IFC as one export that solves everything. Split it into explicit lanes:

1. `IFC baseline semantic export`
   - objects with correct IFC entities and PSets
   - used for downstream BIM semantics and DDC extraction
2. `IFC landscape object export`
   - plant, hardscape, wall, fence, drainage focus
   - used for quantity and object-identity extraction
3. `Geospatial lane`
   - document georef audit
   - layer georef confirmation
   - GIS and shapefile or GeoJSON side lanes where needed

### Export probe status

The export blocker was narrowed and then partially resolved:

- direct `IFC_ExportNoUI(path)` originally returned `false` and wrote no file
- the real cause was confirmed in the Vectorworks dialog: `Layer Mapping` had an empty `Mapped Layers` list
- after saving a real mapped layer through the dialog, `IFC_ExportNoUI()` succeeded and wrote an IFC file

Probe artifacts:

- `/tmp/farber_haines_ifc_probe/export_result.json`
- `/tmp/farber_haines_ifc_probe/menu_export_probe.json`
- `/tmp/farber_haines_ifc_probe/project_field_probe.json`
- `/tmp/farber_haines_ifc_probe/minimal_project_retry.json`
- `/tmp/farber_haines_ifc_probe/scheme_probe.json`
- `/tmp/farber_haines_ifc_probe/scheme4_retry.json`
- `/tmp/farber_haines_ifc_probe/farber_haines_probe_20260516T231627Z.ifc`

What the first successful export proves:

- headless IFC export is usable on this workstation
- the active VWX now has at least one saved IFC layer mapping
- the last verified successful export schema is `IFC4`
  - proven by `FILE_SCHEMA(('IFC4'));` in:
    - `/tmp/farber_haines_ifc_probe/farber_haines_probe_20260516T231627Z.ifc`

What it does **not** prove yet:

- a verified successful `IFC4x3` export does **not** exist yet for Farber-Haines
- a retry with scheme `4` was attempted and failed:
  - `/tmp/farber_haines_ifc_probe/scheme4_retry.json`
- the exported IFC is still semantically thin on the first pass:
  - `IfcProject = 1`
  - `IfcSite = 1`
  - `IfcGeographicElement = 0`
  - `IfcSlab = 0`
  - `IfcMapConversion = 0`
  - `IfcProjectedCRS = 0`
- so the export mechanism is alive, but georef and object-entity richness are still missing from the file contents

Interpretation:

- the export blocker is no longer the existence of a headless export path
- the currently **proven** export version is IFC4, not IFC4x3
- the next export-readiness work is:
  - widen the mapped layer set
  - improve IFC entity coverage in the exported scope
  - solve document georef so `IfcMapConversion` and `IfcProjectedCRS` appear

### Practical gate sequence

1. audit georeference
2. apply or confirm document georeference
3. confirm georeferenced design layers for export-relevant content
4. audit IFC assignments
5. correct plant and site-object IFC entity drift
6. export IFC with last-known-good settings
7. ingest IFC into the downstream stack

## Downstream Target

The target chain stays:

`Vectorworks -> pricing worksheet / export -> IFC + georef -> iTwin + DDC -> Pixeltable`

Interpretation:

- Vectorworks owns geometry, class structure, plant styles, and first-mile quantities
- the pricing workbook owns budget logic
- IFC carries semantic object data downstream
- georeference establishes spatial truth
- Pixeltable remains the central system of record

## Henry Meeting Focus

This is the core message for Henry:

### What is already working

- We can map Vectorworks classes to budget pricing.
- We can attach `Project Cost` records to live objects in the Farber-Haines model.
- We can generate worksheet and CSV summaries with quantity, unit cost, and total cost.
- We have validated the quantity loop for `ea`, `sf`, and `lf`.

### What we need from the Vectorworks side

- best practice for object-type-specific quantity extraction where `vs.HLength()` is insufficient
- best practice for automating or standardizing Data Manager IFC mappings for landscape objects
- confirmation of the most reliable georeference and IFC export sequence for a Landmark-heavy site model
- confirmation of the cleanest path for batch plant-style 3D replacement in production files

### What the project focus should be

The focus is not generic BIM export. The focus is:

`Vectorworks -> spreadsheet / pricing automation loop`

More specifically:

- select object or class in Vectorworks
- derive quantity correctly
- map to budget pricing
- expose estimate output in worksheet and external spreadsheet form

## Recommended Next Proofs

1. tighten the remaining `0.0` linear classes with object-type-specific geometry extraction
2. build the first production `Data Tag` or worksheet surface that displays live cost info on selected objects
3. run georeference audit on the active Farber-Haines VWX
4. run IFC assignment audit on the active Farber-Haines VWX
5. apply document georeference and place a survey-point anchor using the GROVE georef scripts
6. use Data Manager or object-type-specific workflows to solve plant, existing tree, boulder, and edging IFC assignments
7. perform one controlled IFC export and validate object/entity carry-through
8. swap one real plant style to placeholder 3D pins and one to final custom 3D geometry
