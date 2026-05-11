#!/usr/bin/env python3
"""Shapefile (.shp + .prj + companions) -> project_georef boundary fields.

Stub. Reads the .prj for EPSG, reprojects geometry to WGS84 via pyproj.
"""
from __future__ import annotations


def shapefile_to_georef(shp_path: str, project_id: str) -> dict:
    raise NotImplementedError("shapefile_to_georef stub")
