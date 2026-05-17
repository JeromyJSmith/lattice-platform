# Farber-Haines Project Settings Research Report

Date: 2026-05-16

## Purpose

Answer, from verified sources:

1. What settings in this workflow are true project-level settings that should be set once in Vectorworks
2. What data is actually being written into the VWX by our current scripts
3. What remains external scaffolding rather than live Vectorworks state
4. What Vectorworks University and official training material indicate as the intended workflow

## Verified Project-Level Settings In Vectorworks

### 1. Document georeferencing

Official Vectorworks help says the primary project georeferencing lives at:

- `File > Document Settings > Georeferencing`

Key findings from the help:

- document georeferencing aligns the drawing internal origin to a specific Earth location
- the document coordinate system is the main setting to establish first
- most design layers normally inherit the document georeferencing
- layer-level overrides exist, but are "rarely needed"
- there are three supported setup methods:
  - Georeferencing dialog
  - Geolocate tool
  - Survey Point tool

Source:

- `/Users/ojeromyo/.vectorworks-docs/docs/vw-help/2026_eng_VW2026_Guide_Georeference_Specifying_document_georeferencing.htm.md`

### 2. IFC export setup

Official Vectorworks help says the IFC project export configuration lives at:

- `File > Export > Export IFC Project`

Key project-level IFC settings called out by the help:

- IFC version
- model view / MVD
- add-on views such as Quantity Take Off
- whether custom property sets are exported
- IFC georeferencing source
- IFC model placement origin:
  - Internal Origin
  - User Origin
  - Custom Origin
  - Survey Point
  - Stake
- transformation / rotation
- layer mapping to stories or site

Important consequence from the help:

- unmapped layers are not exported
- layer mapping settings are retained by Vectorworks and only need to be redone when new layers are added

Source:

- `/Users/ojeromyo/.vectorworks-docs/docs/vw-help/2026_eng_VW2026_Guide_IFC_Exporting_IFC_projects.htm.md`

Important current-project nuance:

- the Vectorworks help documents the available IFC version setting
- the earlier probe path was only verified as `IFC4`, not `IFC4x3`
- this is proven from the exported file itself:
  - `/tmp/farber_haines_ifc_probe/farber_haines_probe_20260516T231627Z.ifc`
  - schema line: `FILE_SCHEMA(('IFC4'));`
- an attempted retry using scheme `4` did not produce a successful export:
  - `/tmp/farber_haines_ifc_probe/scheme4_retry.json`
- however, the newer working-copy export is now proven as `IFC4X3_ADD2`:
  - `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/_Farber-Haines [2521]__ESTIMATION_WORKING_COPY__2026-05-16.ifc`
  - schema line: `FILE_SCHEMA(('IFC4X3_ADD2'));`
- that newer export is still not fully correct for the project because its
  current exported CRS is `EPSG:3857`, not the expected Farber-Haines local
  CRS, and custom pricing/MARPA property payloads are not yet visible

### 3. Data Manager mapping

Official Vectorworks help says the project-level data-mapping system lives at:

- `Tools > Data Manager`

Key findings from the help:

- Data Manager is where project mapping schemes are stored
- when you click `OK` and save the file, active settings are stored as the document's settings
- it is intended for:
  - attaching data sets automatically by object type or criteria
  - attaching custom property sets for IFC export
  - mapping record fields to IFC fields
  - creating focused data sheets for object info palette editing

This is the real "set once for the project" surface for IFC/data rules.

Source:

- `/Users/ojeromyo/.vectorworks-docs/docs/vw-help/2026_eng_VW2026_Guide_DataManager_Using_the_Data_Manager.htm.md`

### 4. Plant style 3D representation

Official Vectorworks help and product guidance indicate that plant graphics are controlled at the plant style level, not per instance, through Plant Style Manager and style graphics editing.

Source evidence already used elsewhere in the project:

- `/Users/ojeromyo/.vectorworks-docs/docs/vw-help/2026_eng_VW2026_Guide_Plants1_Plant_Style_Manager.htm.md`
- `/Users/ojeromyo/.vectorworks-docs/docs/vw-help/2026_eng_VW2026_Guide_Plants1_Replacing_plant_style_graphics.htm.md`
- `/Users/ojeromyo/.vectorworks-docs/docs/vw-help/2026_eng_VW2026_Guide_Plants1_Editing_plant_style_graphics.htm.md`

## Verified Record Export Surface

Separate from the true project-level settings above, Vectorworks also exposes a
tabular record export lane at:

- `Tools > Database > Record Format Connection`

Official help says this surface lists the record formats available in the file
and can export each record format as a database table, with each record field
becoming a database column.

Source:

- `/Users/ojeromyo/.vectorworks-docs/docs/vw-help/2026_eng_VW2026_Guide_Database_Automatically_creating_a_database_table_from_a_record_format.htm.md`

Important distinction:

- this is **not** the IFC export version/schema selector
- this is the correct surface for exporting:
  - `Project Cost`
  - `Plant Record`
  - `Existing Tree`
  - `Landscape Area`
  - `VwPset_MARPA_*` records

Farber-Haines specific matrix:

- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/docs/farber-haines-record-export-matrix.md`

## What Our Current Scripts Actually Write Into The VWX

### Pricing records on objects

The current pricing updater writes a custom record format named:

- `Project Cost`

Fields written per object:

- `Unit Cost`
- `Quantity`
- `Total Cost`
- `Description`
- `Unit`
- `Measure Basis`

Verified in:

- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/vw-python/examples/apply_estimation_mapping_csv.py`
- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/vw-python/examples/build_cost_estimate_from_xlsx.py`

Concrete API calls used:

- `vs.NewField(...)`
- `vs.SetRecord(...)`
- `vs.SetRField(...)`

### Worksheets inside Vectorworks

The current scripts also create and show worksheets inside the VWX, including:

- `Cost Mapping Update Report`
- `Cost Estimate`
- export/support worksheets in other scripts

Concrete API calls used:

- `vs.CreateWS(...)`
- `vs.SetWSCellFormulaN(...)`
- `vs.ShowWS(...)`

Verified in:

- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/vw-python/examples/apply_estimation_mapping_csv.py`
- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/vw-python/examples/build_cost_estimate_from_xlsx.py`
- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/vw-python/examples/export_project_cost_summary.py`

### Optional class mutation

The pricing updater can also mutate class structure if configured:

- rename class definitions
- reclass matching objects

Concrete API calls used:

- `vs.RenameClass(...)`
- `vs.SetClass(...)`

This is not the default "pricing is stored on classes" pattern. It is a class-mapping assist plus object-record workflow.

## What Is Not Yet Being Written Into The VWX

### Solved document georeference

The current live state still shows:

- no solved document georef binding
- no solved VW-to-world transform written back
- no active selected-reference export on disk

Current validator evidence:

- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/docs/farber-haines-workflow-validation-report.md`

Current georef state:

- `binding_status = unresolved`
- no `vw_origin_x`
- no `vw_origin_y`
- no `vw_scale`
- no `vw_rotation_deg`
- no `transform_vw_to_wgs84`

So the georef side is still mostly:

- source data
- matching logic
- fit logic
- fail-closed runner behavior

but not a finished mutation of the Farber-Haines VWX.

### Final Data Manager project mapping

We have Data Manager sync scaffolding and specs in the repo, but the validated state does not yet prove a completed production Data Manager mapping inside the active Farber-Haines VWX for:

- plant IFC semantics
- site object IFC semantics
- pricing record attachment rules

### Final IFC export semantics

IFC export mechanics run, but the current proof still shows thin semantic output.

Current validated status:

- export runs
- mapped objects: `66`
- unmapped objects: `6497`

So the export dialog/settings are partway proved, not fully production-ready.

## Research: What Other Vectorworks Training Material Suggests

### Vectorworks University: Survey Point Tool

Vectorworks University explicitly frames Survey Point as the tool to:

- set project coordinates
- set geolocation
- ensure you are working near the internal origin

Source:

- [Survey Point Tool](https://university.vectorworks.net/course/index.php?categoryid=191)

This matches the official help and supports the idea that the correct project-level georef workflow is not "random repeated script mutation," but establishing a project coordinate relationship through Survey Point / document georef.

### Vectorworks University: IFC Export and Utilizing the Data Manager

Vectorworks University has a dedicated advanced session:

- `IFC EXPORT AND UTILIZING THE DATA MANAGER`

Its learning objectives are:

- locate the Data Manager
- map fields
- map custom fields and records to IFC
- create Data Sheets to focus on the fields you need

Source:

- [IFC Export and Utilizing the Data Manager](https://university.vectorworks.net/course/index.php?categoryid=49)

This strongly supports the conclusion that the intended production workflow is:

- Data Manager for project-level mapping
- not repeated one-off per-object scripting as the final long-term pattern

### Vectorworks University: Existing Tree survey import

Vectorworks University also has a course on Existing Trees that explicitly says Vectorworks can:

- generate Existing Tree objects in the correct locations
- with the correct data
- from a survey spreadsheet

Source:

- [All Courses listing with Coffee Break - Existing Trees](https://university.vectorworks.net/course/index.php?categoryid=49)

This matters because it shows a real precedent inside Vectorworks for:

- survey/spreadsheet-driven object creation
- data-backed landscape objects

### Official landscape IFC guide

The official Vectorworks landscape IFC guide gives a workflow very close to what we need:

- geolocate or align the file to the survey by its user origin
- establish a survey point
- map layers for export
- attach IFC data to custom symbols/objects
- use Data Manager for default/custom mapping
- test exported IFC in a viewer

Key lines come from:

- `BIM Interoperability for Landscape Architecture: IFC Exchanges in Vectorworks Landmark`

Verified source:

- `https://download2.vectorworks.net/ebooks/us/guides/bim-interoperability-for-landscape-architecture-ifc-exchanges-in-vectorworks-landmark.pdf`

## Verified Conclusion

The current project has two different realities:

### Already real in the VWX

- object-level `Project Cost` records
- Vectorworks worksheets
- optional class/object remapping

### Not yet real in the VWX

- solved document georeferencing
- final project-level Data Manager mappings
- final IFC export semantics
- final plant-style 3D configuration inside the active Farber-Haines file

## Most Likely Intended Production Pattern

Based on official help plus University training, the production-grade Vectorworks pattern is:

1. Set document georeferencing once for the file
2. Use Survey Point / user-origin alignment to bind the file correctly
3. Use Data Manager to define project-level mapping rules
4. Attach custom record data and IFC data through those mappings
5. Use worksheets for verification and reporting
6. Export IFC with a stable origin strategy and stable layer mapping

That is different from the current status, which is:

- pricing workflow partly operational
- georef workflow scaffolded and validated as fail-closed
- IFC workflow partially operational
- project-level Vectorworks settings not yet fully locked
- proven IFC export version currently `IFC4`, while any `IFC4x3` configuration
  should still be treated as intent rather than verified success
