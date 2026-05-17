"""Hardwire Farber-Haines georef data into the active Vectorworks document.

Run inside Vectorworks 2026 with the Farber-Haines working copy open.

This script deliberately writes the project georef binding into the VWX itself:
- creates/updates a named 2D locus anchor in the document
- attaches a `LATTICE Georef Binding` record to that anchor
- sets the user origin with `SetOriginAbsolute`
- calls `SetDocGeoRefByUsrOrg(EPSG)`
- writes a live selected-reference payload for the downstream gate

It keeps the programmatic path short because Vectorworks runs through the modal
dialog pump.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any

import vs  # type: ignore


ROOT = "/Volumes/PixelTable/VW_iTWIN_Bridge/VW_iTwin_Bridge"
ARTIFACT_DIR = ROOT + "/projects/farber-haines-2521/artifacts/georef"
REPORT_PATH = ARTIFACT_DIR + "/farber_haines_vectorworks_georef_hardwire_report.json"
SELECTED_JSON = ARTIFACT_DIR + "/farber_haines_selected_reference_points.json"
BINDING_JSON = ARTIFACT_DIR + "/document_georef_binding.vectorworks_hardwired.json"

RECORD_NAME = "LATTICE Georef Binding"
ANCHOR_NAME = "LATTICE_GEOREF_anchor_wgs84_reference"
ANCHOR_CLASS = "LATTICE-Georef-Control"
FIELD_TEXT = 4

CONFIG = {
    "project_id": "farber-haines-2521",
    "binding_id": "document_georef_binding_vectorworks_hardwired",
    "binding_kind": "vectorworks_project_hardwire",
    "strategy": "set_user_origin_absolute_then_bind_epsg",
    "control_point_id": "anchor_wgs84_reference",
    "epsg_code": 2231,
    "wgs84_lat": 40.0370784,
    "wgs84_lon": -105.2845774,
    # These are the Vectorworks drawing-space anchor coordinates to bind.
    # They are also written into the VWX record so the project carries its
    # own georef intent instead of depending on Pixeltable-only metadata.
    "anchor_vw_x": 799.4679627382823,
    "anchor_vw_y": -717.2747968857685,
}

PRESET = globals().get("PRESET")
if isinstance(PRESET, dict):
    CONFIG.update(PRESET)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_str(value: Any) -> str:
    return str(value if value is not None else "").strip()


def safe_call(fn: Any, *args: Any, default: Any = None) -> Any:
    try:
        return fn(*args)
    except Exception:
        return default


def round_coord(value: float) -> float:
    return round(float(value), 6)


def ensure_class(name: str) -> None:
    if not name:
        return
    try:
        if not vs.GetObject(name):
            vs.NameClass(name)
    except Exception:
        try:
            vs.NameClass(name)
        except Exception:
            pass


def field_names(record_handle: Any) -> set[str]:
    names: set[str] = set()
    if not record_handle:
        return names
    count = int(safe_call(vs.NumFields, record_handle, default=0) or 0)
    for index in range(1, count + 1):
        name = safe_call(vs.GetFldName, record_handle, index, default="")
        if name:
            names.add(str(name))
    return names


def ensure_record_format() -> None:
    record_handle = safe_call(vs.GetObject, RECORD_NAME, default=None)
    existing = field_names(record_handle)
    fields = [
        ("Project ID", CONFIG["project_id"]),
        ("EPSG", str(CONFIG["epsg_code"])),
        ("Binding ID", CONFIG["binding_id"]),
        ("Strategy", CONFIG["strategy"]),
        ("Control ID", CONFIG["control_point_id"]),
        ("WGS84 Lat", str(CONFIG["wgs84_lat"])),
        ("WGS84 Lon", str(CONFIG["wgs84_lon"])),
        ("VW X", str(CONFIG["anchor_vw_x"])),
        ("VW Y", str(CONFIG["anchor_vw_y"])),
        ("Status", "hardwired"),
        ("Updated UTC", ""),
        ("Source", "Vectorworks"),
    ]
    for name, default in fields:
        if name not in existing:
            vs.NewField(RECORD_NAME, name, str(default), FIELD_TEXT, 0)


def find_or_create_anchor() -> Any:
    anchor = safe_call(vs.GetObject, ANCHOR_NAME, default=None)
    if anchor:
        return anchor

    x = float(CONFIG["anchor_vw_x"])
    y = float(CONFIG["anchor_vw_y"])
    vs.Locus(x, y)
    anchor = vs.LNewObj()
    if anchor:
        safe_call(vs.SetName, anchor, ANCHOR_NAME)
        safe_call(vs.SetClass, anchor, ANCHOR_CLASS)
    return anchor


def attach_binding_record(anchor: Any) -> None:
    vs.SetRecord(anchor, RECORD_NAME)
    values = {
        "Project ID": CONFIG["project_id"],
        "EPSG": str(CONFIG["epsg_code"]),
        "Binding ID": CONFIG["binding_id"],
        "Strategy": CONFIG["strategy"],
        "Control ID": CONFIG["control_point_id"],
        "WGS84 Lat": str(CONFIG["wgs84_lat"]),
        "WGS84 Lon": str(CONFIG["wgs84_lon"]),
        "VW X": str(CONFIG["anchor_vw_x"]),
        "VW Y": str(CONFIG["anchor_vw_y"]),
        "Status": "hardwired",
        "Updated UTC": now_iso(),
        "Source": "Vectorworks active document",
    }
    for field, value in values.items():
        vs.SetRField(anchor, RECORD_NAME, field, str(value))


def bbox_for(handle: Any) -> dict[str, float]:
    try:
        p1, p2 = vs.GetBBox(handle)
        min_x = min(float(p1[0]), float(p2[0]))
        max_x = max(float(p1[0]), float(p2[0]))
        min_y = min(float(p1[1]), float(p2[1]))
        max_y = max(float(p1[1]), float(p2[1]))
    except Exception:
        min_x = max_x = float(CONFIG["anchor_vw_x"])
        min_y = max_y = float(CONFIG["anchor_vw_y"])
    return {
        "min_x": round_coord(min_x),
        "min_y": round_coord(min_y),
        "max_x": round_coord(max_x),
        "max_y": round_coord(max_y),
        "center_x": round_coord((min_x + max_x) / 2.0),
        "center_y": round_coord((min_y + max_y) / 2.0),
    }


def doc_georef_snapshot() -> dict[str, Any]:
    is_georef = bool(safe_call(vs.IsGeoreferenced, None, default=False))
    gis = safe_call(vs.GetGISOriginN, default=None)
    if not (gis and gis[0]):
        gis = safe_call(vs.GetGISOrigin, default=None)
    origin = safe_call(vs.GetOriginInDocUnits, default=None)
    if origin is None:
        origin = safe_call(vs.GetOrigin, default=None)
    return {
        "document_is_georeferenced": is_georef,
        "gis_origin": {
            "lat": float(gis[1]) if gis and gis[0] else None,
            "lon": float(gis[2]) if gis and gis[0] else None,
            "angle_to_north": float(gis[3]) if gis and gis[0] else None,
        },
        "user_origin": {
            "x": float(origin[0]) if origin else None,
            "y": float(origin[1]) if origin else None,
        },
        "epsg_code": int(CONFIG["epsg_code"]),
    }


def write_selected_reference_payload(anchor: Any) -> dict[str, Any]:
    bbox = bbox_for(anchor)
    object_uuid = safe_str(safe_call(vs.GetObjectUuid, anchor, default=""))
    source_vwx = safe_str(safe_call(vs.GetFPathName, default=""))
    layer = safe_call(vs.GetLayer, anchor, default=None)
    payload = {
        "export_kind": "vectorworks_selected_reference_points",
        "export_version": 2,
        "export_generated_at_utc": now_iso(),
        "project_id": CONFIG["project_id"],
        "source_vwx": source_vwx,
        "source_vwx_basename": os.path.basename(source_vwx),
        "georef_snapshot": doc_georef_snapshot(),
        "selected_count": 1,
        "object_signature_sha256": object_uuid or (ANCHOR_NAME + "-vectorworks-hardwired"),
        "objects": [
            {
                "object_uuid": object_uuid or ANCHOR_NAME,
                "name": ANCHOR_NAME,
                "class_name": ANCHOR_CLASS,
                "layer_name": safe_str(safe_call(vs.GetLName, layer, default="")),
                "type_n": int(safe_call(vs.GetTypeN, anchor, default=0) or 0),
                "center_point": {"x": bbox["center_x"], "y": bbox["center_y"]},
                "bbox": bbox,
                "vertices": [],
            }
        ],
    }
    with open(SELECTED_JSON, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    return payload


def write_binding_artifact(snapshot: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "_origin": "Vectorworks hardwire script wrote this from the active VWX",
        "project_id": CONFIG["project_id"],
        "binding_id": CONFIG["binding_id"],
        "binding_status": "runtime_apply",
        "allow_apply": True,
        "binding_kind": CONFIG["binding_kind"],
        "strategy": CONFIG["strategy"],
        "control_point_id": CONFIG["control_point_id"],
        "epsg_code": int(CONFIG["epsg_code"]),
        "target_wgs84_lat": float(CONFIG["wgs84_lat"]),
        "target_wgs84_lon": float(CONFIG["wgs84_lon"]),
        "user_origin_absolute_x": float(CONFIG["anchor_vw_x"]),
        "user_origin_absolute_y": float(CONFIG["anchor_vw_y"]),
        "vectorworks_snapshot": snapshot,
        "notes": (
            "Hardwired into Vectorworks as record data on "
            f"{ANCHOR_NAME}; SetDocGeoRefByUsrOrg({CONFIG['epsg_code']}) was called."
        ),
    }
    with open(BINDING_JSON, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    return payload


def main() -> None:
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    started_at = now_iso()
    result = {
        "ok": False,
        "started_at": started_at,
        "finished_at": "",
        "project_id": CONFIG["project_id"],
        "anchor_name": ANCHOR_NAME,
        "record_name": RECORD_NAME,
        "actions": [],
        "error": "",
    }
    try:
        ensure_class(ANCHOR_CLASS)
        ensure_record_format()
        anchor = find_or_create_anchor()
        if not anchor:
            raise RuntimeError("failed to create or find Vectorworks georef anchor object")
        attach_binding_record(anchor)
        result["actions"].append("attached_vectorworks_georef_record")

        vs.SetOriginAbsolute(float(CONFIG["anchor_vw_x"]), float(CONFIG["anchor_vw_y"]))
        result["actions"].append("set_origin_absolute")

        vs.SetDocGeoRefByUsrOrg(int(CONFIG["epsg_code"]))
        result["actions"].append("set_doc_georef_by_user_origin")

        snapshot = doc_georef_snapshot()
        selected_payload = write_selected_reference_payload(anchor)
        binding_artifact = write_binding_artifact(snapshot)
        result.update(
            {
                "ok": bool(snapshot["document_is_georeferenced"]),
                "doc_snapshot": snapshot,
                "selected_reference_path": SELECTED_JSON,
                "binding_artifact_path": BINDING_JSON,
                "selected_payload": selected_payload,
                "binding_artifact": binding_artifact,
            }
        )
    except Exception as exc:
        result["error"] = repr(exc)
    result["finished_at"] = now_iso()
    with open(REPORT_PATH, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, default=str)


if __name__ == "__main__":
    main()
