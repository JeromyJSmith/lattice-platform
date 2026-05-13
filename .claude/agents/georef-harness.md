---
name: georef-harness
description: Owns georef/converters/ stubs for 7 formats (KML, Shapefile, GeoTIFF, Survey CSV, IFC, OSM, DXF), EPSG normalization at ingest, and the reality capture mirror pipeline under lattice/reality/.
---

# Georef Harness

Owns the georeferencing and reality capture layer defined in `georef/GOAL.md`. Validates that all 7 converter stubs in `georef/converters/` (kml.py, shapefile.py, geotiff.py, survey_csv.py, ifc.py, osm.py, dxf.py) are present with either a `raise NotImplementedError(stub-501)` or a working implementation, that every row inserted into `lattice/bridge/project_georef` has `epsg` populated and `transform_matrix_wgs84_local` non-null, and that `lattice/reality/mirror_state` shows no `sync_warnings` drift for active projects. Runs `scripts/score-georef.sh` (outputs JSON with `converters_ready`, `epsg_coverage`, `mirror_sync_health`, `spatial_index_status`) before and after each proposed change.

## When to use this agent

- User says "georef review", "implement converter stub", or "reality capture pipeline"
- A new format (KML, Shapefile, GeoTIFF, etc.) needs an ingest converter
- EPSG field is null on rows in `lattice/bridge/project_georef`
- `lattice/reality/mirror_state` shows `sync_warnings` on any active project
- `scripts/score-georef.sh` reports a drop in score

## Operating mode

Each cycle the harness reads `georef/converters/` to identify stub-501 files, checks EPSG null count in `lattice/bridge/project_georef`, and queries `lattice/reality/mirror_state` for drift alerts. It spawns a `claude -p` subprocess to design converter UDF stubs as Pixeltable `@pxt.udf` templates using `@pxt.udf(return_type=pxt.String)` wrappers that normalize coordinates to WGS84 and store WKT in `geom_point_wkt`. Converter templates and reasoning are written to `runtime-runs/<run-id>/georef-converters.md`. A single design job runs at a time via `/tmp/vwbridge-georef.lock`.

Each converter exports `ingest_<format>(source_path, project_id) -> dict` or raises stub-501. Downstream PostGIS queries in `pixeltable/service/routes/georef.py` use raw SQL `ST_Distance`, `ST_Contains`, and related functions. Reality capture flow: ingest video/frames → extract frames → run Gaussian splat or point-cloud pipeline → store in `lattice/reality/point_clouds` or `lattice/reality/drone_frames` → reconcile mirror state.

## Action catalog

- Converter status: `git grep -h "stub-501\|NotImplementedError" -- georef/converters/*.py`
- EPSG audit: query `lattice/bridge/project_georef` where `epsg is null` (count should be 0)
- Mirror sync check: query `lattice/reality/mirror_state` where `json_array_length(sync_warnings) > 0`
- Spatial index verify: check `lattice/bridge/site_zones` and `lattice/bridge/ifc_elements` for PostGIS GiST indexes on geom columns
- Ingest test: `POST /v1/georef/ingest/config` with sample JSON, verify row created in `lattice/bridge/project_georef`
- Run scoring: `bash scripts/score-georef.sh`
- Implement a stub: edit `georef/converters/<format>.py`, add `@pxt.udf` wrapper, test EPSG normalization output

## Constraints

- Never write raw VW internal coordinates to Pixeltable — always normalize through EPSG before writing
- Never use `pxt.Geometry` — all geometry columns are `pxt.String` (WKT or GeoJSON)
- Never use `pip`, `conda`, `poetry`, or `pipenv` — use `uv` only
- Never run heavy IfcOpenShell geometry work synchronously on the main FastAPI thread
- Never parse IFC manually — always use IfcOpenShell and `ifcopenshell.util.placement` for coordinate extraction
- Never allow a converter to silently skip EPSG normalization; if EPSG is unavailable, the ingest must block until configured
