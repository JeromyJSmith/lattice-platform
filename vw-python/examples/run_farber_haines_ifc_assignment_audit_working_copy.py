"""Run the Farber-Haines IFC assignment audit against the active working copy."""

from __future__ import annotations

import os
import runpy


os.environ["MARPA_PROJECT_ROOT"] = "/Volumes/PixelTable/GROVE_HARNESS/juniper2026"

runpy.run_path(
    "/Volumes/PixelTable/GROVE_HARNESS/juniper2026/vw_plugins/audit_ifc_assignment.py",
    run_name="__main__",
)
