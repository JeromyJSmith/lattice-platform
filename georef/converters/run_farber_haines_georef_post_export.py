#!/usr/bin/env python3
"""Project-specific post-export georef runner for Farber-Haines.

This script assumes the selected VW reference geometry has already been exported
from the working-copy VWX. It then:
1. builds the matched point-pair file from the authoritative world-side package
2. optionally runs the affine fit when at least 3 rows have VW coordinates
"""

from __future__ import annotations

import json
import runpy
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path("/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge")
ARTIFACTS_DIR = ROOT / "projects/farber-haines-2521/artifacts/georef"
PROJECT_ID = "farber-haines-2521"

MATCHER = ROOT / "georef/converters/build_farber_haines_matched_point_pairs.py"
FITTER = ROOT / "georef/converters/fit_vw_point_pairs.py"
PIXELTABLE_VENV_PYTHON = ROOT / "pixeltable/.venv/bin/python"

SELECTED_JSON = ARTIFACTS_DIR / "farber_haines_selected_reference_points.json"
AUTHORITATIVE_JSON = ROOT / "projects/farber-haines-2521/sources/farber_haines_point_pairs_authoritative_template.json"
MATCHED_JSON = ARTIFACTS_DIR / "farber_haines_point_pairs_matched.json"
MATCH_SUMMARY_JSON = ARTIFACTS_DIR / "farber_haines_point_pairs_match_summary.json"
FIT_JSON = Path("/tmp/farber_haines_georef_fit.json")
BINDING_JSON = Path("/tmp/farber_haines_georef_binding_candidate.json")
PIXELTABLE_PG_SOCKET = "/Volumes/PixelTable/.pixeltable/pgdata"
PIXELTABLE_PG_PORT = "5432"
PIXELTABLE_PG_USER = "postgres"
PIXELTABLE_PG_DB = "pixeltable"
VECTORWORKS_EXPORTS_INTERNAL_TABLE = "tbl_7312d40ab75b4bb4905d7300a6ee5e5d"


def selected_payload_from_table() -> dict | None:
    sql = (
        "select col_17::text from "
        f"{VECTORWORKS_EXPORTS_INTERNAL_TABLE} "
        "where coalesce(col_17::jsonb->>'project_id','') = "
        f"'{PROJECT_ID}' "
        "and coalesce(col_17::jsonb->>'export_kind','') = "
        "'vectorworks_selected_reference_points' "
        "order by rowid desc limit 1;"
    )
    result = subprocess.run(
        [
            "psql",
            "-P",
            "pager=off",
            "-tA",
            "-h",
            PIXELTABLE_PG_SOCKET,
            "-p",
            PIXELTABLE_PG_PORT,
            "-U",
            PIXELTABLE_PG_USER,
            "-d",
            PIXELTABLE_PG_DB,
            "-c",
            sql,
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    raw = (result.stdout or "").strip()
    if not raw:
        return None
    try:
        payload = json.loads(raw)
    except Exception:
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def resolve_selected_payload() -> tuple[dict, str]:
    payload = selected_payload_from_table()
    if payload is not None:
        SELECTED_JSON.parent.mkdir(parents=True, exist_ok=True)
        SELECTED_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload, "pixeltable_table"
    if SELECTED_JSON.exists():
        payload = json.loads(SELECTED_JSON.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            return payload, "artifact_json"
    raise SystemExit(
        "missing selected reference export in both PixelTable table "
        f"({VECTORWORKS_EXPORTS_INTERNAL_TABLE}) and artifact JSON: {SELECTED_JSON}"
    )


def run_matcher() -> None:
    run_script(
        MATCHER,
        [
            str(MATCHER),
            "--selected",
            str(SELECTED_JSON),
            "--authoritative",
            str(AUTHORITATIVE_JSON),
            "--output",
            str(MATCHED_JSON),
            "--summary-output",
            str(MATCH_SUMMARY_JSON),
        ],
    )


def matched_count(path: Path) -> int:
    payload = json.loads(path.read_text(encoding="utf-8"))
    points = payload.get("points") or []
    return sum(
        1
        for point in points
        if point.get("vw_x") is not None and point.get("vw_y") is not None
    )


def run_fit() -> None:
    uv_bin = shutil.which("uv") or "/Users/ojeromyo/.local/bin/uv"
    if Path(uv_bin).exists():
        cmd = [
            uv_bin,
            "run",
            "--with",
            "numpy",
            "--with",
            "pyproj",
            "python",
            str(FITTER),
            "--input",
            str(MATCHED_JSON),
            "--output",
            str(FIT_JSON),
            "--binding-output",
            str(BINDING_JSON),
        ]
    else:
        cmd = [
            str(PIXELTABLE_VENV_PYTHON),
            str(FITTER),
            "--input",
            str(MATCHED_JSON),
            "--output",
            str(FIT_JSON),
            "--binding-output",
            str(BINDING_JSON),
        ]
    subprocess.run(cmd, check=True)


def run_script(path: Path, argv: list[str]) -> None:
    sys.argv = argv
    try:
        runpy.run_path(str(path), run_name="__main__")
    except SystemExit as exc:
        code = exc.code
        if code not in (None, 0):
            raise


def main() -> int:
    _, selected_source = resolve_selected_payload()
    if not AUTHORITATIVE_JSON.exists():
        raise SystemExit(f"missing authoritative point package: {AUTHORITATIVE_JSON}")

    run_matcher()
    count = matched_count(MATCHED_JSON)
    result = {
        "ok": True,
        "selected_json": str(SELECTED_JSON),
        "selected_source": selected_source,
        "authoritative_json": str(AUTHORITATIVE_JSON),
        "matched_json": str(MATCHED_JSON),
        "match_summary_json": str(MATCH_SUMMARY_JSON),
        "selected_export_generated_at_utc": "",
        "selected_object_signature_sha256": "",
        "matched_point_count": count,
        "fit_run": False,
        "fit_json": "",
        "binding_json": "",
        "notes": "",
    }
    summary_payload = json.loads(MATCH_SUMMARY_JSON.read_text(encoding="utf-8"))
    result["selected_export_generated_at_utc"] = str(summary_payload.get("selected_export_generated_at_utc") or "")
    result["selected_object_signature_sha256"] = str(summary_payload.get("selected_object_signature_sha256") or "")
    if count >= 3:
        run_fit()
        result["fit_run"] = True
        result["fit_json"] = str(FIT_JSON)
        result["binding_json"] = str(BINDING_JSON)
        result["notes"] = "Fit ran because at least 3 matched points were available."
    else:
        result["notes"] = "Fit skipped because fewer than 3 matched points were available."

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
