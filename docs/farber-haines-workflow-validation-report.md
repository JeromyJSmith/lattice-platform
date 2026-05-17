# Farber-Haines Workflow Validation Report

- Generated at: `2026-05-17T00:27:57.811167+00:00`
- Project: `farber-haines-2521`
- Working copy: `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/projects/vectorworks project files/_Farber-Haines [2521]__ESTIMATION_WORKING_COPY__2026-05-16.vwx`

## Overall

- Overall status: `fail`
- Highest-value gap: Solve the Vectorworks-to-world binding from real survey corners/stakes, then write the fit back to `lattice.bridge.project_georef`. That is the highest-value blocker because Cesium/iTwin alignment, IFC georef trust, and downstream overlay validation all depend on it.

## Checks

### pricing

- Status: `pass`
- Summary: Pricing and estimate exports are live in Pixeltable and on disk.
- Pixeltable summary rows: 33
- Pixeltable object rows: 313
- Summary CSV rows: 33
- Object CSV rows: 313

### georef_seed

- Status: `warn`
- Summary: Project georef seed is live, but the document binding is still unresolved.
- Live project_georef row present: True
- EPSG code: 2876
- Control points in seed: 4
- Binding status: unresolved

### vw_binding

- Status: `fail`
- Summary: Vectorworks-to-world binding is still unresolved.
- Binding status: unresolved
- Allow apply: False
- VW origin X: None
- VW origin Y: None
- VW scale: None
- VW rotation deg: None
- Transform present: False
- Document georeferenced: 0
- Review reason: document_not_georeferenced;no_survey_point_or_stake_anchor;no_model_extents

### survey_control

- Status: `fail`
- Summary: No live survey-control solve has been applied yet.
- Survey CSV applied live: False
- Survey file path: 
- Selected reference JSON present: False
- Point-pairs working JSON present: False
- Fit JSON present: False
- Cycle report present: True
- Cycle report error: post-export georef run failed: missing selected reference export: /Users/ojeromyo/Desktop/farber_haines_selected_reference_points.json

### georef_operator

- Status: `warn`
- Summary: Georef operator path is healthy and fail-closed, but waiting on a real Vectorworks selected-reference export.
- Authoritative point-pair package present: True
- Authoritative source summary present: True
- Selected reference JSON present: False
- Cycle report present: True
- Cycle report ok: False
- Cycle report error: post-export georef run failed: missing selected reference export: /Users/ojeromyo/Desktop/farber_haines_selected_reference_points.json

### ifc

- Status: `warn`
- Summary: IFC export runs, but the current working-copy export still has CRS, semantic typing, or custom-property payload gaps.
- IFC export result ok: True
- IFC file present: True
- Current working-copy IFC4x3 export present: True
- Current working-copy IFC schema: IFC4X3_ADD2
- Current working-copy IFC projected CRS EPSG: 3857
- Current working-copy IFC IfcGeographicElement count: 1034
- Mapped objects in audit: 66
- Unmapped objects in audit: 6497
- Direct IFC setter failures sampled: 12
- Current working-copy IFC issue: hardscape_not_typed_as_ifcslab
- Current working-copy IFC issue: unexpected_crs:3857
- Current working-copy IFC issue: missing_marpa_cost_pset
- Current working-copy IFC issue: missing_project_cost_payload

### ifc_project_settings

- Status: `warn`
- Summary: IFC project export dialog settings are still un-audited for Farber-Haines.
- IFC project-properties summary present: False
- IFC project-properties CSV present: False
- IFC project fields read: 0
- IFC project required fields missing: 0
- IFC project document_georeferenced snapshot: None

### plant_assets

- Status: `pass`
- Summary: Local plant 3D asset pipeline surfaces are present on disk.
- TRELLIS server present: True
- TRELLIS UI present: True
- TRELLIS outputs dir present: True
- Phase1 extract present: True
- Viewer dir present: True

### docs

- Status: `pass`
- Summary: Presentation and operator docs are in place.
- estimation_brief: True
- record_export_matrix: True
- georef_lock_plan: True
- georef_live_sequence: True
- henry_meeting_focus: True

## Live Pixeltable

- `project_georef` row present: `True`
- `vw_estimate_rows` count: `33`
- `vw_estimate_objects` count: `313`
- `project_georef` config version: `1`

## Artifacts

- `summary_csv`: exists=`True` path=`/Users/ojeromyo/Desktop/vw_cost_estimate_summary.csv`
- `object_csv`: exists=`True` path=`/Users/ojeromyo/Desktop/vw_cost_estimate_object_rows.csv`
- `mapping_csv`: exists=`True` path=`/Users/ojeromyo/Desktop/vw_class_budget_mapping_first_pass.csv`
- `project_georef_seed`: exists=`True` path=`/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/projects/farber-haines-2521/georef.config.seed.json`
- `project_georef_evidence`: exists=`True` path=`/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/projects/farber-haines-2521/georef.evidence.register.json`
- `binding_json`: exists=`True` path=`/Volumes/PixelTable/GROVE_HARNESS/juniper2026/georef/document_georef_binding.json`
- `control_points_json`: exists=`True` path=`/Volumes/PixelTable/GROVE_HARNESS/juniper2026/georef/control_points_wgs84_provisional.json`
- `georef_audit_json`: exists=`True` path=`/Volumes/PixelTable/GROVE_HARNESS/juniper2026/data/vw_extract/_audit_georeference_last_run.json`
- `ifc_audit_json`: exists=`True` path=`/Volumes/PixelTable/GROVE_HARNESS/juniper2026/data/vw_extract/_audit_ifc_assignment_last_run.json`
- `ifc_project_props_json`: exists=`False` path=`/Volumes/PixelTable/GROVE_HARNESS/juniper2026/data/vw_extract/_audit_ifc_project_props_last_run.json`
- `ifc_project_properties_csv`: exists=`False` path=`/Volumes/PixelTable/GROVE_HARNESS/juniper2026/data/vw_exports/farber-haines-2521/ifc_project_properties.csv`
- `ifc_export_result`: exists=`True` path=`/tmp/farber_haines_ifc_probe/export_result.json`
- `ifc_probe_file`: exists=`True` path=`/tmp/farber_haines_ifc_probe/farber_haines_probe_20260516T231627Z.ifc`
- `ifc_diag_json`: exists=`True` path=`/Users/ojeromyo/Desktop/fh_ifc_diag.json`
- `ifc4x3_export_file`: exists=`True` path=`/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/_Farber-Haines [2521]__ESTIMATION_WORKING_COPY__2026-05-16.ifc`
- `ifc4x3_assessment_json`: exists=`False` path=`/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/docs/farber-haines-ifc-export-assessment.json`
- `ifc4x3_assessment_md`: exists=`False` path=`/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/docs/farber-haines-ifc-export-assessment.md`
- `fit_json`: exists=`False` path=`/tmp/farber_haines_georef_fit.json`
- `fit_binding_candidate`: exists=`False` path=`/tmp/farber_haines_georef_binding_candidate.json`
- `cycle_report_json`: exists=`True` path=`/tmp/farber_haines_georef_cycle_report.json`
- `selected_reference_json`: exists=`False` path=`/Users/ojeromyo/Desktop/farber_haines_selected_reference_points.json`
- `selected_reference_csv`: exists=`False` path=`/Users/ojeromyo/Desktop/farber_haines_selected_reference_points.csv`
- `point_pairs_working`: exists=`False` path=`/Users/ojeromyo/Desktop/farber_haines_point_pairs_working.json`
- `authoritative_point_pairs`: exists=`True` path=`/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/projects/farber-haines-2521/sources/farber_haines_point_pairs_authoritative_template.json`
- `authoritative_georef_source_summary`: exists=`True` path=`/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/projects/farber-haines-2521/sources/farber_haines_authoritative_georef_sources_summary.json`
- `trellis_server`: exists=`True` path=`/Volumes/PixelTable/MARPA_918_JUNIPER/experiments/trees_sage/trellis_server.py`
- `trellis_html`: exists=`True` path=`/Volumes/PixelTable/MARPA_918_JUNIPER/experiments/trees_sage/trellis.html`
- `trellis_outputs_dir`: exists=`True` path=`/Volumes/PixelTable/MARPA_918_JUNIPER/experiments/trees_sage/trellis_outputs`
- `phase1_extract`: exists=`True` path=`/Volumes/PixelTable/MARPA_918_JUNIPER/src/python/extract/phase1_extract.py`
- `viewer_dir`: exists=`True` path=`/Volumes/PixelTable/MARPA_918_JUNIPER/viewer`
- `estimation_brief`: exists=`True` path=`/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/docs/farber-haines-vectorworks-estimation-brief.md`
- `record_export_matrix`: exists=`True` path=`/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/docs/farber-haines-record-export-matrix.md`
- `georef_lock_plan`: exists=`True` path=`/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/docs/farber-haines-georef-lock-plan.md`
- `georef_live_sequence`: exists=`True` path=`/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/docs/farber-haines-georef-live-update-sequence.md`
- `henry_meeting_focus`: exists=`True` path=`/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/docs/farber-haines-henry-meeting-focus.md`
