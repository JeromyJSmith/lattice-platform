#!/usr/bin/env python3
"""Sample 1 frame / N seconds from a drone video as 'keyframes'.

Useful when the full per-frame ingest is overkill (e.g. for a quick scrub).
Sets drone_frames.is_keyframe=true for the sampled rows.
"""
from __future__ import annotations


def extract_keyframes(video_path: str, every_n_sec: float = 2.0) -> int:
    raise NotImplementedError("frame-extractor stub")
