"""Run the Farber-Haines estimation apply script against the sandbox layer.

Run inside the Farber-Haines estimation working-copy VWX after creating the
`ZZ_ESTIMATION__L2.01_PLANTING_PLAN` layer.
"""

from __future__ import annotations


PRESET = {
    "csv_path": "/Users/ojeromyo/Desktop/vw_cost_lookup_active_apply.csv",
    "target_layers": ["ZZ_ESTIMATION__L2.01_PLANTING_PLAN"],
}


SCRIPT_PATH = (
    "/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/"
    "vw-python/examples/apply_estimation_mapping_csv.py"
)


with open(SCRIPT_PATH, "r", encoding="utf-8") as handle:
    code = compile(handle.read(), SCRIPT_PATH, "exec")
    exec(code, globals(), globals())
