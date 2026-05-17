#!/usr/bin/env python3
"""Run the Farber-Haines post-export georef cycle.

Default behavior is dry-run:
1. build matched point pairs from the latest selected VW export
2. run the affine fit if enough matched rows exist
3. inspect fit quality and report whether apply-to-Pixeltable is allowed

Use `--apply-fit` to actually write the fit candidate into
`lattice/bridge/project_georef`, but only if the fit passes thresholds.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path("/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge")
ARTIFACTS_DIR = ROOT / "projects/farber-haines-2521/artifacts/georef"
POST_EXPORT_RUNNER = ROOT / "georef/converters/run_farber_haines_georef_post_export.py"
APPLY_FIT_SCRIPT = ROOT / "pixeltable/scripts/apply_farber_haines_georef_fit.py"
PIXELTABLE_PYTHON = ROOT / "pixeltable/.venv/bin/python"
MATCH_SUMMARY_JSON = ARTIFACTS_DIR / "farber_haines_point_pairs_match_summary.json"
FIT_JSON = Path("/tmp/farber_haines_georef_fit.json")
BINDING_JSON = Path("/tmp/farber_haines_georef_binding_candidate.json")
REPORT_JSON = Path("/tmp/farber_haines_georef_cycle_report.json")
ARTIFACT_REPORT_JSON = ARTIFACTS_DIR / "farber_haines_georef_cycle_report.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply-fit", action="store_true")
    parser.add_argument("--max-rmse", type=float, default=5.0)
    parser.add_argument("--max-residual", type=float, default=15.0)
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_post_export() -> dict[str, Any]:
    python_exe = sys.executable or "python3"
    result = subprocess.run(
        [python_exe, str(POST_EXPORT_RUNNER)],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return json.loads(result.stdout)
    stdout = (result.stdout or "").strip()
    stderr = (result.stderr or "").strip()
    raise RuntimeError(
        "post-export georef run failed"
        + (f": {stderr}" if stderr else "")
        + (f" | stdout={stdout}" if stdout else "")
    )


def run_apply_fit(max_rmse: float, max_residual: float) -> dict[str, Any]:
    result = subprocess.run(
        [
            str(PIXELTABLE_PYTHON),
            str(APPLY_FIT_SCRIPT),
            "--max-rmse",
            str(max_rmse),
            "--max-residual",
            str(max_residual),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def main() -> int:
    args = parse_args()
    try:
        post_export = run_post_export()
    except Exception as exc:
        report = {
            "ok": False,
            "dry_run": not bool(args.apply_fit),
            "apply_requested": bool(args.apply_fit),
            "apply_performed": False,
            "apply_block_reason": "Post-export run failed before fit evaluation.",
            "thresholds": {
                "max_rmse": args.max_rmse,
                "max_residual": args.max_residual,
            },
            "post_export": None,
            "match_summary": {},
            "fit_summary": {
                "fit_run": False,
                "matched_point_count": 0,
                "fit_json": "",
                "binding_json": "",
                "rmse": None,
                "max_residual": None,
                "binding_status": "",
                "thresholds_pass": False,
            },
            "apply_result": None,
            "error": str(exc),
        }
        ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        REPORT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")
        ARTIFACT_REPORT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps(report, indent=2))
        return 1
    match_summary = load_json(MATCH_SUMMARY_JSON) if MATCH_SUMMARY_JSON.exists() else {}
    fit = load_json(FIT_JSON) if FIT_JSON.exists() else {}
    binding = load_json(BINDING_JSON) if BINDING_JSON.exists() else {}

    matched_point_count = int(post_export.get("matched_point_count") or 0)
    fit_run = bool(post_export.get("fit_run"))
    fit_rmse = float(fit.get("fit_rmse_project_units") or 0.0) if fit_run else None
    fit_max_residual = float(fit.get("fit_max_residual_project_units") or 0.0) if fit_run else None

    thresholds_pass = bool(
        fit_run
        and fit_rmse is not None
        and fit_max_residual is not None
        and fit_rmse <= args.max_rmse
        and fit_max_residual <= args.max_residual
    )

    apply_requested = bool(args.apply_fit)
    apply_performed = False
    apply_result: dict[str, Any] | None = None
    apply_block_reason = ""

    if apply_requested:
        if not fit_run:
            apply_block_reason = "Fit did not run, so there is nothing to apply."
        elif not thresholds_pass:
            apply_block_reason = (
                f"Fit quality failed thresholds: rmse={fit_rmse}, max_residual={fit_max_residual}, "
                f"required rmse<={args.max_rmse} and max_residual<={args.max_residual}."
            )
        else:
            try:
                apply_result = run_apply_fit(args.max_rmse, args.max_residual)
                apply_performed = True
            except Exception as exc:
                apply_block_reason = f"Fit apply failed: {exc}"
                apply_performed = False

    report = {
        "ok": True,
        "dry_run": not apply_requested,
        "apply_requested": apply_requested,
        "apply_performed": apply_performed,
        "apply_block_reason": apply_block_reason,
        "thresholds": {
            "max_rmse": args.max_rmse,
            "max_residual": args.max_residual,
        },
        "post_export": post_export,
        "match_summary": match_summary,
        "fit_summary": {
            "fit_run": fit_run,
            "matched_point_count": matched_point_count,
            "fit_json": str(FIT_JSON) if FIT_JSON.exists() else "",
            "binding_json": str(BINDING_JSON) if BINDING_JSON.exists() else "",
            "rmse": fit_rmse,
            "max_residual": fit_max_residual,
            "binding_status": binding.get("binding_status") if binding else "",
            "thresholds_pass": thresholds_pass,
        },
        "apply_result": apply_result,
    }

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")
    ARTIFACT_REPORT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
