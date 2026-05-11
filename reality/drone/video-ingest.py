#!/usr/bin/env python3
"""Stream-ingest a drone .mp4: ffmpeg pipes frames; per-frame extract GPS EXIF
+ insert a row into lattice/reality/drone_frames (image column + georef).

Non-blocking: frames flow into Pixeltable as ffmpeg decodes them. The
sidecar's worker.py polls drone_frames for newly-inserted rows and runs
CLIP/YOLO computed columns on each.

Stub. Acceptance criteria on issue 'Drone video streaming ingest'.
"""
from __future__ import annotations


def ingest_video(video_path: str, flight_id: str, project_id: str) -> dict:
    raise NotImplementedError("drone video-ingest stub")
