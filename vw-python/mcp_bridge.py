"""VW MCP bridge — controls Vectorworks 2026 via AppleScript 'run Python script'.

No file dialog. No TCP server. No infinite loop inside VW.
Each tool call runs a one-shot Python script inside VW via AppleScript and
reads the result from a temp file. VW briefly pauses per call (~100-500 ms).

Registered in .mcp.json as "vectorworks".
VW must be running. A blank document is opened automatically if none is open.

Run via .mcp.json (stdio transport):
    uv run --with fastmcp vw-python/mcp_bridge.py
"""

import json
import os
import subprocess
import tempfile

from fastmcp import FastMCP

_VW_APP = "Vectorworks 2026"
_TIMEOUT = 30

mcp = FastMCP(
    "vectorworks",
    instructions=(
        "Controls a live Vectorworks 2026 document via AppleScript. "
        "VW must be running. Call vw_ping first. "
        "VW auto-opens a blank document if none is open."
    ),
)


def _run_in_vw(body: str, timeout: int = _TIMEOUT) -> object:
    """Run a one-shot Python script inside VW; return the value of `_result`.

    Writes the script to a temp file so AppleScript reads it with real newlines
    intact — json.dumps() would escape \\n to literal backslash-n which breaks
    Python's multi-statement parser inside VW.
    """
    result_path = tempfile.mktemp(suffix=".json", prefix="vwmcp_")
    script_path = tempfile.mktemp(suffix=".py",   prefix="vwscript_")
    script = (
        "import json as _json, vs\n"
        + body
        + f"\nwith open({json.dumps(result_path)}, 'w') as _f: _json.dump(_result, _f)\n"
    )
    with open(script_path, "w") as f:
        f.write(script)
    # AppleScript reads the file → real newlines → VW gets valid Python source
    apple = (
        f"set _s to read POSIX file {json.dumps(script_path)}\n"
        f"tell application {json.dumps(_VW_APP)} to run Python script _s"
    )
    try:
        subprocess.run(["osascript", "-e", apple], timeout=timeout, capture_output=True)
        with open(result_path) as f:
            return json.load(f)
    finally:
        for p in (script_path, result_path):
            try:
                os.unlink(p)
            except FileNotFoundError:
                pass


def _ensure_document():
    """Open a blank VW document if none is open."""
    import time
    try:
        has_doc = _run_in_vw("_result = bool(vs.ActLayer())", timeout=8)
    except Exception:
        has_doc = False
    if not has_doc:
        subprocess.run(
            ["osascript", "-e",
             'tell application "System Events" to tell process "Vectorworks" '
             'to click menu item "New..." of menu "File" of menu bar 1'],
            timeout=5, capture_output=True,
        )
        time.sleep(2)
        subprocess.run(
            ["osascript", "-e",
             'tell application "System Events" to key code 36'],
            timeout=3, capture_output=True,
        )
        time.sleep(2)


# ── tools ──────────────────────────────────────────────────────────────────────

@mcp.tool()
def vw_ping() -> str:
    """Check that Vectorworks is running and responds to AppleScript."""
    r = subprocess.run(
        ["osascript", "-e", f'tell application {json.dumps(_VW_APP)} to return name'],
        capture_output=True, text=True, timeout=5,
    )
    if r.returncode == 0 and "Vectorworks" in r.stdout:
        return "pong"
    raise RuntimeError("Vectorworks is not running or not responding")


@mcp.tool()
def vw_ensure_document() -> str:
    """Open a blank document if none is open. Call before other tools if needed."""
    _ensure_document()
    return "document ready"


@mcp.tool()
def vw_get_drawing_info() -> dict:
    """Return the active document name and file path."""
    _ensure_document()
    return _run_in_vw("_result = {'file_path': vs.GetFPathName(), 'doc_name': vs.GetFName()}")


@mcp.tool()
def vw_list_layers() -> list:
    """List all layers with name and visibility."""
    _ensure_document()
    return _run_in_vw("""
try:
    layers = []
    layer = vs.FLayer()
    while layer:
        layers.append({'name': vs.GetLName(layer), 'visible': vs.GetLVis(layer) == 0})
        layer = vs.NextLayer(layer)
    _result = layers
except Exception as e:
    _result = [{'fatal': str(e)}]
""")


@mcp.tool()
def vw_list_objects_on_layer(layer: str) -> list:
    """List every object on a named design layer.

    Args:
        layer: Exact layer name as shown in the Layers palette.
    """
    _ensure_document()
    return _run_in_vw(f"""
try:
    layer_name = {json.dumps(layer)}
    target = None
    lyr = vs.FLayer()
    while lyr:
        if vs.GetLName(lyr) == layer_name:
            target = lyr
            break
        lyr = vs.NextLayer(lyr)
    objects = []
    if target:
        h = vs.FInLayer(target)
        i = 0
        while h and i < 500:
            try:
                obj = {{'type': vs.GetTypeN(h), 'name': vs.GetName(h), 'num_records': vs.NumRecords(h)}}
            except Exception as oe:
                obj = {{'error': str(oe)}}
            objects.append(obj)
            h = vs.NextObj(h)
            i += 1
    _result = objects
except Exception as e:
    _result = [{{'fatal': str(e)}}]
""")


@mcp.tool()
def vw_get_object_bounds(layer: str, name: str) -> dict:
    """Return the 2D bounding box of a named object.

    Args:
        layer: Design layer name.
        name: Object name (OIP Name field).
    """
    _ensure_document()
    return _run_in_vw(f"""
try:
    layer_name = {json.dumps(layer)}
    obj_name = {json.dumps(name)}
    found = None
    lyr = vs.FLayer()
    while lyr:
        if vs.GetLName(lyr) == layer_name:
            h = vs.FInLayer(lyr)
            while h:
                if vs.GetName(h) == obj_name:
                    found = h
                    break
                h = vs.NextObj(h)
            if found:
                break
        lyr = vs.NextLayer(lyr)
    if found:
        p1, p2 = vs.GetBBox(found)
        _result = {{'min_x': p1[0], 'min_y': p1[1], 'max_x': p2[0], 'max_y': p2[1]}}
    else:
        _result = {{'error': 'object not found'}}
except Exception as e:
    _result = {{'fatal': str(e)}}
""")


@mcp.tool()
def vw_get_record_data(layer: str, name: str, record: str) -> dict:
    """Return all fields from a named record attached to an object.

    Args:
        layer: Design layer name.
        name: Object name.
        record: Record format name (e.g. "Plant Record").
    """
    _ensure_document()
    return _run_in_vw(f"""
try:
    layer_name = {json.dumps(layer)}
    obj_name = {json.dumps(name)}
    record_name = {json.dumps(record)}
    found = None
    lyr = vs.FLayer()
    while lyr:
        if vs.GetLName(lyr) == layer_name:
            h = vs.FInLayer(lyr)
            while h:
                if vs.GetName(h) == obj_name:
                    found = h
                    break
                h = vs.NextObj(h)
            if found:
                break
        lyr = vs.NextLayer(lyr)
    fields = {{}}
    if found:
        for ri in range(1, vs.NumRecords(found) + 1):
            rec = vs.GetRecord(found, ri)
            if rec and vs.GetName(rec) == record_name:
                for fi in range(1, vs.NumFields(rec) + 1):
                    fname = vs.GetFldName(rec, fi)
                    fields[fname] = vs.GetRField(found, record_name, fname)
                break
    _result = fields
except Exception as e:
    _result = {{'fatal': str(e)}}
""")


@mcp.tool()
def vw_export_ifc() -> dict:
    """Trigger an IFC 4.3 export. Returns path of the exported file under ~/.lattice/vw-exports/."""
    _ensure_document()
    return _run_in_vw("""
try:
    import os, time
    target_dir = os.path.expanduser('~/.lattice/vw-exports')
    os.makedirs(target_dir, exist_ok=True)
    out_path = os.path.join(target_dir, f'{int(time.time())}.ifc')
    vs.SetPref(8908, True)
    vs.SetSavePref(8909, out_path)
    vs.DoMenuTextByName('Export IFC...', 0)
    _result = {'path': out_path}
except Exception as e:
    _result = {'fatal': str(e)}
""")


if __name__ == "__main__":
    mcp.run(transport="stdio")
