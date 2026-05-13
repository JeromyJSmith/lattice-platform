#!/usr/bin/env python3
"""Ingest a TRELLIS-generated GLB into Pixeltable lattice/bridge/plant_assets.

Usage:
    PIXELTABLE_HOME=/Volumes/PixelTable/.pixeltable \
    PYTHONPATH=/Volumes/PixelTable/schemas \
    python ingest_trellis_glb.py \
      --glb assets/plants/lod-300/JUNI_VIR.glb \
      --species-code JUNI_VIR \
      --common-name "Eastern Red Cedar" \
      --scientific-name "Juniperus virginiana" \
      --vw-style-name "Juniperus 12'" \
      --mature-height 3.7 \
      --crown-radius 1.2
"""
from __future__ import annotations

import argparse
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent.parent.parent.resolve()  # VW_iTwin_Bridge root


def run(args: argparse.Namespace) -> None:
    try:
        import pixeltable as pxt
    except ImportError:
        sys.exit("pixeltable not found — run with: uv run python ingest_trellis_glb.py ...")

    glb_path = Path(args.glb).resolve()
    if not glb_path.exists():
        sys.exit(f"GLB not found: {glb_path}")

    # Relative path from project root for portability
    try:
        rel_path = str(glb_path.relative_to(HERE))
    except ValueError:
        rel_path = str(glb_path)

    table_path = "lattice/bridge/plant_assets"
    t = pxt.get_table(table_path)

    # Check for existing row by species_code and upsert
    existing = (
        t.select(t.asset_id)
        .where(t.species_code == args.species_code)
        .collect()
    )

    now = datetime.now(timezone.utc)

    if len(existing) > 0:
        asset_id = existing["asset_id"][0]
        t.update(
            {"lod_300_glb": rel_path, "asset_source": "trellis", "updated_at": now},
            where=t.species_code == args.species_code,
        )
        print(f"Updated existing row  asset_id={asset_id}")
    else:
        asset_id = uuid.uuid4().hex
        row = {
            "asset_id":         asset_id,
            "species_code":     args.species_code,
            "common_name":      args.common_name,
            "scientific_name":  args.scientific_name,
            "family":           args.family or "",
            "lod_300_glb":      rel_path,
            "asset_source":     "trellis",
            "vw_style_name":    args.vw_style_name,
            "mature_height_m":  args.mature_height,
            "crown_radius_m":   args.crown_radius,
            "canopy_density":   args.canopy_density,
            "is_custom":        True,
            "created_at":       now,
            "updated_at":       now,
            "raw_event":        {
                "ingest_script": "ingest_trellis_glb.py",
                "source_glb":    str(glb_path),
            },
        }
        t.insert([row])
        print(f"Inserted new row  asset_id={asset_id}")

    print(f"  species_code  : {args.species_code}")
    print(f"  common_name   : {args.common_name}")
    print(f"  lod_300_glb   : {rel_path}")
    print(f"  vw_style_name : {args.vw_style_name}")
    print(f"  table         : {table_path}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--glb",             required=True)
    p.add_argument("--species-code",    required=True)
    p.add_argument("--common-name",     required=True)
    p.add_argument("--scientific-name", required=True)
    p.add_argument("--vw-style-name",   required=True,
                   help="Exact name in VW Plant Style Manager")
    p.add_argument("--mature-height",   type=float, default=0.0, metavar="M")
    p.add_argument("--crown-radius",    type=float, default=0.0, metavar="M")
    p.add_argument("--canopy-density",  type=float, default=0.7, metavar="0-1")
    p.add_argument("--family",          default="")
    run(p.parse_args())


if __name__ == "__main__":
    main()
