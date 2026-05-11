#!/usr/bin/env python3
"""Classify vegetation returns from a point cloud (LASrange + height filter).

Writes back to point_cloud_sessions.classified_veg_pct.
"""
from __future__ import annotations


def classify_vegetation(las_path: str, session_id: str) -> dict:
    raise NotImplementedError("classify-vegetation stub")
