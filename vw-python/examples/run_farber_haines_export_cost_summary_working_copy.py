"""Export the whole-file Farber-Haines class-level estimate summary."""

from __future__ import annotations


PRESET = {
    "target_layers": [],
}


SCRIPT_PATH = (
    "/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/"
    "vw-python/examples/export_project_cost_summary.py"
)


with open(SCRIPT_PATH, "r", encoding="utf-8") as handle:
    code = compile(handle.read(), SCRIPT_PATH, "exec")
    exec(code, globals(), globals())
