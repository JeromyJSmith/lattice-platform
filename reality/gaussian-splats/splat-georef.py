#!/usr/bin/env python3
"""Align a 3DGS splat to project_georef.

Two paths:
  - Control points  -> compute rigid + scale transform via least squares
  - ICP             -> register splat origin against terrain DEM / point cloud

Writes transform_to_wgs84 (4x4 row-major) back to the gaussian_splats row.
"""
from __future__ import annotations


def align_splat(splat_path: str, project_id: str, method: str = "control_points") -> dict:
    raise NotImplementedError("splat-georef stub")
