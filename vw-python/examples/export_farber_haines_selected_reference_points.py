"""Export selected reference geometry from the active Farber-Haines working copy.

Run inside Vectorworks after selecting the parcel boundary, stakes, survey
markers, or other stable reference objects you want to use for the georef solve.

Outputs:
- /Users/ojeromyo/Desktop/farber_haines_selected_reference_points.json
- /Users/ojeromyo/Desktop/farber_haines_selected_reference_points.csv

This is intentionally geometry-first. It captures raw Vectorworks drawing-space
coordinates so they can be paired with real-world control points later.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Any

import vs  # type: ignore


JSON_PATH = "/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/projects/farber-haines-2521/artifacts/georef/farber_haines_selected_reference_points.json"
CSV_PATH = "/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/projects/farber-haines-2521/artifacts/georef/farber_haines_selected_reference_points.csv"

POLYGON_TYPES = {5, 21}


def safe_str(value: Any) -> str:
    return str(value or "").strip()


def round_coord(value: float) -> float:
    return round(float(value), 6)


def get_handle_uuid(handle: Any) -> str:
    try:
        return safe_str(vs.GetObjectUuid(handle))
    except Exception:
        return ""


def get_class_name(handle: Any) -> str:
    try:
        return safe_str(vs.GetClass(handle))
    except Exception:
        return ""


def get_layer_name(handle: Any) -> str:
    try:
        layer_handle = vs.GetLayer(handle)
        if not layer_handle:
            return ""
        return safe_str(vs.GetLName(layer_handle))
    except Exception:
        return ""


def get_name(handle: Any) -> str:
    try:
        return safe_str(vs.GetName(handle))
    except Exception:
        return ""


def get_plugin_name(handle: Any) -> str:
    try:
        ok, symbol_handle = vs.GetPluginStyleSymbol(handle, None)
        if not ok or not symbol_handle:
            return ""
        return get_name(symbol_handle)
    except Exception:
        return ""


def get_bbox(handle: Any) -> dict[str, float] | None:
    try:
        p1, p2 = vs.GetBBox(handle)
        min_x = min(float(p1[0]), float(p2[0]))
        max_x = max(float(p1[0]), float(p2[0]))
        min_y = min(float(p1[1]), float(p2[1]))
        max_y = max(float(p1[1]), float(p2[1]))
        return {
            "min_x": round_coord(min_x),
            "min_y": round_coord(min_y),
            "max_x": round_coord(max_x),
            "max_y": round_coord(max_y),
            "center_x": round_coord((min_x + max_x) / 2.0),
            "center_y": round_coord((min_y + max_y) / 2.0),
        }
    except Exception:
        return None


def get_center_point(handle: Any) -> dict[str, float] | None:
    bbox = get_bbox(handle)
    if bbox is not None:
        return {
            "x": round_coord(bbox["center_x"]),
            "y": round_coord(bbox["center_y"]),
        }
    try:
        point = vs.Get2DPt(handle, 1)
        return {
            "x": round_coord(point[0]),
            "y": round_coord(point[1]),
        }
    except Exception:
        return None


def get_vertices(handle: Any, type_n: int) -> list[dict[str, float | int]]:
    vertices: list[dict[str, float | int]] = []
    try:
        count = int(vs.GetVertNum(handle) or 0)
    except Exception:
        count = 0
    if count <= 0:
        return vertices

    if type_n == 5:
        for index in range(1, count + 1):
            try:
                point = vs.GetPolyPt(handle, index)
                vertices.append({
                    "index": index,
                    "x": round_coord(point[0]),
                    "y": round_coord(point[1]),
                })
            except Exception:
                continue
        return vertices

    if type_n == 21:
        for index in range(1, count + 1):
            try:
                point, vertex_type, arc_radius = vs.GetPolylineVertex(handle, index)
                vertices.append({
                    "index": index,
                    "x": round_coord(point[0]),
                    "y": round_coord(point[1]),
                    "vertex_type": int(vertex_type),
                    "arc_radius": round_coord(float(arc_radius)),
                })
            except Exception:
                continue
    return vertices


def collect_selected_handles() -> list[Any]:
    handles: list[Any] = []
    vs.ForEachObject(lambda h: handles.append(h), "SEL=TRUE")
    return handles


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def object_signature(items: list[dict[str, Any]]) -> str:
    basis = []
    for item in items:
        basis.append({
            "object_uuid": item.get("object_uuid") or "",
            "name": item.get("name") or "",
            "class_name": item.get("class_name") or "",
            "layer_name": item.get("layer_name") or "",
            "type_n": item.get("type_n") or 0,
            "vertex_count": len(item.get("vertices") or []),
        })
    encoded = json.dumps(basis, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def get_document_georef_snapshot() -> dict[str, Any]:
    document_is_georeferenced = False
    active_layer_is_georeferenced = False
    try:
        document_is_georeferenced = bool(vs.IsGeoreferenced(None))
    except Exception:
        document_is_georeferenced = False
    try:
        active_layer = vs.ActLayer()
        if active_layer:
            active_layer_is_georeferenced = bool(vs.IsGeoreferenced(active_layer))
    except Exception:
        active_layer_is_georeferenced = False
    return {
        "document_is_georeferenced": document_is_georeferenced,
        "active_layer_is_georeferenced": active_layer_is_georeferenced,
    }


def build_payload() -> dict[str, Any]:
    selected = collect_selected_handles()
    items: list[dict[str, Any]] = []
    for handle in selected:
        try:
            type_n = int(vs.GetTypeN(handle))
        except Exception:
            type_n = 0
        bbox = get_bbox(handle)
        item = {
            "object_uuid": get_handle_uuid(handle),
            "name": get_name(handle),
            "class_name": get_class_name(handle),
            "layer_name": get_layer_name(handle),
            "type_n": type_n,
            "center_point": get_center_point(handle),
            "bbox": bbox,
            "vertices": get_vertices(handle, type_n) if type_n in POLYGON_TYPES else [],
        }
        items.append(item)
    source_vwx = safe_str(vs.GetFPathName())
    georef_snapshot = get_document_georef_snapshot()
    return {
        "export_kind": "vectorworks_selected_reference_points",
        "export_version": 2,
        "export_generated_at_utc": now_iso(),
        "project_id": "farber-haines-2521",
        "source_vwx": source_vwx,
        "source_vwx_basename": os.path.basename(source_vwx),
        "georef_snapshot": georef_snapshot,
        "selected_count": len(items),
        "object_signature_sha256": object_signature(items),
        "objects": items,
    }


def write_outputs(payload: dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(JSON_PATH), exist_ok=True)
    with open(JSON_PATH, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)

    headers = [
        "object_uuid",
        "name",
        "class_name",
        "layer_name",
        "type_n",
        "center_x",
        "center_y",
        "bbox_center_x",
        "bbox_center_y",
        "vertex_index",
        "vertex_x",
        "vertex_y",
        "vertex_type",
        "arc_radius",
    ]
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for item in payload["objects"]:
            center = item.get("center_point") or {}
            bbox = item.get("bbox") or {}
            vertices = item.get("vertices") or []
            if not vertices:
                writer.writerow({
                    "object_uuid": item["object_uuid"],
                    "name": item["name"],
                    "class_name": item["class_name"],
                    "layer_name": item["layer_name"],
                    "type_n": item["type_n"],
                    "center_x": center.get("x", ""),
                    "center_y": center.get("y", ""),
                    "bbox_center_x": bbox.get("center_x", ""),
                    "bbox_center_y": bbox.get("center_y", ""),
                    "vertex_index": "",
                    "vertex_x": "",
                    "vertex_y": "",
                    "vertex_type": "",
                    "arc_radius": "",
                })
                continue
            for vertex in vertices:
                writer.writerow({
                    "object_uuid": item["object_uuid"],
                    "name": item["name"],
                    "class_name": item["class_name"],
                    "layer_name": item["layer_name"],
                    "type_n": item["type_n"],
                    "center_x": center.get("x", ""),
                    "center_y": center.get("y", ""),
                    "bbox_center_x": bbox.get("center_x", ""),
                    "bbox_center_y": bbox.get("center_y", ""),
                    "vertex_index": vertex.get("index", ""),
                    "vertex_x": vertex.get("x", ""),
                    "vertex_y": vertex.get("y", ""),
                    "vertex_type": vertex.get("vertex_type", ""),
                    "arc_radius": vertex.get("arc_radius", ""),
                })


def main() -> None:
    payload = build_payload()
    write_outputs(payload)
    vs.AlrtDialog(
        "Exported selected reference points.\n\n"
        f"Selected objects: {payload['selected_count']}\n"
        f"JSON: {JSON_PATH}\n"
        f"CSV: {CSV_PATH}"
    )


if __name__ == "__main__":
    main()
