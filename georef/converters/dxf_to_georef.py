#!/usr/bin/env python3
"""DXF (with known origin / scale / rotation) -> project_georef.vw_* fields.

LATTICE doesn't accept Revit/DGN, but DXF from collaborators is fair game.
ezdxf reads headers; user must supply the EPSG separately since DXF carries
no CRS metadata by default.
"""
from __future__ import annotations


def dxf_to_georef(dxf_path: str, project_id: str, origin_lonlat: tuple, epsg: str) -> dict:
    raise NotImplementedError("dxf_to_georef stub")
