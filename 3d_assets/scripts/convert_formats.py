#!/usr/bin/env python3
"""Convert a TRELLIS-generated GLB to FBX, USDC, USDZ, and place the LOD-300 GLB.

Usage:
    python convert_formats.py --glb /path/to/model.glb --species-code JUNI_VIR [--out-dir exports/]

Requires Blender on PATH (/opt/homebrew/bin/blender on this machine).
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent.parent.resolve()
BLENDER = shutil.which("blender") or "/opt/homebrew/bin/blender"

BLENDER_SCRIPT = """
import bpy, sys, os

input_glb = sys.argv[sys.argv.index("--") + 1]
out_fbx   = sys.argv[sys.argv.index("--") + 2]
out_usdc  = sys.argv[sys.argv.index("--") + 3]
out_usdz  = sys.argv[sys.argv.index("--") + 4]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=input_glb)

# FBX
bpy.ops.export_scene.fbx(
    filepath=out_fbx,
    use_selection=False,
    embed_textures=True,
    path_mode="COPY",
    bake_space_transform=True,
    axis_forward="-Z",
    axis_up="Y",
)

# USD / USDZ (Blender 3.3+)
try:
    bpy.ops.wm.usd_export(filepath=out_usdc, export_textures=True, generate_preview_surface=True)
    # usdz is just a zip of usdc + textures; Blender writes .usdz directly if extension is .usdz
    bpy.ops.wm.usd_export(filepath=out_usdz, export_textures=True, generate_preview_surface=True)
except Exception as e:
    print(f"USD export warning: {e}", file=sys.stderr)

print("DONE")
"""


def run(args: argparse.Namespace) -> None:
    glb = Path(args.glb).resolve()
    if not glb.exists():
        sys.exit(f"GLB not found: {glb}")

    out_dir = Path(args.out_dir).resolve()
    fbx_dir  = out_dir / "fbx"
    usd_dir  = out_dir / "usd"
    usdz_dir = out_dir / "usdz"
    lod_dir  = HERE / "assets" / "plants" / "lod-300"

    for d in (fbx_dir, usd_dir, usdz_dir, lod_dir):
        d.mkdir(parents=True, exist_ok=True)

    code = args.species_code
    out_fbx  = fbx_dir  / f"{code}.fbx"
    out_usdc = usd_dir  / f"{code}.usdc"
    out_usdz = usdz_dir / f"{code}.usdz"
    out_lod  = lod_dir  / f"{code}.glb"

    # Place GLB into lod-300
    shutil.copy2(glb, out_lod)
    print(f"GLB  → {out_lod}")

    # Write the Blender script to a temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(BLENDER_SCRIPT)
        script_path = f.name

    cmd = [
        BLENDER,
        "--background",
        "--python", script_path,
        "--",
        str(glb),
        str(out_fbx),
        str(out_usdc),
        str(out_usdz),
    ]
    print(f"Running Blender headless...")
    result = subprocess.run(cmd, capture_output=False, text=True)

    Path(script_path).unlink(missing_ok=True)

    if result.returncode != 0:
        sys.exit(f"Blender exited with code {result.returncode}")

    manifest = {
        "species_code": code,
        "source_glb":   str(glb),
        "lod_300_glb":  str(out_lod),
        "fbx":          str(out_fbx) if out_fbx.exists() else None,
        "usdc":         str(out_usdc) if out_usdc.exists() else None,
        "usdz":         str(out_usdz) if out_usdz.exists() else None,
    }
    manifest_path = out_dir / f"{code}_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"Manifest → {manifest_path}")
    for k, v in manifest.items():
        if v and k != "source_glb":
            print(f"  {k:12s}: {v}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--glb", required=True, help="Path to source model.glb from TRELLIS")
    p.add_argument("--species-code", required=True, help="Short code e.g. JUNI_VIR")
    p.add_argument("--out-dir", default=str(HERE / "3d_assets" / "exports"),
                   help="Root output directory (default: 3d_assets/exports/)")
    run(p.parse_args())


if __name__ == "__main__":
    main()
