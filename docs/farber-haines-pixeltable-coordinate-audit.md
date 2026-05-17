# Farber-Haines Pixeltable Coordinate Audit

Date: 2026-05-16

## Summary

Farber-Haines already has a live `project_georef` row in Pixeltable, but it is
still a provisional seed rather than a solved coordinate authority.

## Live table checked

- `lattice.bridge.project_georef`

Filter:

- `project_id = 'farber-haines-2521'`

## What is already in Pixeltable

- `project_id = farber-haines-2521`
- `epsg_code = 2876`
- CRS WKT for EPSG 2876
- provisional site origin:
  - `longitude = -105.28455249999999`
  - `latitude = 40.03678`
- boundary geometry:
  - `boundary_wkt_wgs84`
  - `boundary_geojson`
  - `bounding_box_json`
- provisional parcel-corner control points in `control_points_json`
- notes explicitly saying the binding remains unresolved

## What is missing or still blank

- `vw_origin_x`
- `vw_origin_y`
- `vw_scale`
- `vw_rotation_deg`
- `transform_vw_to_wgs84`
- `transform_wgs84_to_ecef`
- `transform_project_to_utm`
- `transform_ifc_to_wgs84`
- `survey_easting`
- `survey_northing`
- `ifc_ref_latitude`
- `ifc_ref_longitude`
- `ifc_ref_elevation`
- OSM ids and file paths
- shapefile / geopackage flags
- orthophoto and DEM references

## What this means

Yes, coordinates are already in Pixeltable.

But no, the full solved Farber-Haines georeference is not already there.

Current Pixeltable truth is:

- a good provisional parcel/boundary seed
- not yet a solved VW-to-world transform
- not yet an IFC-to-world transform
- not yet a survey-backed binding

## Related live tables

These are live and useful, but they are estimating tables, not coordinate
authority tables:

- `lattice.projects.farber-haines-2521.vw_estimate_rows`
- `lattice.projects.farber-haines-2521.vw_estimate_objects`

They prove the pricing loop is landing in Pixeltable, but they do not solve the
remaining georef binding problem.
