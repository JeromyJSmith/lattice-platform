#!/usr/bin/env python3
"""DBSCAN on vegetation returns -> tree crown centroids -> existing_trees rows.

Open3D + scikit-learn DBSCAN on the veg-classified subset. Output goes to a
future lattice/bridge/existing_trees table; until that table exists, the
script writes to lattice/execution/evidence for audit.
"""
from __future__ import annotations


def extract_trees(las_path: str, project_id: str) -> dict:
    raise NotImplementedError("extract-trees stub")
