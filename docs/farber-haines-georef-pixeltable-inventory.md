# Farber-Haines Georef And Pixeltable Inventory

Date: 2026-05-16

## What The Script Error Screenshot Means

The screenshot at `/Users/ojeromyo/Desktop/CleanShot 2026-05-16 at 17.14.54.jpg` shows failures from earlier probe paths, not the current proven path:

- `NameError: name '__file__' is not defined`
  - caused by older Vectorworks wrapper experiments that executed inline Python without injecting `__file__`
- `Handle variable is NIL`
  - caused by broad IFC/object probes touching handles that were not valid for the specific function being called
- `SetPref failed with constant 8908`
  - confirms the old undocumented preference-number export path is not reliable on this workstation
- `Menu cannot be found. Export IFC...`
  - older code used the wrong menu text
- `Invalid number of parameters to the callback function`
  - older callback signature bug in a Vectorworks-side iterator

These are useful diagnostics, but they are no longer the active blocker. The current export path works once the document has a saved IFC layer mapping.

## Proven Current State

### Export path

The active Farber-Haines file is:

- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/projects/vectorworks project files/_Farber-Haines [2521].vwx`

Headless IFC export originally failed because `Export IFC Project -> Layer Mapping` had an empty `Mapped Layers` list.

After saving a real layer mapping through the Vectorworks dialog, the scripted export succeeded:

- export marker: `/tmp/farber_haines_ifc_probe/export_result.json`
- exported IFC: `/tmp/farber_haines_ifc_probe/farber_haines_probe_20260516T231627Z.ifc`

### Important limitation of that export

The first successful IFC export is only a structural proof:

- `IfcProject = 1`
- `IfcSite = 1`
- `IfcGeographicElement = 0`
- `IfcSlab = 0`
- `IfcMapConversion = 0`
- `IfcProjectedCRS = 0`

So the export mechanism is alive, but semantic/georef richness is still missing. The next work is about improving what gets exported, not just whether export runs.

## Reusable Georef Truth Found Across Project Iterations

### 1. GROVE_HARNESS Juniper 2026

Current Farber-Haines georef artifacts live here:

- `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/georef/document_georef_binding.json`
- `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/georef/control_points_wgs84_provisional.json`
- `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/georef/crs/epsg_2876.wkt`
- `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/georef/crs/epsg_3857.wkt`

What they tell us:

- the current document binding is explicitly blocked:
  - `binding_status = unresolved`
  - `allow_apply = false`
- the blind `0,0` document-origin strategy is known-bad for this file
- there is already a provisional parcel-corner control-point set in WGS84 for NW/NE/SE/SW parcel corners

This means the right next georef move is not another blind apply. It is a control-point solve.

### 2. MARPA_918_JUNIPER

This older lane already solved the pattern we need conceptually:

- surveyed/control point store:
  - `lattice.marpa.site_anchors`
- drawing-to-world picks:
  - `lattice.marpa.plan_gcp_picks`
- transform provenance:
  - `projects.marpa.juniper_918.scene.coord_transforms`

Key implementation references:

- `/Volumes/PixelTable/MARPA_918_JUNIPER/scripts/pixeltable/fit_coord_transform.py`
- `/Volumes/PixelTable/MARPA_918_JUNIPER/src/python/pixeltable/schema.py`
- `/Volumes/PixelTable/MARPA_918_JUNIPER/docs/MARPA_VIEWER_HANDOFF.md`

Why this matters:

- it proves the organization already uses a pattern of:
  - control points
  - explicit transform fit
  - append-only transform provenance in Pixeltable
- the exact CRS there is mostly `EPSG:3857`, so its numbers are not directly reusable for Farber-Haines
- the pattern is reusable even if the actual coordinates are not

### 3. MARPA_PLATFORM

There is already prior Farber-Haines worksheet and budget processing here:

- `/Volumes/PixelTable/MARPA_PLATFORM/data/runs/farber-haines-2521/2026-05-01T201914Z__sim/02_vw_exports_laneA/worksheet_manifest.json`
- `/Volumes/PixelTable/MARPA_PLATFORM/data/runs/farber-haines-2521/2026-05-01T201914Z__sim/02_vw_exports_laneA/worksheet_Plant_Schedule.csv`
- `/Volumes/PixelTable/MARPA_PLATFORM/data/runs/farber-haines-2521/2026-05-01T201914Z__sim/02_vw_exports_laneA/worksheet_Hardscape_Areas.csv`
- `/Volumes/PixelTable/MARPA_PLATFORM/data/runs/farber-haines-2521/2026-05-01T201914Z__sim/02_vw_exports_laneA/worksheet_Site_Prep_and_Drainage.csv`
- `/Volumes/PixelTable/MARPA_PLATFORM/data/runs/farber-haines-2521/2026-05-01T201914Z__sim/02_vw_exports_laneA/worksheet_Walls_and_Edging.csv`
- `/Volumes/PixelTable/MARPA_PLATFORM/scripts/run_ingest_budget.sh`
- `/Volumes/PixelTable/MARPA_PLATFORM/docs/pixeltable_schema.md`

Why this matters:

- we already have a Farber-Haines-specific worksheet export precedent
- we already have a budget ingestion precedent
- the older lane modeled bronze/silver/gold budget and worksheet bodies in Pixeltable

## The Current LATTICE Pixeltable Landing Surfaces

The live repo already has the correct schema surfaces for this project.

### Coordinate authority

Use:

- `lattice/bridge/project_georef`

Authoritative references:

- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/pixeltable/migrations/0013_georef_reality_mirror.py`
- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/meta/SCHEMA.md`
- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/meta/ARCHITECTURE.md`

This table is the canonical place for:

- project CRS
- WGS84 anchor
- survey/control points JSON
- IFC georef fields
- VW internal origin fields
- transform matrices

### Object-level pricing and quantities

The current object-level landing surface already exists on `ifc_elements`.

Relevant columns already in schema:

- `unit_cost`
- `unit_cost_region`
- `quantity`
- `quantity_unit`
- `boq_phase`
- `cost_last_updated`
- `estimated_value`
- `actual_cost`
- `erp_item_id`

Authoritative schema references:

- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/pixeltable/migrations/0012_extended_schema.py`
- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/meta/SCHEMA.md`

This means the repo does not need a second pricing store just to hold first-pass estimates. The existing object bridge can already carry price and quantity fields once ingestion is wired.

## What Should Go Into Pixeltable Next

### Georef

For Farber-Haines, the next Pixeltable write should be a `project_georef` row built from:

1. the active project id for Farber-Haines
2. the provisional parcel corner set in `control_points_wgs84_provisional.json`
3. any verified survey or parcel-corner upgrade that replaces those provisional points
4. the VW internal origin / document-georef state from the active VWX
5. the first valid IFC georef data once `IfcMapConversion` and `IfcProjectedCRS` appear in export

Status on 2026-05-16:

- this first row is now written
- writer:
  - `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/pixeltable/scripts/ingest_farber_haines_georef.py`
- verified backing-table count:
  - `project_georef = 1` for `project_id = farber-haines-2521`
- the inserted row is still a provisional seed, not a solved document transform

### Pricing / estimates

The next estimate write path should target object-level rows, not just standalone CSVs:

1. keep budget workbook rows as source artifacts
2. keep worksheet/class/object exports as source artifacts
3. attach pricing and quantity data onto parsed object rows in `ifc_elements`
4. use `boq_phase` for Phase 1 / Phase 2 split
5. derive report views from Pixeltable instead of treating CSV as the terminal product

Status on 2026-05-16:

- project-scoped estimate tables are now created and populated:
  - `lattice/projects/farber-haines-2521/vw_estimate_rows`
  - `lattice/projects/farber-haines-2521/vw_estimate_objects`
- writer:
  - `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/pixeltable/scripts/ingest_farber_haines_estimates.py`
- verified backing-table counts:
  - `vw_estimate_rows = 33`
  - `vw_estimate_objects = 313`

What was required to populate `vw_estimate_objects`:

- object-level rows were exported from Vectorworks with:
  - `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/vw-python/examples/export_project_cost_object_rows.py`
- source artifact:
  - `/Users/ojeromyo/Desktop/vw_cost_estimate_object_rows.csv`
- object identity is preserved as `vs.GetObjectUuid()` values

What that proved:

- the active VWX now has a durable object-row estimate export path
- `313` object rows carry nonblank Vectorworks UUIDs
- the current crosswalk is still blocked because these UUIDs are standard 36-char UUIDs while the current IFC export only exposes 22-char IFC `GlobalId` strings
- the current IFC probe is also semantically thin:
  - `IfcSlab = 0`
  - `IfcGeographicElement = 0`
  - only `IfcProject` and `IfcSite` were present in the first successful export

## Recommended Integration Path

### Immediate

1. Keep the saved IFC layer mapping in the VWX so `IFC_ExportNoUI()` remains usable.
2. Export a broader IFC scope after improving mapped layers beyond just `Proposed Site Plan`.
3. Solve Farber-Haines georef from parcel/control points instead of another blind origin apply.
4. Write the first `project_georef` row in LATTICE.
5. Export object-level Project Cost rows from Vectorworks and ingest them into `vw_estimate_objects`.
6. Improve the IFC export until real element rows exist and a VW UUID to IFC identity crosswalk can be designed from evidence.

### Next

1. Improve IFC export coverage so the file contains actual priced landscape elements, not only `IfcProject` and `IfcSite`.
2. Populate `ifc_elements.quantity`, `ifc_elements.quantity_unit`, `ifc_elements.unit_cost`, and `ifc_elements.boq_phase` after the VW object UUID to IFC GlobalId crosswalk is proved.
3. Build a Pixeltable-backed estimate report view for:
   - retail / vendor
   - phase split
   - profit / margin

### Important constraint

Do not copy the old `EPSG:3857` Juniper numbers into Farber-Haines. Reuse the control-point-and-transform pattern, not the old project coordinates.
