#!/usr/bin/env -S uv run --with numpy --with pyproj python
"""Fit a 2D affine transform from Vectorworks drawing coordinates to project CRS.

Input JSON shape:
{
  "project_id": "farber-haines-2521",
  "target_crs": {"epsg_code": 2876, "name": "..."},
  "points": [
    {
      "point_id": "parcel_corner_nw",
      "vw_x": 123.4,
      "vw_y": 567.8,
      "lat_wgs84": 40.0,
      "lon_wgs84": -105.2
    }
  ]
}

Each point must provide `vw_x` and `vw_y` plus either:
- `project_x` and `project_y`, or
- `lat_wgs84` and `lon_wgs84`

The script fits:
  project_xy ~= [vw_x, vw_y, 1] @ M

and writes a diagnostic bundle with residuals and a recommended binding patch.
It does NOT mutate Vectorworks or claim the georef is solved automatically.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from pyproj import Transformer


@dataclass
class SolvedPoint:
    point_id: str
    vw_x: float
    vw_y: float
    project_x: float
    project_y: float
    source_note: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Point-pair JSON path")
    parser.add_argument("--output", required=True, help="Output JSON path")
    parser.add_argument(
        "--binding-output",
        required=False,
        help="Optional recommended binding JSON path",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("Input JSON root must be an object.")
    return data


def project_transformer(epsg_code: int) -> Transformer:
    return Transformer.from_crs("EPSG:4326", f"EPSG:{epsg_code}", always_xy=True)


def coerce_points(data: dict[str, Any]) -> tuple[list[SolvedPoint], int]:
    target_crs = data.get("target_crs") or {}
    epsg_code = int(target_crs.get("epsg_code"))
    transformer = project_transformer(epsg_code)
    raw_points = data.get("points")
    if not isinstance(raw_points, list):
        raise ValueError("Input JSON must contain a points array.")

    solved: list[SolvedPoint] = []
    for raw in raw_points:
        if not isinstance(raw, dict):
            continue
        point_id = str(raw.get("point_id") or "").strip()
        if not point_id:
            continue
        vw_x = raw.get("vw_x")
        vw_y = raw.get("vw_y")
        if vw_x is None or vw_y is None:
            continue
        source_note = str(raw.get("source_note") or "").strip()
        if raw.get("project_x") is not None and raw.get("project_y") is not None:
            project_x = float(raw["project_x"])
            project_y = float(raw["project_y"])
        elif raw.get("lat_wgs84") is not None and raw.get("lon_wgs84") is not None:
            project_x, project_y = transformer.transform(
                float(raw["lon_wgs84"]),
                float(raw["lat_wgs84"]),
            )
        else:
            continue
        solved.append(
            SolvedPoint(
                point_id=point_id,
                vw_x=float(vw_x),
                vw_y=float(vw_y),
                project_x=float(project_x),
                project_y=float(project_y),
                source_note=source_note,
            )
        )
    return solved, epsg_code


def fit_affine(points: list[SolvedPoint]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if len(points) < 3:
        raise ValueError("Need at least 3 point pairs to fit a 2D affine transform.")
    src = np.asarray([[p.vw_x, p.vw_y] for p in points], dtype=np.float64)
    tgt = np.asarray([[p.project_x, p.project_y] for p in points], dtype=np.float64)
    src_h = np.hstack([src, np.ones((src.shape[0], 1), dtype=np.float64)])
    m, _, _, _ = np.linalg.lstsq(src_h, tgt, rcond=None)
    a = m[:2, :].T
    b = m[2, :]
    pred = src @ a.T + b
    return a, b, pred


def summarize_transform(a: np.ndarray, b: np.ndarray) -> dict[str, Any]:
    sx = float(np.linalg.norm(a[0]))
    sy = float(np.linalg.norm(a[1]))
    rotation_rad = math.atan2(float(a[1, 0]), float(a[0, 0]))
    rotation_deg = math.degrees(rotation_rad)
    return {
        "matrix_a": a.tolist(),
        "vector_b": b.tolist(),
        "scale_x_project_units_per_vw_unit": sx,
        "scale_y_project_units_per_vw_unit": sy,
        "rotation_deg": rotation_deg,
    }


def residuals(points: list[SolvedPoint], pred: np.ndarray) -> tuple[list[dict[str, Any]], float, float]:
    rows: list[dict[str, Any]] = []
    errors: list[float] = []
    for point, pred_xy in zip(points, pred):
        dx = float(point.project_x - pred_xy[0])
        dy = float(point.project_y - pred_xy[1])
        err = math.hypot(dx, dy)
        errors.append(err)
        rows.append(
            {
                "point_id": point.point_id,
                "vw_x": point.vw_x,
                "vw_y": point.vw_y,
                "project_x": point.project_x,
                "project_y": point.project_y,
                "predicted_project_x": float(pred_xy[0]),
                "predicted_project_y": float(pred_xy[1]),
                "residual_x": dx,
                "residual_y": dy,
                "residual_distance_project_units": err,
                "source_note": point.source_note,
            }
        )
    rmse = math.sqrt(sum(err * err for err in errors) / len(errors))
    max_error = max(errors) if errors else 0.0
    return rows, rmse, max_error


def recommended_binding(
    input_data: dict[str, Any],
    epsg_code: int,
    transform_summary: dict[str, Any],
    rmse: float,
    max_error: float,
) -> dict[str, Any]:
    origin = input_data.get("points", [{}])[0] if input_data.get("points") else {}
    return {
        "_origin": "fit_vw_point_pairs.py recommendation bundle",
        "project_id": input_data.get("project_id"),
        "binding_status": "candidate" if rmse <= 1.0 else "needs_review",
        "allow_apply": False,
        "binding_kind": "affine_point_pair_fit_review_first",
        "epsg_code": epsg_code,
        "target_wgs84_lat": origin.get("lat_wgs84"),
        "target_wgs84_lon": origin.get("lon_wgs84"),
        "transform_summary": transform_summary,
        "fit_rmse_project_units": rmse,
        "fit_max_residual_project_units": max_error,
        "notes": (
            "Review residuals and confirm point-pair truth before mutating "
            "document georeference. This bundle is diagnostic, not authoritative."
        ),
    }


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    binding_output_path = Path(args.binding_output) if args.binding_output else None

    input_data = load_json(input_path)
    points, epsg_code = coerce_points(input_data)
    a, b, pred = fit_affine(points)
    transform_summary = summarize_transform(a, b)
    residual_rows, rmse, max_error = residuals(points, pred)

    output = {
        "project_id": input_data.get("project_id"),
        "source_input": str(input_path),
        "target_epsg_code": epsg_code,
        "point_count": len(points),
        "transform": transform_summary,
        "fit_rmse_project_units": rmse,
        "fit_max_residual_project_units": max_error,
        "residuals": residual_rows,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2)

    if binding_output_path is not None:
        binding_output_path.parent.mkdir(parents=True, exist_ok=True)
        with binding_output_path.open("w", encoding="utf-8") as handle:
            json.dump(
                recommended_binding(
                    input_data=input_data,
                    epsg_code=epsg_code,
                    transform_summary=transform_summary,
                    rmse=rmse,
                    max_error=max_error,
                ),
                handle,
                indent=2,
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
