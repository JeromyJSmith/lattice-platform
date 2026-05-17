"""0017 — TRELLIS image-to-3D job tracking.

Adds lattice/genai/trellis_jobs to track image-to-GLB and Gaussian-splat
generation jobs submitted to the Replicate TRELLIS model (firtoz/trellis).

What this migration creates:
  lattice/genai/trellis_jobs  — per-job record for TRELLIS generations (new)
"""

from __future__ import annotations

import argparse
import sys

from migrations._helpers import (
    OWNED_PARENTS,
    assert_ownership,
    banner,
    ensure_table,
)

MIGRATION_ID = "0017_trellis_jobs"


def _trellis_jobs_schema(pxt) -> dict[str, object]:
    return {
        # --- identity ---
        "id":                     pxt.String,   # UUID hex — primary key
        "job_id":                 pxt.String,   # user-facing job identifier
        "project_id":             pxt.String,   # optional FK -> bridge project

        # --- input ---
        "input_image_path":       pxt.String,   # local path to saved upload
        "input_filename":         pxt.String,   # original filename from upload

        # --- replicate ---
        "replicate_model":        pxt.String,   # e.g. "firtoz/trellis"
        "replicate_version":      pxt.String,   # model version hash (if pinned)
        "replicate_prediction_id": pxt.String,  # prediction ID from Replicate API
        "replicate_poll_url":     pxt.String,   # GET URL to check prediction status

        # --- generation params ---
        "seed":                   pxt.Int,
        "ss_guidance_strength":   pxt.Float,
        "ss_sampling_steps":      pxt.Int,
        "slat_guidance_strength": pxt.Float,
        "slat_sampling_steps":    pxt.Int,
        "mesh_simplify_ratio":    pxt.Float,
        "texture_size":           pxt.Int,

        # --- status ---
        "status":                 pxt.String,   # pending/starting/processing/succeeded/failed/cancelled
        "error_message":          pxt.String,

        # --- output URLs (Replicate CDN, publicly accessible) ---
        "output_glb_url":         pxt.String,   # GLB mesh output
        "output_ply_url":         pxt.String,   # Gaussian splat .ply
        "output_trimesh_url":     pxt.String,   # trimesh .ply
        "output_video_url":       pxt.String,   # turntable preview video

        # --- timing ---
        "created_at":             pxt.Timestamp,
        "updated_at":             pxt.Timestamp,
        "completed_at":           pxt.Timestamp,
        "duration_seconds":       pxt.Float,

        # --- raw response ---
        "raw_response":           pxt.Json,
    }


def run(pxt, dry_run: bool = False) -> None:
    banner("0017: creating lattice/genai/trellis_jobs", dry_run=dry_run)
    assert_ownership(pxt, OWNED_PARENTS)

    # lattice/genai already exists (created in 0012); just ensure the table.
    ensure_table(pxt, "lattice/genai/trellis_jobs", _trellis_jobs_schema(pxt), dry_run)

    if not dry_run:
        print("✓ lattice/genai/trellis_jobs ready")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    try:
        import pixeltable as pxt
    except ImportError:
        sys.exit("pixeltable not found — run with: uv run python 0017_trellis_jobs.py")

    run(pxt, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
