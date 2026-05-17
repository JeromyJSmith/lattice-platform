#!/usr/bin/env python3
"""Build a fillable point-pair working file from selected VW reference export.

Input:
- /Users/ojeromyo/Desktop/farber_haines_selected_reference_points.json

Output:
- /Users/ojeromyo/Desktop/farber_haines_point_pairs_working.json

This does not guess world coordinates. It turns exported selected objects and
their vertices into a fillable structure for the georef solve workflow.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path("/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge")
ARTIFACTS_DIR = ROOT / "projects/farber-haines-2521/artifacts/georef"

DEFAULT_INPUT = str(ARTIFACTS_DIR / "farber_haines_selected_reference_points.json")
DEFAULT_OUTPUT = str(ARTIFACTS_DIR / "farber_haines_point_pairs_working.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=DEFAULT_INPUT)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("Selected reference export must be a JSON object.")
    return data


def make_point_id(prefix: str, suffix: str) -> str:
    safe_prefix = "".join(ch if ch.isalnum() else "_" for ch in prefix).strip("_")
    safe_suffix = "".join(ch if ch.isalnum() else "_" for ch in suffix).strip("_")
    return f"{safe_prefix}__{safe_suffix}".strip("_")


def build_points(data: dict[str, Any]) -> list[dict[str, Any]]:
    objects = data.get("objects")
    if not isinstance(objects, list):
        return []
    rows: list[dict[str, Any]] = []
    for item in objects:
        if not isinstance(item, dict):
            continue
        label_bits = [
            str(item.get("name") or "").strip(),
            str(item.get("class_name") or "").strip(),
            str(item.get("layer_name") or "").strip(),
        ]
        label = " | ".join(bit for bit in label_bits if bit) or str(item.get("object_uuid") or "selected_object")
        object_uuid = str(item.get("object_uuid") or "").strip()
        center = item.get("center_point") or {}
        if center.get("x") is not None and center.get("y") is not None:
            rows.append(
                {
                    "point_id": make_point_id(object_uuid or label, "center"),
                    "description": f"{label} center point",
                    "vw_x": center.get("x"),
                    "vw_y": center.get("y"),
                    "lat_wgs84": None,
                    "lon_wgs84": None,
                    "project_x": None,
                    "project_y": None,
                    "source_note": "Fill with matched survey/parcel/OSM control coordinate.",
                    "object_uuid": object_uuid,
                    "geometry_source": "center_point",
                }
            )
        vertices = item.get("vertices") or []
        if not isinstance(vertices, list):
            continue
        for vertex in vertices:
            if not isinstance(vertex, dict):
                continue
            index = vertex.get("index")
            rows.append(
                {
                    "point_id": make_point_id(object_uuid or label, f"vertex_{index}"),
                    "description": f"{label} vertex {index}",
                    "vw_x": vertex.get("x"),
                    "vw_y": vertex.get("y"),
                    "lat_wgs84": None,
                    "lon_wgs84": None,
                    "project_x": None,
                    "project_y": None,
                    "source_note": "Fill with matched survey/parcel/OSM control coordinate.",
                    "object_uuid": object_uuid,
                    "geometry_source": "vertex",
                    "vertex_index": index,
                }
            )
    return rows


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    data = load_json(input_path)
    output = {
        "_purpose": "Fillable VW-to-world point pairs built from selected reference geometry export.",
        "project_id": data.get("project_id", "farber-haines-2521"),
        "source_vwx": data.get("source_vwx"),
        "target_crs": {
            "epsg_code": 2231,
            "name": "NAD83 / Colorado North",
        },
        "points": build_points(data),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
