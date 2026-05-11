#!/usr/bin/env python3
"""Fan out a capture event to all 7 platform layers.

Reads the latest mirror_state row, then POSTs SSE notifications to each
subscribed layer (Cesium, ThatOpen, deck.gl, Potree, VW bridge, iTwin
classifier, ERP). Each layer marks its flag true once it has caught up.

Writes one evidence row per layer notified.
"""
from __future__ import annotations


def broadcast(project_id: str, event_kind: str) -> dict:
    raise NotImplementedError("platform-broadcaster stub")
