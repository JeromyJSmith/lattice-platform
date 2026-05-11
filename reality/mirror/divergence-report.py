#!/usr/bin/env python3
"""Cloud-to-cloud divergence: design ThatOpen mesh -> reality point cloud / splat.

Uses CloudComPy (the Python binding to CloudCompare's C2C tool). Writes
mirror_state.design_reality_divergence_m + a per-element divergence column.
"""
from __future__ import annotations


def compute_divergence(project_id: str) -> dict:
    raise NotImplementedError("divergence-report stub")
