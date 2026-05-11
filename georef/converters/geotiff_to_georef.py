#!/usr/bin/env python3
"""GeoTIFF DEM / orthophoto -> project_georef.dem_* or .orthophoto_*.

Stub. Extracts CRS via GDAL, computes min/max elevation, writes file path
+ resolution back to the georef row.
"""
from __future__ import annotations


def geotiff_to_georef(tif_path: str, project_id: str, asset_kind: str) -> dict:
    """asset_kind in {'dem', 'orthophoto'}"""
    raise NotImplementedError("geotiff_to_georef stub")
