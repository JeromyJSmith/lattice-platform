#!/usr/bin/env python3
"""Pull OSM features for the project boundary via the Overpass API and write
OSM IDs + GeoJSON path into project_georef.

Stub. Uses overpass-api.de query inside the project bounding box.
"""
from __future__ import annotations


def osm_to_georef(project_id: str, bounding_box: list) -> dict:
    raise NotImplementedError("osm_to_georef stub")
