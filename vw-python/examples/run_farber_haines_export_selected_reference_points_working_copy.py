"""Run selected-reference-point export against the active Farber-Haines working copy."""

from __future__ import annotations


SCRIPT_PATH = (
    "/Volumes/PixelTable/VW_iTwin_Bridge/VW_iTwin_Bridge/"
    "vw-python/examples/export_farber_haines_selected_reference_points.py"
)


with open(SCRIPT_PATH, "r", encoding="utf-8") as handle:
    code = compile(handle.read(), SCRIPT_PATH, "exec")
    exec(code, globals(), globals())
