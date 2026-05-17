#!/usr/bin/env -S uv run --with pyproj python
"""Run the Farber-Haines live georef update sequence.

Order:
1. Apply survey CSV control into project_georef
2. Apply fitted VW transform into the same row

This is the intended project-specific path once:
- a real survey CSV exists
- a real point-pair fit has been generated
"""

from __future__ import annotations

import argparse
import runpy
import sys


SURVEY_TARGET = (
    "/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/"
    "pixeltable/scripts/apply_farber_haines_survey_csv.py"
)
FIT_TARGET = (
    "/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/"
    "pixeltable/scripts/apply_farber_haines_georef_fit.py"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path")
    parser.add_argument("--source-epsg", default="EPSG:2876")
    parser.add_argument(
        "--skip-fit",
        action="store_true",
        help="Only apply survey CSV, do not apply /tmp fit result.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    sys.argv = [
        SURVEY_TARGET,
        args.csv_path,
        "--source-epsg",
        args.source_epsg,
    ]
    runpy.run_path(SURVEY_TARGET, run_name="__main__")

    if not args.skip_fit:
        sys.argv = [FIT_TARGET]
        runpy.run_path(FIT_TARGET, run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
