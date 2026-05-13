#!/usr/bin/env -S uv run --with fastmcp --with httpx python
"""3D Asset Generation MCP Server — port 8767.

Exposes the full plant asset pipeline as MCP tools:
  - generate_plant_prompt     → species → SD prompt + settings
  - render_plant_image        → SD prompt → ComfyUI job → image path
  - generate_3d_from_image    → image path → TRELLIS job → GLB path
  - run_full_pipeline         → species → GLB (orchestrates all three)
  - get_job_status            → check any pipeline job
  - list_completed_assets     → gallery of finished GLBs
  - ingest_asset              → write GLB to Pixeltable plant_assets

Register in .mcp.json:
  "3d-asset-gen": {
    "command": "uv",
    "args": ["run", "/path/to/3d_assets/mcp_server.py"]
  }

Run standalone:
  uv run 3d_assets/mcp_server.py
"""
from __future__ import annotations

import asyncio
import json
import os
import shutil
import sys
import time
import uuid
from pathlib import Path

HERE = Path(__file__).parent.resolve()
PROJECT_ROOT = HERE.parent
sys.path.insert(0, str(HERE / "scripts"))

from fastmcp import FastMCP

from generate_plant_prompt import build_prompt, build_all_prompts, SPECIES_TRAITS
from comfyui_client import (
    submit_job as _comfyui_submit,
    poll_job as _comfyui_poll,
    get_output_path,
    is_running as comfyui_is_running,
    COMFYUI_URL,
)

TRELLIS_SERVER = "http://127.0.0.1:8766"
TRELLIS_OUTPUTS = Path("/Volumes/PixelTable/MARPA_918_JUNIPER/experiments/trees_sage/trellis_outputs")
DOWNLOADS = Path.home() / "Downloads"

# In-memory pipeline job tracking
PIPELINE_JOBS: dict[str, dict] = {}

mcp = FastMCP("3d-asset-gen", port=8767)


# ---------------------------------------------------------------------------
# Tool: generate_plant_prompt
# ---------------------------------------------------------------------------

@mcp.tool()
def generate_plant_prompt(
    species_code: str,
    common_name: str,
    scientific_name: str,
    season: str = "summer",
) -> dict:
    """Generate an optimized Stable Diffusion prompt for a plant species.

    Returns sd_prompt, negative_prompt, recommended_model, width, height,
    steps, cfg, sampler, and notes. Use the output directly with render_plant_image.

    species_code: short code like JUNI_VIR, PLAT_ACE, QUER_ROB
    season: spring | summer | autumn | winter | evergreen
    """
    p = build_prompt(species_code, common_name, scientific_name, season=season)  # type: ignore[arg-type]
    return {
        "species_code":      p.species_code,
        "sd_prompt":         p.sd_prompt,
        "negative_prompt":   p.negative_prompt,
        "recommended_model": p.recommended_model,
        "width":             p.width,
        "height":            p.height,
        "steps":             p.steps,
        "cfg":               p.cfg,
        "sampler":           p.sampler,
        "notes":             p.notes,
    }


@mcp.tool()
def list_known_species() -> list[dict]:
    """List all species with pre-built botanical trait profiles."""
    known = [
        ("JUNI_VIR", "Eastern Red Cedar",   "Juniperus virginiana"),
        ("PLAT_ACE", "Sycamore",            "Platanus acerifolia"),
        ("QUER_ROB", "English Oak",         "Quercus robur"),
        ("ACER_RUB", "Red Maple",           "Acer rubrum"),
        ("TAXO_DIS", "Bald Cypress",        "Taxodium distichum"),
        ("MAGN_GRA", "Southern Magnolia",   "Magnolia grandiflora"),
        ("ILEX_OPA", "American Holly",      "Ilex opaca"),
        ("CORN_FLO", "Flowering Dogwood",   "Cornus florida"),
        ("PRUN_CER", "Cherry",              "Prunus cerasifera"),
        ("FAGU_SYL", "European Beech",      "Fagus sylvatica"),
    ]
    return [{"code": c, "common": n, "scientific": s} for c, n, s in known]


# ---------------------------------------------------------------------------
# Tool: render_plant_image
# ---------------------------------------------------------------------------

@mcp.tool()
def render_plant_image(
    sd_prompt: str,
    negative_prompt: str,
    model: str,
    species_code: str,
    width: int = 1024,
    height: int = 1024,
    steps: int = 35,
    cfg: float = 7.0,
    sampler: str = "dpmpp_2m",
    seed: int = 42,
) -> dict:
    """Submit a text-to-image render job to ComfyUI.

    Returns job_id and status. ComfyUI must be running at http://127.0.0.1:8188.
    Use get_job_status(job_id) to poll for completion.

    Start ComfyUI first if needed:
        cd /Volumes/Comfy/ComfyUI/ComfyUI && uv run python main.py
    """
    if not comfyui_is_running():
        return {
            "error": "ComfyUI is not running",
            "fix": "cd /Volumes/Comfy/ComfyUI/ComfyUI && uv run python main.py --port 8188",
        }

    jid = uuid.uuid4().hex[:10]
    try:
        prompt_id = _comfyui_submit(
            positive=sd_prompt,
            negative=negative_prompt,
            model=model,
            width=width,
            height=height,
            steps=steps,
            cfg=cfg,
            sampler=sampler,
            seed=seed,
            filename_prefix=f"trellis_{species_code}_{jid}",
        )
    except Exception as exc:
        return {"error": str(exc)}

    PIPELINE_JOBS[jid] = {
        "id":          jid,
        "type":        "comfyui_render",
        "species_code": species_code,
        "comfyui_prompt_id": prompt_id,
        "status":      "queued",
        "created":     time.time(),
    }
    return {"job_id": jid, "comfyui_prompt_id": prompt_id, "status": "queued"}


# ---------------------------------------------------------------------------
# Tool: generate_3d_from_image
# ---------------------------------------------------------------------------

@mcp.tool()
def generate_3d_from_image(image_path: str, seed: int = 42) -> dict:
    """Submit an image to the TRELLIS server for 3D generation.

    Returns trellis_job_id and status. Use get_job_status to poll.
    TRELLIS server must be running at http://127.0.0.1:8766.

    image_path: absolute path to JPG/PNG/WEBP image
    """
    import urllib.request
    import urllib.parse

    img = Path(image_path)
    if not img.exists():
        return {"error": f"Image not found: {image_path}"}

    suffix = img.suffix.lower()
    if suffix not in {".png", ".jpg", ".jpeg", ".webp"}:
        return {"error": f"Unsupported format {suffix}. Use png/jpg/webp."}

    # multipart POST to trellis_server
    boundary = uuid.uuid4().hex
    mime = {"png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
    content_type = mime.get(suffix, "image/png")

    img_data = img.read_bytes()
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="image"; filename="{img.name}"\r\n'
        f"Content-Type: {content_type}\r\n\r\n"
    ).encode() + img_data + f"\r\n--{boundary}\r\n".encode() + (
        f'Content-Disposition: form-data; name="seed"\r\n\r\n{seed}\r\n'
        f"--{boundary}--\r\n"
    ).encode()

    try:
        req = urllib.request.Request(
            f"{TRELLIS_SERVER}/api/generate",
            data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
    except Exception as exc:
        return {"error": f"TRELLIS server error: {exc}",
                "fix": "cd /Volumes/PixelTable/MARPA_918_JUNIPER/experiments/trees_sage && uv run trellis_server.py"}

    jid = result.get("id", "unknown")
    PIPELINE_JOBS[jid] = {**result, "type": "trellis_3d", "source_image": image_path}
    return {
        "job_id": jid,
        "status": result.get("status"),
        "log_url": f"{TRELLIS_SERVER}/api/jobs/{jid}/log",
        "glb_path": f"{TRELLIS_OUTPUTS}/{jid}/model.glb",
    }


# ---------------------------------------------------------------------------
# Tool: run_full_pipeline
# ---------------------------------------------------------------------------

@mcp.tool()
def run_full_pipeline(
    species_code: str,
    common_name: str,
    scientific_name: str,
    season: str = "summer",
    seed: int = 42,
) -> dict:
    """Orchestrate the full pipeline: generate prompt → render image → TRELLIS 3D.

    Returns a pipeline_job_id. The pipeline runs asynchronously — use
    get_job_status(pipeline_job_id) to track each stage.

    Requires both ComfyUI (port 8188) and TRELLIS server (port 8766) running.
    """
    # Stage 1: build prompt
    p = build_prompt(species_code, common_name, scientific_name, season=season)  # type: ignore[arg-type]

    pipeline_id = f"pipeline_{uuid.uuid4().hex[:8]}"
    PIPELINE_JOBS[pipeline_id] = {
        "id":           pipeline_id,
        "type":         "full_pipeline",
        "species_code": species_code,
        "stage":        "prompt_ready",
        "prompt":       p.__dict__,
        "created":      time.time(),
    }

    # Stage 2: submit ComfyUI render
    if not comfyui_is_running():
        PIPELINE_JOBS[pipeline_id]["stage"] = "waiting_comfyui"
        return {
            "pipeline_id": pipeline_id,
            "stage": "waiting_comfyui",
            "prompt": p.sd_prompt[:200],
            "fix": "Start ComfyUI: cd /Volumes/Comfy/ComfyUI/ComfyUI && uv run python main.py",
            "note": "Once ComfyUI is running, call render_plant_image() with the prompt above, then generate_3d_from_image() with the result.",
        }

    render_result = render_plant_image(
        sd_prompt=p.sd_prompt,
        negative_prompt=p.negative_prompt,
        model=p.recommended_model,
        species_code=species_code,
        width=p.width,
        height=p.height,
        steps=p.steps,
        cfg=p.cfg,
        sampler=p.sampler,
        seed=seed,
    )

    if "error" in render_result:
        PIPELINE_JOBS[pipeline_id]["stage"] = "comfyui_error"
        PIPELINE_JOBS[pipeline_id]["error"] = render_result["error"]
        return {"pipeline_id": pipeline_id, **render_result}

    PIPELINE_JOBS[pipeline_id].update({
        "stage":               "comfyui_rendering",
        "comfyui_job_id":      render_result["job_id"],
        "comfyui_prompt_id":   render_result["comfyui_prompt_id"],
    })

    return {
        "pipeline_id":       pipeline_id,
        "stage":             "comfyui_rendering",
        "comfyui_job_id":    render_result["job_id"],
        "species_prompt":    p.sd_prompt[:150] + "...",
        "model":             p.recommended_model,
        "next_step":         f"Call get_job_status('{pipeline_id}') to check progress",
    }


# ---------------------------------------------------------------------------
# Tool: get_job_status
# ---------------------------------------------------------------------------

@mcp.tool()
def get_job_status(job_id: str) -> dict:
    """Check the status of any pipeline job (ComfyUI render, TRELLIS 3D, or full pipeline)."""
    import urllib.request

    job = PIPELINE_JOBS.get(job_id)
    if not job:
        # Try to look it up in the TRELLIS server
        try:
            url = f"{TRELLIS_SERVER}/api/jobs/{job_id}"
            with urllib.request.urlopen(url, timeout=5) as resp:
                return json.loads(resp.read())
        except Exception:
            return {"error": f"Job {job_id} not found"}

    # For full pipelines, enrich with ComfyUI/TRELLIS status
    result = dict(job)
    if job.get("type") == "comfyui_render" and job.get("comfyui_prompt_id"):
        history = _comfyui_poll(job["comfyui_prompt_id"], timeout=5, interval=1)
        if history:
            img_path = get_output_path(history)
            result["comfyui_status"] = "done"
            result["image_path"] = str(img_path) if img_path else None
        else:
            result["comfyui_status"] = "still_rendering"

    return result


# ---------------------------------------------------------------------------
# Tool: list_completed_assets
# ---------------------------------------------------------------------------

@mcp.tool()
def list_completed_assets() -> list[dict]:
    """List all completed TRELLIS GLB assets on disk."""
    import urllib.request
    try:
        with urllib.request.urlopen(f"{TRELLIS_SERVER}/api/gallery", timeout=5) as resp:
            return json.loads(resp.read())
    except Exception:
        # Fallback: scan disk directly
        items = []
        if TRELLIS_OUTPUTS.exists():
            for d in sorted(TRELLIS_OUTPUTS.iterdir(), reverse=True):
                glb = d / "model.glb"
                if glb.exists():
                    items.append({
                        "id": d.name,
                        "glb": str(glb),
                        "size_mb": round(glb.stat().st_size / 1e6, 1),
                        "mtime": glb.stat().st_mtime,
                    })
        return items


# ---------------------------------------------------------------------------
# Tool: copy_to_downloads
# ---------------------------------------------------------------------------

@mcp.tool()
def copy_asset_to_downloads(job_id: str, filename: str | None = None) -> dict:
    """Copy a completed TRELLIS GLB to ~/Downloads."""
    glb = TRELLIS_OUTPUTS / job_id / "model.glb"
    if not glb.exists():
        return {"error": f"GLB not found for job {job_id}"}
    dest = DOWNLOADS / (filename or f"trellis_{job_id}.glb")
    shutil.copy2(glb, dest)
    return {"copied_to": str(dest), "size_mb": round(dest.stat().st_size / 1e6, 1)}


# ---------------------------------------------------------------------------
# Tool: ingest_asset
# ---------------------------------------------------------------------------

@mcp.tool()
def ingest_asset(
    job_id: str,
    species_code: str,
    common_name: str,
    scientific_name: str,
    vw_style_name: str,
    mature_height_m: float = 0.0,
    crown_radius_m: float = 0.0,
) -> dict:
    """Copy completed GLB to lod-300 folder and upsert into Pixeltable plant_assets."""
    glb_src = TRELLIS_OUTPUTS / job_id / "model.glb"
    if not glb_src.exists():
        return {"error": f"No GLB found for job {job_id}"}

    lod_dir = PROJECT_ROOT / "assets" / "plants" / "lod-300"
    lod_dir.mkdir(parents=True, exist_ok=True)
    dest = lod_dir / f"{species_code}.glb"
    shutil.copy2(glb_src, dest)

    # Relative path for Pixeltable
    try:
        rel = str(dest.relative_to(PROJECT_ROOT))
    except ValueError:
        rel = str(dest)

    try:
        import pixeltable as pxt
        t = pxt.get_table("lattice/bridge/plant_assets")
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        existing = t.select(t.asset_id).where(t.species_code == species_code).collect()
        if len(existing) > 0:
            t.update(
                {"lod_300_glb": rel, "asset_source": "trellis", "updated_at": now},
                where=t.species_code == species_code,
            )
            action = "updated"
        else:
            t.insert([{
                "asset_id":        uuid.uuid4().hex,
                "species_code":    species_code,
                "common_name":     common_name,
                "scientific_name": scientific_name,
                "lod_300_glb":     rel,
                "asset_source":    "trellis",
                "vw_style_name":   vw_style_name,
                "mature_height_m": mature_height_m,
                "crown_radius_m":  crown_radius_m,
                "is_custom":       True,
                "created_at":      now,
                "updated_at":      now,
                "raw_event":       {"source_job": job_id},
            }])
            action = "inserted"
        pxt_status = f"pixeltable {action}"
    except Exception as exc:
        pxt_status = f"pixeltable skipped: {exc}"

    return {
        "species_code": species_code,
        "glb_path":     str(dest),
        "pixeltable":   pxt_status,
        "vw_style_name": vw_style_name,
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
