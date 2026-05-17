#!/usr/bin/env python3
"""Merge selected VW reference geometry with the authoritative Farber-Haines point package.

This removes most of the manual JSON editing between:
1. exporting selected VW reference geometry, and
2. running the affine fit.

It auto-matches:
- the parcel boundary polygon vertices -> authoritative parcel corners
- selected objects whose names/classes/layers mention benchmark/control ids
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path("/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge")
ARTIFACTS_DIR = ROOT / "projects/farber-haines-2521/artifacts/georef"
DEFAULT_SELECTED = str(ARTIFACTS_DIR / "farber_haines_selected_reference_points.json")
DEFAULT_AUTH = (
    "/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/projects/farber-haines-2521/sources/farber_haines_point_pairs_authoritative_template.json"
)
DEFAULT_OUTPUT = str(ARTIFACTS_DIR / "farber_haines_point_pairs_matched.json")
DEFAULT_SUMMARY = str(ARTIFACTS_DIR / "farber_haines_point_pairs_match_summary.json")

BOUNDARY_HINTS = ("parcel", "property", "boundary", "lot line", "site edge")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selected", default=DEFAULT_SELECTED)
    parser.add_argument("--authoritative", default=DEFAULT_AUTH)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--summary-output", default=DEFAULT_SUMMARY)
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object.")
    return data


def dump_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def validate_selected_payload(selected: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if selected.get("export_kind") != "vectorworks_selected_reference_points":
        errors.append("selected payload export_kind must be `vectorworks_selected_reference_points`.")
    if str(selected.get("project_id") or "") != "farber-haines-2521":
        errors.append("selected payload project_id must be `farber-haines-2521`.")
    source_vwx = str(selected.get("source_vwx") or "").strip()
    if not source_vwx:
        errors.append("selected payload is missing source_vwx.")
    else:
        source_path = Path(source_vwx)
        if source_path.suffix.lower() != ".vwx":
            errors.append(f"selected payload source_vwx is not a VWX path: {source_vwx}")
        if not source_path.exists():
            errors.append(f"selected payload source_vwx does not exist on disk: {source_vwx}")
        if "mock" in source_path.name.lower():
            errors.append(f"selected payload source_vwx looks synthetic: {source_vwx}")
    objects = selected.get("objects")
    if not isinstance(objects, list) or len(objects) == 0:
        errors.append("selected payload must contain a non-empty objects list.")
    selected_count = selected.get("selected_count")
    if int(selected_count or 0) != len(objects or []):
        errors.append(
            f"selected_count mismatch: declared={selected_count}, actual_objects={len(objects or [])}."
        )
    return errors


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def dedupe_vertices(vertices: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[tuple[float, float]] = set()
    for vertex in vertices:
        try:
            key = (round(float(vertex["x"]), 6), round(float(vertex["y"]), 6))
        except Exception:
            continue
        if key in seen:
            continue
        seen.add(key)
        out.append(vertex)
    return out


def object_label(obj: dict[str, Any]) -> str:
    parts = [
        str(obj.get("name") or ""),
        str(obj.get("class_name") or ""),
        str(obj.get("layer_name") or ""),
    ]
    return " | ".join(part for part in parts if part)


def boundary_score(obj: dict[str, Any]) -> tuple[int, float]:
    label = object_label(obj).lower()
    bbox = obj.get("bbox") or {}
    width = float(bbox.get("max_x", 0.0)) - float(bbox.get("min_x", 0.0))
    height = float(bbox.get("max_y", 0.0)) - float(bbox.get("min_y", 0.0))
    area = abs(width * height)
    hint = 0 if any(token in label for token in BOUNDARY_HINTS) else 1
    return (hint, -area)


def pick_boundary_object(objects: list[dict[str, Any]]) -> dict[str, Any] | None:
    polygonish = [obj for obj in objects if len(dedupe_vertices(list(obj.get("vertices") or []))) >= 4]
    if not polygonish:
        return None
    polygonish.sort(key=boundary_score)
    return polygonish[0]


def parcel_corner_points(authoritative_points: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [pt for pt in authoritative_points if str(pt.get("point_id", "")).startswith("parcel_corner_")]


def match_boundary(boundary_obj: dict[str, Any] | None, authoritative_points: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    if boundary_obj is None:
        return [], ["No suitable polygon object found for parcel-boundary matching."]
    source_vertices = dedupe_vertices(list(boundary_obj.get("vertices") or []))
    corners = parcel_corner_points(authoritative_points)
    notes: list[str] = []
    if len(source_vertices) < len(corners):
        notes.append(
            f"Boundary object only yielded {len(source_vertices)} unique vertices for {len(corners)} parcel corners."
        )
    matched: list[dict[str, Any]] = []
    for auth_point, vertex in zip(corners, source_vertices):
        row = dict(auth_point)
        row["vw_x"] = float(vertex["x"])
        row["vw_y"] = float(vertex["y"])
        row["match_source"] = "boundary_vertex_order"
        row["matched_object_uuid"] = boundary_obj.get("object_uuid") or ""
        row["matched_object_label"] = object_label(boundary_obj)
        row["matched_vertex_index"] = vertex.get("index")
        matched.append(row)
    if matched:
        notes.append(
            f"Matched {len(matched)} parcel corners from selected boundary object `{object_label(boundary_obj)}`."
        )
    return matched, notes


def build_token_map(objects: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    mapping: dict[str, dict[str, Any]] = {}
    for obj in objects:
        label = object_label(obj)
        compact = norm(label)
        if compact:
            mapping[compact] = obj
        for raw in re.findall(r"[A-Za-z0-9\-]+", label):
            token = norm(raw)
            if token:
                mapping.setdefault(token, obj)
    return mapping


def center_or_bbox(obj: dict[str, Any]) -> tuple[float | None, float | None]:
    center = obj.get("center_point") or {}
    if center.get("x") is not None and center.get("y") is not None:
        return float(center["x"]), float(center["y"])
    bbox = obj.get("bbox") or {}
    if bbox.get("center_x") is not None and bbox.get("center_y") is not None:
        return float(bbox["center_x"]), float(bbox["center_y"])
    return None, None


def match_named_controls(objects: list[dict[str, Any]], authoritative_points: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    token_map = build_token_map(objects)
    matched: list[dict[str, Any]] = []
    notes: list[str] = []
    used_object_ids: set[str] = set()
    for point in authoritative_points:
        point_id = str(point.get("point_id") or "")
        if point_id.startswith("parcel_corner_"):
            continue
        candidate = token_map.get(norm(point_id))
        if candidate is None:
            continue
        object_uuid = str(candidate.get("object_uuid") or "")
        if object_uuid and object_uuid in used_object_ids:
            continue
        vw_x, vw_y = center_or_bbox(candidate)
        if vw_x is None or vw_y is None:
            continue
        row = dict(point)
        row["vw_x"] = vw_x
        row["vw_y"] = vw_y
        row["match_source"] = "name_class_layer_token"
        row["matched_object_uuid"] = object_uuid
        row["matched_object_label"] = object_label(candidate)
        matched.append(row)
        if object_uuid:
            used_object_ids.add(object_uuid)
    notes.append(f"Matched {len(matched)} named control / benchmark rows from selected objects.")
    return matched, notes


def merge_matches(authoritative: dict[str, Any], selected: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    validation_errors = validate_selected_payload(selected)
    if validation_errors:
        raise ValueError("Invalid selected VW reference payload:\n- " + "\n- ".join(validation_errors))
    authoritative_points = list(authoritative.get("points") or [])
    objects = list(selected.get("objects") or [])
    boundary_obj = pick_boundary_object(objects)

    boundary_rows, boundary_notes = match_boundary(boundary_obj, authoritative_points)
    control_rows, control_notes = match_named_controls(objects, authoritative_points)

    matched_by_id: dict[str, dict[str, Any]] = {}
    for row in boundary_rows + control_rows:
        matched_by_id[str(row.get("point_id") or "")] = row

    points_out: list[dict[str, Any]] = []
    unmatched_ids: list[str] = []
    for point in authoritative_points:
        point_id = str(point.get("point_id") or "")
        if point_id in matched_by_id:
            points_out.append(matched_by_id[point_id])
        else:
            points_out.append(dict(point))
            unmatched_ids.append(point_id)

    summary = {
        "project_id": authoritative.get("project_id"),
        "selected_source": selected.get("source_vwx"),
        "selected_source_basename": selected.get("source_vwx_basename") or Path(str(selected.get("source_vwx") or "")).name,
        "selected_export_generated_at_utc": selected.get("export_generated_at_utc"),
        "selected_export_version": selected.get("export_version"),
        "selected_object_signature_sha256": selected.get("object_signature_sha256"),
        "selected_document_is_georeferenced": ((selected.get("georef_snapshot") or {}).get("document_is_georeferenced")),
        "selected_active_layer_is_georeferenced": ((selected.get("georef_snapshot") or {}).get("active_layer_is_georeferenced")),
        "selected_count": selected.get("selected_count"),
        "matched_count": len(matched_by_id),
        "matched_point_ids": sorted(matched_by_id),
        "unmatched_point_ids": unmatched_ids,
        "boundary_object_label": object_label(boundary_obj) if boundary_obj else "",
        "notes": boundary_notes + control_notes,
    }

    output = {
        "_purpose": (
            "Fit-ready Farber-Haines point pairs merged from selected VW reference geometry "
            "and the authoritative world-side control package."
        ),
        "project_id": authoritative.get("project_id"),
        "target_crs": authoritative.get("target_crs"),
        "authoritative_sources": authoritative.get("sources"),
        "selected_export_generated_at_utc": selected.get("export_generated_at_utc"),
        "selected_export_version": selected.get("export_version"),
        "selected_object_signature_sha256": selected.get("object_signature_sha256"),
        "selected_source_vwx": selected.get("source_vwx"),
        "points": points_out,
    }
    return output, summary


def main() -> int:
    args = parse_args()
    selected = load_json(Path(args.selected))
    authoritative = load_json(Path(args.authoritative))
    output, summary = merge_matches(authoritative, selected)
    dump_json(Path(args.output), output)
    dump_json(Path(args.summary_output), summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
