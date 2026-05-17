# Farber-Haines Working-Copy Operator Sequence

Date: 2026-05-16

Use this sequence in the copied VWX file:

- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/projects/vectorworks project files/_Farber-Haines [2521]__ESTIMATION_WORKING_COPY__2026-05-16.vwx`

The copied file is the destructive-safe boundary. Do not run these mutation
steps against the untouched architect baseline.

## 1. Pricing / estimate application

Run in Vectorworks:

- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/vw-python/examples/run_farber_haines_apply_estimation_working_copy.py`
- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/vw-python/examples/run_farber_haines_export_cost_summary_working_copy.py`
- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/vw-python/examples/run_farber_haines_export_cost_object_rows_working_copy.py`

Expected artifacts:

- `/Users/ojeromyo/Desktop/vw_cost_estimate_summary.csv`
- `/Users/ojeromyo/Desktop/vw_cost_estimate_object_rows.csv`

## 2. Georeference readback before mutation

Run in Vectorworks:

- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/vw-python/examples/run_farber_haines_georef_audit_working_copy.py`
- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/vw-python/examples/run_farber_haines_georef_dryrun_working_copy.py`

Expected outputs under GROVE:

- `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/data/vw_extract/_audit_georeference_last_run.json`
- `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/data/vw_extract/_apply_georef_last_results.json`
- `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/data/vw_exports/farber-haines-2521/georeference_audit.csv`

Current truth:

- `document_georef_binding.json` is still unresolved
- `allow_apply = false`
- blind 0,0 binding is known-bad

So the dry run is the safe checkpoint until a control-point solve exists.

## 3. IFC export readiness

Run in Vectorworks:

- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/vw-python/examples/run_farber_haines_ifc_assignment_audit_working_copy.py`
- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/vw-python/examples/run_farber_haines_ifc_probe_working_copy.py`

Expected outputs:

- `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/data/vw_extract/_audit_ifc_assignment_last_run.json`
- `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/data/vw_exports/farber-haines-2521/ifc_assignment_audit.csv`
- `/tmp/farber_haines_ifc_probe_working_copy/export_result.json`

## 4. Plant 3D workflow

Do style-level work directly in the copied file:

- use Plant Style Manager
- replace 3D graphics at the style level
- use placeholder pins first if location QA is the goal
- use imported GLB or symbol-based assets when visual quality matters

## 5. Meeting focus

The current meeting-ready line is:

- Vectorworks can already drive price-bearing quantity outputs
- the copied VWX is the safe experimental surface
- the remaining technical blockers are georef control-point binding and richer IFC semantic export, not the pricing loop itself
