# Farber-Haines Georef Config Seed

Date: 2026-05-16

The repo’s canonical georef surface is `georef.config.json`, not loose temp
files. For Farber-Haines we now generate a seed document from the currently
known control/binding state with:

- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/georef/converters/build_farber_haines_georef_config_seed.py`

Default output:

- `/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/projects/farber-haines-2521/georef.config.seed.json`

What it contains:

- `EPSG:2876` CRS + WKT
- target origin lat/lon from the current binding artifact
- current VW internal origin from the latest dry-run state
- provisional parcel-corner control points
- a provisional boundary GeoJSON polygon built from those corners
- source-priority metadata matching the repo georef contract

What it does not claim:

- that the georef is solved
- that the VW-to-world transform is validated
- that `transforms.vw_to_wgs84` is ready

This seed is the canonical project-config starting point. Once real corner and
stake point pairs are solved, the fit output can be used to upgrade this config
and then feed `project_georef`.
