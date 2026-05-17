#!/usr/bin/env python3
"""Run the default Farber-Haines point-pair fit workflow.

Inputs:
- /Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/projects/farber-haines-2521/artifacts/georef/farber_haines_point_pairs_working.json

Outputs:
- /tmp/farber_haines_georef_fit.json
- /tmp/farber_haines_georef_binding_candidate.json
"""

from __future__ import annotations

import runpy
import sys


TARGET = (
    "/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/"
    "georef/converters/fit_vw_point_pairs.py"
)
ARTIFACTS_DIR = "/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/projects/farber-haines-2521/artifacts/georef"

sys.argv = [
    TARGET,
    "--input",
    f"{ARTIFACTS_DIR}/farber_haines_point_pairs_working.json",
    "--output",
    "/tmp/farber_haines_georef_fit.json",
    "--binding-output",
    "/tmp/farber_haines_georef_binding_candidate.json",
]

runpy.run_path(TARGET, run_name="__main__")
