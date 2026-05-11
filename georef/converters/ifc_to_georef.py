#!/usr/bin/env python3
"""Extract IfcSite RefLat/RefLon/RefElevation + placement matrix from an IFC
file via IfcOpenShell. Writes ifc_ref_*, ifc_placement_matrix, plus the
canonical lon/lat/elevation_m if no higher-priority source exists.
"""
from __future__ import annotations


def ifc_to_georef(ifc_path: str, project_id: str) -> dict:
    raise NotImplementedError("ifc_to_georef stub — use ifcopenshell.util.placement")
