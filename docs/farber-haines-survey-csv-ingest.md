# Farber-Haines Survey CSV Ingest

Date: 2026-05-16

The highest-truth next source for Farber-Haines georeferencing is a survey CSV
containing stake and corner coordinates.

The generic converter is now implemented at:

- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/georef/converters/survey_csv_to_georef.py`

It expects at minimum:

- `id` or `point_id` or `name`
- `easting` or `x`
- `northing` or `y`

Optional fields:

- `elevation_ft` or `elevation` or `z`
- `description`
- `quality`

Example usage:

```bash
uv run --with pyproj \
  /Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/georef/converters/survey_csv_to_georef.py \
  /path/to/survey_points.csv \
  farber-haines-2521 \
  EPSG:2876
```

It returns a payload suitable for merging into `project_georef`, including:

- `survey_easting`
- `survey_northing`
- `benchmark_elevation_m`
- `state_plane_zone`
- `control_points_json`
- `survey_file_path`
- `has_survey_csv = true`

For this project, this is the cleanest way to promote:

- parcel corners
- property stakes
- repeated 5-foot survey stake points

into the canonical georef authority instead of leaving them as manual notes.
