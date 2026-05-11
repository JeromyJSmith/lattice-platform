#!/usr/bin/env python3
"""KML / KMZ -> project_georef.boundary_*. Reads coordinates via GDAL,
reprojects to WGS84, writes WKT + GeoJSON + area into the georef row.

Stub. Acceptance criteria on the matching GitHub issue (Universal georef
ingest). Sketch:

    from osgeo import ogr
    src = ogr.Open(kml_path)
    layer = src.GetLayer()
    geom = layer.GetFeature(0).GetGeometryRef()
    wkt = geom.ExportToWkt()      # WGS84 from KML
    geojson = geom.ExportToJson()
"""
from __future__ import annotations
import sys


def kml_to_georef(kml_path: str, project_id: str) -> dict:
    raise NotImplementedError("kml_to_georef stub")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: kml_to_georef.py <kml_path> <project_id>", file=sys.stderr)
        raise SystemExit(1)
    print(kml_to_georef(sys.argv[1], sys.argv[2]))
