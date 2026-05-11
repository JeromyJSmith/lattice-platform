#!/usr/bin/env python3
"""Run pdal-pipeline.json on a .las / .laz, then PotreeConverter for browser tiles."""
from __future__ import annotations


def ingest_las(las_path: str, project_id: str) -> dict:
    raise NotImplementedError("las-ingest stub — see reality/point-clouds/pdal-pipeline.json")
