# Georeferencing + Reality Capture Harness — LATTICE Meta-Harness Control

Owns 7 georef converter stubs (KML, Shapefile, GeoTIFF, Survey CSV, IFC, OSM, DXF), reality capture pipeline stubs (drone/splat/pointcloud/mirror), `project_georef` table (67 cols), coordinate normalization at ingest boundary, PostGIS spatial queries downstream.

## Fitness Function

Score georef health against **converter completeness**, **coordinate normalization**, and **reality capture mirror state**:

1. **Converter stub inventory**: `ls georef/converters/*.py` should list 7 files (kml.py, shapefile.py, geotiff.py, survey_csv.py, ifc.py, osm.py, dxf.py) with `raise NotImplementedError(stub-501)` or working implementation
2. **EPSG normalization**: every row inserted to `lattice/bridge/project_georef` has `epsg` field populated + `transform_matrix_wgs84_local` computed and non-null
3. **Mirror state clean**: `lattice/reality/mirror_state` table for active projects has `sync_warnings` = empty array (no drift alerts)
4. **Geospatial indexing**: `lattice/bridge/site_zones` and `lattice/bridge/ifc_elements` have PostGIS GiST indexes on geom columns (verified via Pixeltable column metadata)
5. **Reality pipeline validation**: drone ingest stub, splat ingest stub, point-cloud ingest stub, mirror reconciliation stub all callable via `/v1/reality/*` endpoints

**Baseline score**: `scripts/score-georef.sh` runs in < 5s, outputs JSON with `converters_ready`, `epsg_coverage`, `mirror_sync_health`, `spatial_index_status`.

## Improvement Loop

Autoresearch loop (on every commit to `georef/` or when reality capture data arrives):

1. Run `scripts/score-georef.sh` → baseline snapshot
2. Auto-read `georef/converters/` directory, check each file for stub-501 or implementation marker
3. Spawn `claude -p` subprocess to design converter UDF stubs, generate Pixeltable `@pxt.udf` templates, suggest PostGIS spatial function patterns
4. Write reasoning + converter templates to `runtime-runs/<run-id>/georef-converters.md`
5. If all converters implemented OR explicitly stub-501 marked, and EPSG coverage > 95%, commit; else hold
6. Flock concurrency: max 1 converter design job at a time via `/tmp/vwbridge-georef.lock`

## Action Catalog

- **Converter status**: `git grep -h "stub-501\|NotImplementedError" -- georef/converters/*.py` shows which are stubs
- **EPSG audit**: `pixeltable select project_id, epsg from lattice.bridge.project_georef where epsg is null | wc -l` should be 0
- **Mirror sync check**: `pixeltable select count(*) from lattice.reality.mirror_state where json_array_length(sync_warnings) > 0`
- **Spatial index verify**: `pixeltable select column_name, dtype from lattice.bridge.site_zones._schema where column_name like 'geom%'`
- **Ingest test**: POST to `/v1/georef/ingest/config` with sample JSON, verify `lattice/bridge/project_georef` row created

## Operating Mode

- **Converter pattern**: each `georef/converters/<format>.py` exports `ingest_<format>(source_path, project_id) -> dict` or raises stub-501
- **Pixeltable UDF pattern**: `@pxt.udf(return_type=pxt.String)` wraps converter, normalizes coords to WGS84, stores WKT in `geom_point_wkt` column
- **PostGIS pattern**: downstream queries in `pixeltable/service/routes/georef.py` use raw SQL `ST_Distance(geom, ...)`, `ST_Contains(boundary, centroid)`, etc.
- **Reality capture flow**: ingest video/frames → extract frames → splat or pointcloud → store in `lattice/reality/point_clouds` or `lattice/reality/drone_frames` → sync mirror state
- **Failure mode**: converter unimplemented → POST returns 501; EPSG missing → ingest blocks until georeferencing configured; mirror drift → alert in `lattice/execution/health`
