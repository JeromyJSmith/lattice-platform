# Farber-Haines Georef Live Update Sequence

Date: 2026-05-16

This is the combined project-specific path once real survey and fit data exist.

## Preconditions

1. A real survey CSV exists for parcel corners and/or stake points.
2. The VW working-copy point-pair fit has already been run, producing:
   - `/tmp/farber_haines_georef_fit.json`
   - `/tmp/farber_haines_georef_binding_candidate.json`

## Single-run path

```bash
uv run --with pyproj \
  /Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/pixeltable/scripts/run_farber_haines_georef_live_update.py \
  /path/to/farber_haines_survey_points.csv \
  --source-epsg EPSG:2876
```

## What it does

1. Applies survey CSV control into the live `lattice.bridge.project_georef` row.
2. Applies the fitted VW transform into that same row.

## If only survey is ready

```bash
uv run --with pyproj \
  /Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/pixeltable/scripts/run_farber_haines_georef_live_update.py \
  /path/to/farber_haines_survey_points.csv \
  --source-epsg EPSG:2876 \
  --skip-fit
```

## Verification checklist after update

Check the live `project_georef` row for:

- `has_survey_csv = true`
- populated `control_points_json`
- populated `survey_easting`
- populated `survey_northing`
- populated `vw_scale`
- populated `vw_rotation_deg`
- populated `transform_vw_to_wgs84`
- updated `config_version`

Then validate visually:

1. Cesium / globe placement
2. IFC / iTwin overlay alignment
3. orientation against true north
4. stake and parcel-edge agreement
