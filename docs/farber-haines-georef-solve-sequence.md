# Farber-Haines Georef Solve Sequence

Date: 2026-05-16

## Goal

Turn real Vectorworks drawing coordinates plus real-world control points into a
measured transform before mutating document georeference.

## Inputs

### 1. Drawing-side coordinates

Captured from the working copy with:

- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/vw-python/examples/run_farber_haines_export_selected_reference_points_working_copy.py`

Artifacts:

- `/Users/ojeromyo/Desktop/farber_haines_selected_reference_points.json`
- `/Users/ojeromyo/Desktop/farber_haines_selected_reference_points.csv`

### 2. Point-pair template

- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/docs/farber-haines-georef-point-pairs-template.json`
- helper builder:
  - `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/georef/converters/build_point_pairs_from_selected.py`
- authoritative world-side package builder:
  - `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/georef/converters/build_farber_haines_authoritative_point_pair_package.py`
- selected-to-authoritative matcher:
  - `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/georef/converters/build_farber_haines_matched_point_pairs.py`
- post-export autofit runner:
  - `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/georef/converters/run_farber_haines_georef_post_export.py`
- end-to-end cycle runner:
  - `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/pixeltable/scripts/run_farber_haines_georef_cycle.py`

Project-ready world-side package:

- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/projects/farber-haines-2521/sources/farber_haines_point_pairs_authoritative_template.json`

Populate it with:

- `vw_x`
- `vw_y`
- `lat_wgs84`
- `lon_wgs84`

or explicit projected coordinates:

- `project_x`
- `project_y`

Recommended fit strategy:

- use the 4 county parcel corners as anchors
- then include as many 5-foot survey stake rectangles along the boundary as you can reliably match
- if you can identify them cleanly in the drawing, also match one or more nearby control candidates such as `Q-8`, `M-405-1`, `M-405`, or `V-8-1`
- let the overdetermined fit expose bad picks through residuals instead of trusting only 4 points

Helper command to build a fillable working file from the selected-reference export:

```bash
python3 /Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/georef/converters/build_point_pairs_from_selected.py
```

Default output:

- `/Users/ojeromyo/Desktop/farber_haines_point_pairs_working.json`

Helper command to build the authoritative world-side package:

```bash
python3 /Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/georef/converters/build_farber_haines_authoritative_point_pair_package.py
```

That output is already shaped for `fit_vw_point_pairs.py`; the only missing fields are the matched `vw_x` / `vw_y` values from the working-copy capture.

Helper command to auto-merge the selected VW export with the authoritative package:

```bash
python3 /Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/georef/converters/build_farber_haines_matched_point_pairs.py
```

Default outputs:

- `/Users/ojeromyo/Desktop/farber_haines_point_pairs_matched.json`
- `/Users/ojeromyo/Desktop/farber_haines_point_pairs_match_summary.json`

This matcher will:

- use the best selected polygon as the parcel-boundary source and map its ordered vertices to the 4 county parcel corners
- match selected named objects to benchmark/control ids like `Q-8`, `M-405-1`, `M-405`, `V-8-1`
- leave unmatched world-side points with null `vw_x` / `vw_y`
- reject selected-reference payloads unless they:
  - declare `export_kind = vectorworks_selected_reference_points`
  - point to a real `.vwx` file on disk
  - do not look synthetic or mock-derived
  - contain a non-empty object list whose count matches `selected_count`

The selected-reference export now carries provenance fields:

- `export_generated_at_utc`
- `export_version`
- `object_signature_sha256`
- `source_vwx_basename`
- `georef_snapshot.document_is_georeferenced`
- `georef_snapshot.active_layer_is_georeferenced`

Canonical Vectorworks API calls used by the selected-reference export:

- `ForEachObject` (selected-object harvest via criteria `SEL=TRUE`)
- `GetObjectUuid`
- `GetTypeN`
- `GetClass`
- `GetLayer` + `GetLName`
- `GetName`
- `GetBBox`
- `GetVertNum`
- `GetPolyPt`
- `GetPolylineVertex`
- `GetFPathName`
- `IsGeoreferenced` (document/layer georef state snapshot)
- `GetPluginStyleSymbol` (style symbol handle retrieval)

Project-specific one-shot post-export command:

```bash
python3 /Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/georef/converters/run_farber_haines_georef_post_export.py
```

This will:

1. read `/Users/ojeromyo/Desktop/farber_haines_selected_reference_points.json`
2. build `/Users/ojeromyo/Desktop/farber_haines_point_pairs_matched.json`
3. build `/Users/ojeromyo/Desktop/farber_haines_point_pairs_match_summary.json`
4. run the fit automatically if at least 3 matched rows are available

Project-specific full cycle command:

```bash
/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/pixeltable/.venv/bin/python \
  /Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/pixeltable/scripts/run_farber_haines_georef_cycle.py
```

Default behavior is dry-run only. It will:

1. run the post-export match/fit path
2. check fit quality against thresholds
3. write `/tmp/farber_haines_georef_cycle_report.json`
4. refuse to apply the fit to `project_georef` unless `--apply-fit` is passed and thresholds are satisfied

This runner now uses the project `.venv` interpreter directly instead of
`uv run python`, which removes the local editable-package discovery failure
that previously blocked the apply stage.

To allow writeback only when the fit is genuinely acceptable:

```bash
/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/pixeltable/.venv/bin/python \
  /Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/pixeltable/scripts/run_farber_haines_georef_cycle.py --apply-fit
```

Project-specific fit runner:

```bash
python3 /Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/georef/converters/run_farber_haines_georef_fit.py
```

Default fit outputs:

- `/tmp/farber_haines_georef_fit.json`
- `/tmp/farber_haines_georef_binding_candidate.json`

## Solve

Run:

```bash
uv run --with numpy --with pyproj \
  /Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/georef/converters/fit_vw_point_pairs.py \
  --input /path/to/filled_point_pairs.json \
  --output /tmp/farber_haines_georef_fit.json \
  --binding-output /tmp/farber_haines_georef_binding_candidate.json
```

## Outputs

### Fit diagnostics

- transform matrix
- translation vector
- implied rotation
- implied scale
- per-point residuals
- RMSE
- max residual

### Binding candidate

A non-authoritative recommendation bundle suitable for review before updating:

- `document_georef_binding.json`
- `project_georef`
- any later apply script inputs

## Decision rule

- low residuals across all points: candidate binding is worth testing in the working copy
- high residuals or one bad outlier: the point pairs are wrong, mixed, or insufficient

Do not apply document georef until the residuals are good enough to trust.
