"""Run estimation mapping against the active Farber-Haines working copy.

This intentionally targets the whole working-copy VWX. The copied file is the
safe destructive boundary, so no layer filter is applied.
"""

from __future__ import annotations


PRESET = {
    "csv_path": "/Users/ojeromyo/Desktop/vw_cost_lookup_active_apply.csv",
    "target_layers": [],
}


SCRIPT_PATH = (
    "/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/"
    "vw-python/examples/apply_estimation_mapping_csv.py"
)


with open(SCRIPT_PATH, "r", encoding="utf-8") as handle:
    code = compile(handle.read(), SCRIPT_PATH, "exec")
    exec(code, globals(), globals())
