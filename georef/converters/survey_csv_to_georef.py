#!/usr/bin/env python3
"""Survey CSV (control points: id, easting, northing, elevation_ft, description)
-> project_georef.control_points_json + survey_* fields.

Stub. pyproj reprojects from the source EPSG (usually a State Plane zone)
to WGS84 for the canonical origin row.
"""
from __future__ import annotations


def survey_csv_to_georef(csv_path: str, project_id: str, source_epsg: str) -> dict:
    raise NotImplementedError("survey_csv_to_georef stub")
