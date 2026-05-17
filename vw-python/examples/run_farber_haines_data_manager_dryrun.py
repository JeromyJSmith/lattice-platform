"""Run the Farber-Haines Data Manager sync in dry-run mode inside Vectorworks."""

from __future__ import annotations

import os
import runpy
import sys


ROOT = os.path.dirname(__file__)
TARGET = os.path.join(ROOT, "farber_haines_data_manager_sync.py")

sys.argv = [
    TARGET,
    "--mode",
    "apply",
    "--spec",
    "/tmp/farber_haines_data_manager_mapping_spec.json",
    "--out",
    "/tmp/farber_haines_data_manager_sync_dryrun.json",
    "--dry-run",
]

runpy.run_path(TARGET, run_name="__main__")
