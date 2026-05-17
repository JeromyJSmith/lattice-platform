"""Run the Farber-Haines document georeference script in dry-run mode.

Targets the active Farber-Haines estimation working copy while writing audit
artifacts into the established GROVE_HARNESS juniper2026 tree.
"""

from __future__ import annotations

import os
import runpy


os.environ["MARPA_PROJECT_ROOT"] = "/Volumes/PixelTable/GROVE_HARNESS/juniper2026"
os.environ["APPLY_DOCUMENT_GEOREF_FORCE_MODE"] = "dry_run"

runpy.run_path(
    "/Volumes/PixelTable/GROVE_HARNESS/juniper2026/vw_plugins/apply_document_georef.py",
    run_name="__main__",
)
