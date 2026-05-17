# Farber-Haines Georef Lock Plan

Date: 2026-05-16

## Why the georeference is not sticking

The current Farber-Haines file does not have a solved document-to-world
binding. The evidence is explicit:

- `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/georef/document_georef_binding.json`
  - `binding_status = unresolved`
  - `allow_apply = false`
  - blind `0,0` apply already proved wrong

The last dry-run state also shows the document is currently anchored to the
wrong place:

- `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/data/vw_extract/_apply_georef_last_results.json`
  - current doc georef before apply:
    - `lat = 38.8894757`
    - `lon = -77.03524595`
  - target Farber-Haines anchor:
    - `lat = 40.0370784`
    - `lon = -105.2845774`

So the problem is not “Vectorworks forgot.” The problem is that the current
document/user-origin relationship has never been solved against authoritative
site control for this file.

## What has to be true for Cesium alignment

To line up on a Cesium globe, we need a solved transform between:

1. Vectorworks drawing coordinates
2. project CRS coordinates
3. WGS84 latitude/longitude

That requires actual paired points, not just a desired EPSG code.

## Minimum viable lock strategy

Use at least 3 point pairs, preferably 4:

- one northwest parcel corner
- one northeast parcel corner
- one southeast parcel corner
- one southwest parcel corner

For each point pair we need:

- Vectorworks drawing X/Y from the actual Farber-Haines working-copy model
- matching real-world WGS84 lat/lon or projected CRS coordinates

Once those pairs exist, we can solve:

- translation
- rotation
- scale sanity

And then we can decide whether the document georef should be applied through:

- document georef + correct user origin
- survey point anchor
- geolocate workflow
- or a hybrid of the above

## What we should stop doing

Do not keep re-running:

- `SetDocGeoRefByUsrOrg(2876)` with a blind `0,0` user-origin assumption
- survey point creation at `(0,0)` without a solved binding

That only writes a wrong georef more consistently.

## What we should do next

1. Open the working copy:
   - `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/projects/vectorworks project files/_Farber-Haines [2521]__ESTIMATION_WORKING_COPY__2026-05-16.vwx`
2. Pick 3 to 4 stable parcel or survey reference points that exist in the model.
3. Record their Vectorworks X/Y coordinates.
4. Match them to world coordinates from survey / GIS / parcel control.
5. Solve the binding.
6. Only then apply document georef and place the survey point.
7. Re-export to IFC and verify:
   - `IfcMapConversion`
   - `IfcProjectedCRS`
   - Cesium placement

## Working-copy capture tool

Use this in the copied VWX after selecting the actual parcel boundary,
survey markers, stakes, or other stable reference geometry:

- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/vw-python/examples/run_farber_haines_export_selected_reference_points_working_copy.py`

Outputs:

- `/Users/ojeromyo/Desktop/farber_haines_selected_reference_points.json`
- `/Users/ojeromyo/Desktop/farber_haines_selected_reference_points.csv`

What it captures:

- selected object UUID
- class and layer
- object center
- bounding-box center
- polygon vertices via `GetPolyPt`
- polyline vertices via `GetPolylineVertex`

That gives us actual drawing-space coordinates we can pair against world-space
parcel or survey points.

## Existing sources we can use

- provisional world control:
  - `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/georef/control_points_wgs84_provisional.json`
- binding artifact:
  - `/Volumes/PixelTable/GROVE_HARNESS/juniper2026/georef/document_georef_binding.json`
- operator sequence:
  - `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/docs/farber-haines-working-copy-operator-sequence.md`
- solve sequence:
  - `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/docs/farber-haines-georef-solve-sequence.md`
- fit tool:
  - `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/georef/converters/fit_vw_point_pairs.py`

## The short version

The georef does not stick because the file does not yet know which drawing
points correspond to which real-world points. EPSG alone is not enough.
We need a solved control-point binding first, then the document georef will
have something true to stick to.
