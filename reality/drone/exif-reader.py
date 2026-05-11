#!/usr/bin/env python3
"""Read GPS + camera-pose EXIF from a JPG / DNG / TIFF.

Returns a dict with lon/lat/altitude_m/heading/pitch/roll/timestamp.
"""
from __future__ import annotations


def read_exif(image_path: str) -> dict:
    raise NotImplementedError("exif-reader stub — use exifread or piexif")
