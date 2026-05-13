---
description: Implement georef converter stubs, enforce EPSG normalization at ingest, validate mirror state, and maintain the 67-column project_georef table and spatial indexes.
---

# LATTICE Georeferencing and Reality Capture

The georef section owns 7 format converters in `georef/converters/`, the
`lattice/bridge/project_georef` table (67 columns), reality capture pipeline stubs
under `/v1/reality/*` endpoints, and the `lattice/reality/mirror_state` table.
All coordinates must be EPSG-normalized before any Pixeltable write. The scoring
script `scripts/score-georef.sh` measures converter completeness, EPSG coverage,
mirror sync health, and spatial index status.

## When this skill applies

- Implementing or updating one of the 7 georef converter modules
- Fixing an EPSG normalization gap (rows in `project_georef` with null `epsg`)
- Validating mirror state drift (`sync_warnings` not empty)
- Adding or verifying PostGIS GiST indexes on geometry columns
- Running the georef section cycle: `bash meta/harness/bootstrap/run-autoresearch.sh georef`
- A converter returns 501 or raises `NotImplementedError` and needs implementation

## How it works

1. Check converter stub status:
   ```bash
   git grep -h "stub-501\|NotImplementedError" -- georef/converters/*.py
   ```
   Files that still raise `NotImplementedError` are stubs awaiting implementation.
   The 7 converters are: `kml.py`, `shapefile.py`, `geotiff.py`, `survey_csv.py`,
   `ifc.py`, `osm.py`, `dxf.py`.

2. Implement a converter following the canonical pattern:
   ```python
   # georef/converters/<format>.py
   def ingest_<format>(source_path: str, project_id: str) -> dict:
       """Returns normalized row dict for lattice/bridge/project_georef."""
       # Parse source → extract CRS → reproject to WGS84 via pyproj
       # Compute transform_matrix_wgs84_local
       # Return dict with epsg, geom_point_wkt, transform_matrix_wgs84_local set
   ```
   Wrap in a `@pxt.udf(return_type=pxt.String)` in the corresponding UDF module.

3. Normalize coordinates:
   - Use `pyproj.Transformer.from_crs(source_epsg, 4326)` for WGS84 conversion.
   - Store geometry as WKT string: `POINT(lon lat)` in `geom_point_wkt`.
   - Never write raw Vectorworks internal coordinate values.

4. Verify EPSG coverage in Pixeltable:
   ```python
   import pixeltable as pxt
   t = pxt.get_table("lattice/bridge/project_georef")
   nulls = t.select(t.project_id).where(t.epsg == None).collect()
   assert len(nulls) == 0, f"{len(nulls)} rows missing EPSG"
   ```

5. Check mirror state:
   ```python
   ms = pxt.get_table("lattice/reality/mirror_state")
   warnings = ms.select(ms.project_id, ms.sync_warnings).where(
       ms.sync_warnings != "[]"
   ).collect()
   ```
   Any non-empty `sync_warnings` array is a drift alert.

6. Verify spatial indexes on `site_zones` and `ifc_elements`:
   ```bash
   pixeltable select column_name, dtype from lattice.bridge.site_zones._schema \
     where column_name like 'geom%'
   ```

7. Test ingest endpoint:
   ```bash
   curl -s -X POST http://localhost:8001/v1/georef/ingest/config \
     -H "Content-Type: application/json" \
     -d '{"project_id":"test","source_format":"kml","source_path":"/tmp/test.kml"}'
   ```
   Expect HTTP 200 with `{"row_id": "..."}` or HTTP 501 for stub converters.

## Files used

- `georef/converters/kml.py`, `shapefile.py`, `geotiff.py`, `survey_csv.py`,
  `ifc.py`, `osm.py`, `dxf.py` — converter implementations
- `georef/GOAL.md` — georef section fitness function
- `pixeltable/service/routes/georef.py` — FastAPI routes for georef + reality
- `lattice/bridge/project_georef` — Pixeltable table (67 columns, EPSG required)
- `lattice/bridge/site_zones` — spatial zone table with GiST index
- `lattice/bridge/ifc_elements` — IFC element table with geometry columns
- `lattice/reality/mirror_state` — mirror sync state per active project
- `lattice/reality/point_clouds`, `lattice/reality/drone_frames` — reality capture tables
- `scripts/score-georef.sh` — section scoring script

## Constraints

- All geometry stored as `pxt.String` containing WKT (`POINT(lon lat)`) or GeoJSON.
  Never `pxt.Geometry` — that type does not exist in Pixeltable 0.6.x.
- Converters that are not yet implemented must raise `NotImplementedError("stub-501")`
  so the POST endpoint returns HTTP 501 cleanly rather than crashing.
- All coordinates must be EPSG-normalized before any Pixeltable write.
  Raw VW internal coordinate values must never reach a table row.
- PostGIS spatial queries (`ST_Distance`, `ST_Contains`, etc.) run at the DuckDB
  WASM query layer downstream — not inside Pixeltable UDFs.
- Reality capture ingest is heavy — run IFC geometry normalization async via thread
  pool, not on the FastAPI event loop.
- Mirror drift (`sync_warnings` non-empty) must be resolved before the next ingest
  cycle writes new rows to `mirror_state`.
