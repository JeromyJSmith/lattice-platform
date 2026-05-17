"""Export Farber-Haines object-level estimate rows from the sandbox layer."""

from __future__ import annotations


PRESET = {
    "target_layers": ["ZZ_ESTIMATION__L2.01_PLANTING_PLAN"],
}


SCRIPT_PATH = (
    "/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/"
    "vw-python/examples/export_project_cost_object_rows.py"
)


with open(SCRIPT_PATH, "r", encoding="utf-8") as handle:
    code = compile(handle.read(), SCRIPT_PATH, "exec")
    exec(code, globals(), globals())
