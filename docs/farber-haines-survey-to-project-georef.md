# Farber-Haines Survey CSV To Project Georef

Date: 2026-05-16

Once a real survey CSV exists, the project-specific updater is:

- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/pixeltable/scripts/apply_farber_haines_survey_csv.py`

Example:

```bash
uv run --with pyproj \
  /Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/pixeltable/scripts/apply_farber_haines_survey_csv.py \
  /path/to/farber_haines_survey_points.csv \
  --source-epsg EPSG:2876
```

What it updates in `lattice.bridge.project_georef`:

- `config_version` -> `farber-haines-survey-csv-v1`
- `survey_easting`
- `survey_northing`
- `survey_elevation_units`
- `benchmark_elevation_m`
- `state_plane_zone`
- `control_points_json`
- `benchmark_id`
- `survey_file_path`
- `has_survey_csv`
- `notes`
- `updated_at`

This is the right moment when the project should stop relying mainly on:

- provisional parcel-corner screenshots
- OSM-only context

and start treating the survey stakes and corner coordinates as the highest-truth
control source for the georef solve.
