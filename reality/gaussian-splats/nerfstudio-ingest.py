#!/usr/bin/env python3
"""Ingest a nerfstudio export directory into lattice/reality/gaussian_splats.

Expects a nerfstudio output with transforms.json + splat.ply.
"""
from __future__ import annotations


def ingest_nerfstudio(export_dir: str, project_id: str, flight_id: str | None) -> dict:
    raise NotImplementedError("nerfstudio-ingest stub")
