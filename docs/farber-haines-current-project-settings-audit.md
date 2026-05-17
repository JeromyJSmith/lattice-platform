# Farber-Haines Current Project Settings Audit

Date: 2026-05-16

## Purpose

This report answers a narrower and more operational question than the broader
workflow brief:

- which settings in this workflow are true project-level Vectorworks settings
- which of those are currently proven set in the Farber-Haines file
- which are currently missing
- which are still unknown because we have not yet run the right audit

This is intentionally evidence-based. If a setting has not been directly
observed through an audit, script result, or documented export artifact, it is
listed as unknown rather than assumed.

## Project-Level Setting Surfaces

Based on official Vectorworks help, the main project-level surfaces are:

1. `File > Document Settings > Georeferencing`
2. `File > Export > Export IFC Project`
3. `Tools > Data Manager`
4. Plant Style / Plant Style Manager configuration

Sources:

- `/Users/ojeromyo/.vectorworks-docs/docs/vw-help/2026_eng_VW2026_Guide_Georeference_Specifying_document_georeferencing.htm.md`
- `/Users/ojeromyo/.vectorworks-docs/docs/vw-help/2026_eng_VW2026_Guide_IFC_Exporting_IFC_projects.htm.md`
- `/Users/ojeromyo/.vectorworks-docs/docs/vw-help/2026_eng_VW2026_Guide_DataManager_Using_the_Data_Manager.htm.md`

## Current Evidence Summary

### 1. Document georeferencing

Status: **missing / not set correctly**

Strongest evidence:

- `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/data/vw_extract/_audit_georeference_last_run.json`
- `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/georef/document_georef_binding.json`

Observed current state:

- `document_georeferenced = 0`
- `coordinate_system_name = ""`
- `epsg_code = ""`
- `doc_latitude = 38.8894757`
- `doc_longitude = -77.03524595`
- `survey_point_exists = 0`
- `stake_origin_exists = 0`
- `review_reason = document_not_georeferenced;no_survey_point_or_stake_anchor;no_model_extents`
- binding file says:
  - `binding_status = unresolved`
  - `allow_apply = false`

Interpretation:

- the Farber-Haines file is not currently in a trustworthy project-level
  georeferenced state
- there is no valid survey-point/stake anchor currently recognized by the audit
- the current lat/lon values are not trustworthy site truth for this project

### 2. User origin / internal-origin relationship

Status: **partially observed**

Strongest evidence:

- `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/data/vw_extract/_audit_georeference_last_run.json`

Observed current state:

- `internal_origin_x = 0.0`
- `internal_origin_y = 0.0`
- `user_origin_x = 799.4679627382823`
- `user_origin_y = -717.2747968857685`
- `distance_from_internal_origin = 1074.0726966515906`

Interpretation:

- the file currently has a non-zero user-origin offset
- this is one of the project-level facts that matters for IFC origin strategy
- but it is not yet tied to a valid georeferenced survey-point solve

### 3. Survey Point / Stake origin

Status: **missing**

Strongest evidence:

- `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/data/vw_extract/_audit_georeference_last_run.json`

Observed current state:

- `survey_point_exists = 0`
- `stake_origin_exists = 0`
- `stake_count = 0`
- `survey_locus_count = 0`

Interpretation:

- no project anchor currently exists in the file in the form that the audit
  recognizes
- this is a direct reason the document georef is not yet considered valid

### 4. True north / project north

Status: **observed but weakly distinguished**

Strongest evidence:

- `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/data/vw_extract/_audit_georeference_last_run.json`

Observed current state:

- `true_north_rotation = 0.0`
- `project_north_rotation = 0.0`
- note says these are identical because the script only has one API surface:
  `vs.GetAngleToNorth`

Interpretation:

- the current audit does not prove a separate project-north configuration
- only the exposed angle-to-north value is observed

### 5. IFC project export dialog fields

Status: **unknown / not yet audited**

Strongest evidence:

- the audit script exists:
  - `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/vw_plugins/audit_ifc_project_properties.py`
- project working-copy runner now exists:
  - `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/vw-python/examples/run_farber_haines_ifc_project_properties_audit_working_copy.py`
- but the Farber-Haines outputs are missing:
  - `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/data/vw_extract/_audit_ifc_project_props_last_run.json`
  - `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/data/vw_exports/farber-haines-2521/ifc_project_properties.csv`

Interpretation:

- we do **not** currently know, from evidence, whether the following are set in
  the export dialog:
  - project name / site address fields
  - IFC georeferencing pane values
  - origin setup mode
  - map conversion values
  - CRS fields
- these remain a real audit gap

### 6. IFC export mechanics

Status: **present but incomplete**

Strongest evidence:

- `/tmp/farber_haines_ifc_probe/export_result.json`
- `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/data/vw_extract/_audit_ifc_assignment_last_run.json`
- `/Users/ojeromyo/Desktop/fh_ifc_diag.json`

Observed current state:

- IFC export runs
- last verified successful schema is `IFC4`
  - proven from:
    - `/tmp/farber_haines_ifc_probe/farber_haines_probe_20260516T231627Z.ifc`
    - schema line: `FILE_SCHEMA(('IFC4'));`
- mapped objects in audit: `66`
- unmapped objects in audit: `6497`
- sampled direct IFC setter failures: `12`
- an attempted scheme-4 retry did not succeed:
  - `/tmp/farber_haines_ifc_probe/scheme4_retry.json`

Interpretation:

- export itself is alive
- the old probe path was only proven as `IFC4`
- the current working-copy export is now proven as `IFC4X3_ADD2`:
  - `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/_Farber-Haines [2521]__ESTIMATION_WORKING_COPY__2026-05-16.ifc`
  - `FILE_SCHEMA(('IFC4X3_ADD2'));`
- the current working-copy export also includes:
  - `IFCPROJECTEDCRS('EPSG:3857 WGS 84 / Pseudo-Mercator', ...)`
  - `IFCMAPCONVERSION(...)`
- so georef is now present in the IFC, but it is currently using `EPSG:3857`
  instead of the expected Farber-Haines local/project CRS
- the current working-copy export is still semantically incomplete:
  - `IfcGeographicElement = 1034`
  - `IfcSlab = 0`
  - no visible `Project Cost` payload
  - no visible `VwPset_MARPA_*` payload
- project-level IFC setup is not good enough yet for meaningful landscape
  semantic output

### 7. Data Manager mapping

Status: **partially applied**

Strongest evidence:

- `/tmp/farber_haines_data_manager_sync_apply.json`
- `/Users/ojeromyo/Desktop/farber_haines_data_manager_mapping_spec.json`

Observed current state:

- object-level Data Manager enable/add-entry calls succeeded for:
  - `Plant`
  - `Existing Tree`
- desired entity:
  - `IfcGeographicElement`
- MARPA record-backed Psets were enabled for those object families:
  - `VwPset_MARPA_Object`
  - `VwPset_MARPA_Plant`
  - `VwPset_MARPA_Cost`
  - `VwPset_MARPA_Source`
  - `VwPset_MARPA_ExportQA`
- some standard/custom property set operations failed, including:
  - `IFC_CustPsetFromRec(...) returned FALSE`
  - `IFC_DMAddPSetForEnt(... 'Pset_VegetationCommon' ...) returned FALSE`

Interpretation:

- Data Manager is not blank
- there is real project-level mapping work inside the VWX for Plant and
  Existing Tree
- but it is not a clean fully-verified final mapping state
- boulders and edging still require manual criteria-based follow-up according
  to the mapping spec

### 8. Pricing data in Vectorworks

Status: **present**

Strongest evidence:

- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/vw-python/examples/apply_estimation_mapping_csv.py`
- `/Users/ojeromyo/Desktop/vw_cost_estimate_summary.csv`
- `/Users/ojeromyo/Desktop/vw_cost_estimate_object_rows.csv`
- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/docs/farber-haines-workflow-validation-report.md`

Observed current state:

- `Project Cost` record fields are being written on objects
- Vectorworks worksheets are being generated
- grouped estimate rows in Pixeltable: `33`
- object-level estimate rows in Pixeltable: `313`

Interpretation:

- the pricing side is the most real and most project-integrated slice so far
- this is not just external scaffolding; it is actively writing object data and
  worksheet data in the VWX

### 9. Plant 3D asset lane

Status: **external pipeline present; VWX state not yet directly audited**

Strongest evidence:

- `/Volumes/PixelTable/MARPA_918_JUNIPER/experiments/trees_sage/trellis_server.py`
- `/Volumes/PixelTable/MARPA_918_JUNIPER/experiments/trees_sage/trellis.html`
- `/Volumes/PixelTable/MARPA_918_JUNIPER/experiments/trees_sage/trellis_outputs`
- `/Volumes/PixelTable/MARPA_918_JUNIPER/src/python/extract/phase1_extract.py`
- `/Volumes/PixelTable/MARPA_918_JUNIPER/viewer`

Interpretation:

- the local image-to-3D generation lane exists
- what is **not** yet directly audited is whether the active Farber-Haines VWX
  has its plant styles configured with:
  - placeholder 3D pins
  - image props
  - real 3D symbols

## Current Known / Missing / Unknown

### Known present

- pricing record workflow on VW objects
- Vectorworks estimate worksheets
- non-zero user-origin offset
- partial Data Manager mapping for Plant and Existing Tree
- working IFC export mechanics
- local plant 3D asset generation pipeline

### Known missing

- valid document georeferencing
- survey point anchor
- stake anchor
- solved VW-to-world transform

### Unknown because not yet directly audited

- current IFC export dialog project/site data values
- current IFC export origin mode selection
- current layer mapping selections inside the IFC export dialog
- exact plant-style 3D representation state in the active Farber-Haines file

## Practical Conclusion

The strongest evidence says the project is **not** stuck because "nothing is
being inserted into Vectorworks." The more accurate picture is:

- pricing and some mapping data **are** being inserted into Vectorworks
- the project-level georeference settings are **not yet actually locked in**
- the IFC export dialog state is still partly a blind spot because we have not
  yet run the project-properties audit against the active Farber-Haines file

## Highest-Value Next Audits

1. Run `audit_ifc_project_properties.py` against the active Farber-Haines file
   so the IFC export dialog settings stop being unknown.
2. Audit the plant style 3D state in the active file so we know whether any
   styles already carry 3D geometry or pin-style placeholders.
3. Generate a real selected-reference export from the working-copy VWX so the
   georef operator lane can move from fail-closed scaffolding to a real solve.
