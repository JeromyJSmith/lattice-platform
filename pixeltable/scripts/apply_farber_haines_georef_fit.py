#!/usr/bin/env -S uv run python
"""Apply a Farber-Haines georef fit result into the live project_georef row.

This upgrades the existing provisional seed with VW transform evidence from
`fit_vw_point_pairs.py`, but keeps the row explicitly review-first.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))

from scripts._pxt_env import get_client  # noqa: E402


PROJECT_ID = "farber-haines-2521"
TABLE_PATH = "lattice/bridge/project_georef"
FIT_PATH = Path("/tmp/farber_haines_georef_fit.json")
BINDING_CANDIDATE_PATH = Path("/tmp/farber_haines_georef_binding_candidate.json")
CONFIG_SEED_PATH = Path(
    "/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/projects/farber-haines-2521/georef.config.seed.json"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-rmse", type=float, default=5.0)
    parser.add_argument("--max-residual", type=float, default=15.0)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def now() -> datetime:
    return datetime.now(timezone.utc)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True)


def fetch_current_row(table: Any) -> dict[str, Any]:
    rows = list(table.where(table.project_id == PROJECT_ID).limit(1).collect())
    if not rows:
        raise SystemExit(f"no project_georef row found for {PROJECT_ID}")
    return rows[0]


def row_id(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("id") or "")
    return str(value or "")


def compute_hash(seed: dict[str, Any], fit: dict[str, Any], binding_candidate: dict[str, Any]) -> str:
    payload = {
        "seed": seed,
        "fit": fit,
        "binding_candidate": binding_candidate,
    }
    return hashlib.sha256(dump_json(payload).encode("utf-8")).hexdigest()


def merged_notes(current_notes: str, fit: dict[str, Any]) -> str:
    rmse = fit.get("fit_rmse_project_units")
    max_residual = fit.get("fit_max_residual_project_units")
    extra = (
        f" Georef fit candidate applied from point-pair solve; "
        f"rmse={rmse}, max_residual={max_residual}. "
        "This remains review-first until validated against Cesium/iTwin/IFC."
    )
    return (current_notes or "").strip() + extra


def main() -> int:
    args = parse_args()
    if not FIT_PATH.exists():
        raise SystemExit(f"missing fit file: {FIT_PATH}")
    if not CONFIG_SEED_PATH.exists():
        raise SystemExit(f"missing config seed file: {CONFIG_SEED_PATH}")

    fit = load_json(FIT_PATH)
    binding_candidate = load_json(BINDING_CANDIDATE_PATH) if BINDING_CANDIDATE_PATH.exists() else {}
    seed = load_json(CONFIG_SEED_PATH)
    fit_rmse = float(fit.get("fit_rmse_project_units") or 0.0)
    fit_max_residual = float(fit.get("fit_max_residual_project_units") or 0.0)
    thresholds_pass = fit_rmse <= args.max_rmse and fit_max_residual <= args.max_residual

    if not thresholds_pass and not args.force:
        raise SystemExit(
            "refusing to apply georef fit candidate because thresholds failed: "
            f"rmse={fit_rmse}, max_residual={fit_max_residual}, "
            f"required rmse<={args.max_rmse} and max_residual<={args.max_residual}; "
            "re-run with --force only if you explicitly want to bypass this guard."
        )

    pxt = get_client()
    table = pxt.get_table(TABLE_PATH)
    current = fetch_current_row(table)

    transform = fit.get("transform") or {}
    fit_hash = compute_hash(seed, fit, binding_candidate)
    timestamp = now()

    updated = dict(current)
    updated["id"] = uuid.uuid4().hex
    updated["config_file_hash"] = fit_hash
    updated["config_version"] = "farber-haines-fit-candidate-v1"
    updated["vw_origin_x"] = seed.get("vw_internal", {}).get("origin_x")
    updated["vw_origin_y"] = seed.get("vw_internal", {}).get("origin_y")
    updated["vw_scale"] = transform.get("scale_x_project_units_per_vw_unit")
    updated["vw_rotation_deg"] = transform.get("rotation_deg")
    updated["vw_units"] = "document_units_review_required"
    updated["transform_vw_to_wgs84"] = dump_json({
        "target_epsg_code": fit.get("target_epsg_code"),
        "transform": transform,
        "fit_rmse_project_units": fit.get("fit_rmse_project_units"),
        "fit_max_residual_project_units": fit.get("fit_max_residual_project_units"),
        "residuals": fit.get("residuals"),
    })
    updated["notes"] = merged_notes(str(current.get("notes") or ""), fit)
    updated["updated_at"] = timestamp

    current_created = current.get("created_at")
    if current_created is None:
        updated["created_at"] = timestamp
    else:
        updated["created_at"] = current_created

    table.delete(table.project_id == PROJECT_ID)
    table.insert([updated])
    print(json.dumps({
        "ok": True,
        "table": TABLE_PATH,
        "project_id": PROJECT_ID,
        "config_version": updated["config_version"],
        "fit_rmse_project_units": fit_rmse,
        "fit_max_residual_project_units": fit_max_residual,
        "thresholds_pass": thresholds_pass,
        "force": bool(args.force),
    }, default=str, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
