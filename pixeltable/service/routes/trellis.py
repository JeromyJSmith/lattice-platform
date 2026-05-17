"""TRELLIS image-to-3D routes — local MLX inference via ~/trellis-mac.

Pipeline: upload image → asyncio subprocess → ~/trellis-mac/generate.py → GLB on disk.

Endpoints:
  POST   /v1/trellis/jobs               — upload image, queue generation
  GET    /v1/trellis/jobs               — list recent jobs
  GET    /v1/trellis/jobs/{job_id}      — get job status
  DELETE /v1/trellis/jobs/{job_id}      — cancel / remove job
"""

from __future__ import annotations

import asyncio
import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from service.deps import get_pxt, require_local_socket_or_token

router = APIRouter(dependencies=[Depends(require_local_socket_or_token)])
log = logging.getLogger("vwbridge.trellis")

_REPO_ROOT = Path(__file__).resolve().parents[3]
_UPLOAD_DIR = _REPO_ROOT / "runtime-runs" / "trellis-uploads"
_OUTPUT_DIR = _REPO_ROOT / "runtime-runs" / "trellis-outputs"

TRELLIS_DIR = Path.home() / "trellis-mac"
TRELLIS_PY = TRELLIS_DIR / ".venv" / "bin" / "python"
TRELLIS_SCRIPT = TRELLIS_DIR / "generate.py"
HF_HUB_CACHE = Path("/Volumes/PixelTable/models/huggingface-cache")

T_JOBS = "lattice/genai/trellis_jobs"

# In-process job state for running subprocesses (pid tracking)
_RUNNING: dict[str, asyncio.subprocess.Process] = {}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _to_dict(row) -> dict[str, Any]:
    if hasattr(row, "items"):
        return {k: v for k, v in row.items() if v is not None}
    return dict(row)


def _glb_url(job_id: str) -> str:
    return f"/trellis-outputs/{job_id}/model.glb"


async def _run_trellis(job_id: str, image_path: Path, seed: int, pipeline_type: str, texture_size: int, pxt) -> None:
    out_dir = _OUTPUT_DIR / job_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_stem = str(out_dir / "model")
    log_path = out_dir / "run.log"

    cmd = [
        str(TRELLIS_PY),
        str(TRELLIS_SCRIPT),
        str(image_path),
        "--output", out_stem,
        "--seed", str(seed),
        "--pipeline-type", pipeline_type,
        "--texture-size", str(texture_size),
    ]

    env = os.environ.copy()
    env["HF_HUB_CACHE"] = str(HF_HUB_CACHE)
    env["HF_HUB_OFFLINE"] = "1"

    try:
        t = pxt.get_table(T_JOBS)
        t.update({"status": "processing", "updated_at": _now()}, where=t.job_id == job_id)
    except Exception as exc:
        log.warning("Pixeltable status update failed: %s", exc)

    with open(log_path, "w") as logf:
        logf.write(f"cmd: {' '.join(cmd)}\n\n")
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(TRELLIS_DIR),
            stdout=logf,
            stderr=asyncio.subprocess.STDOUT,
            env=env,
        )
        _RUNNING[job_id] = proc
        rc = await proc.wait()
    _RUNNING.pop(job_id, None)

    glb = out_dir / "model.glb"
    now = _now()
    if rc == 0 and glb.exists():
        updates: dict[str, Any] = {
            "status": "succeeded",
            "output_glb_url": _glb_url(job_id),
            "completed_at": now,
            "updated_at": now,
        }
    else:
        log_tail = ""
        if log_path.exists():
            data = log_path.read_text(errors="replace")
            log_tail = data[-500:] if len(data) > 500 else data
        updates = {
            "status": "failed",
            "error_message": f"generate.py exited rc={rc}. Log tail: {log_tail}",
            "completed_at": now,
            "updated_at": now,
        }

    try:
        t = pxt.get_table(T_JOBS)
        t.update(updates, where=t.job_id == job_id)
    except Exception as exc:
        log.warning("Pixeltable final update failed: %s", exc)

    log.info("TRELLIS job %s finished rc=%s glb_exists=%s", job_id, rc, glb.exists())


# ---------------------------------------------------------------------------
# POST /v1/trellis/jobs
# ---------------------------------------------------------------------------

@router.post("/jobs")
async def create_job(
    file: UploadFile = File(..., description="Source image (JPEG, PNG, WebP)"),
    project_id: str = Form(""),
    seed: int = Form(42),
    pipeline_type: str = Form("512"),
    texture_size: int = Form(1024),
    pxt=Depends(get_pxt),
):
    """Upload an image and start a local TRELLIS image-to-3D generation.

    Returns immediately with a job_id. Poll GET /v1/trellis/jobs/{job_id} for status.
    """
    if not TRELLIS_PY.exists():
        raise HTTPException(503, f"trellis-mac venv not found at {TRELLIS_PY}. Is ~/trellis-mac installed?")
    if not TRELLIS_SCRIPT.exists():
        raise HTTPException(503, f"trellis-mac generate.py not found at {TRELLIS_SCRIPT}")
    if pipeline_type not in ("512", "1024", "1024_cascade"):
        raise HTTPException(400, f"pipeline_type must be 512, 1024, or 1024_cascade")
    if texture_size not in (512, 1024, 2048):
        raise HTTPException(400, "texture_size must be 512, 1024, or 2048")

    image_bytes = await file.read()
    if len(image_bytes) > 20 * 1024 * 1024:
        raise HTTPException(413, "Image exceeds 20 MB limit")
    content_type = file.content_type or "image/jpeg"
    if not content_type.startswith("image/"):
        raise HTTPException(400, f"Expected an image file, got {content_type!r}")

    job_id = uuid.uuid4().hex[:16]
    upload_dir = _UPLOAD_DIR / job_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename or "input.jpg").suffix or ".jpg"
    input_path = upload_dir / f"input{suffix}"
    input_path.write_bytes(image_bytes)

    now = _now()
    row = {
        "id":                      uuid.uuid4().hex,
        "job_id":                  job_id,
        "project_id":              project_id,
        "input_image_path":        str(input_path),
        "input_filename":          file.filename or "input.jpg",
        "replicate_model":         "local/trellis-mac",
        "replicate_version":       "",
        "replicate_prediction_id": "",
        "replicate_poll_url":      "",
        "seed":                    seed,
        "ss_guidance_strength":    7.5,
        "ss_sampling_steps":       12,
        "slat_guidance_strength":  3.0,
        "slat_sampling_steps":     12,
        "mesh_simplify_ratio":     0.95,
        "texture_size":            texture_size,
        "status":                  "starting",
        "error_message":           "",
        "output_glb_url":          "",
        "output_ply_url":          "",
        "output_trimesh_url":      "",
        "output_video_url":        "",
        "created_at":              now,
        "updated_at":              now,
        "raw_response":            {"pipeline_type": pipeline_type, "backend": "local"},
    }
    try:
        t = pxt.get_table(T_JOBS)
        t.insert([row])
    except Exception as exc:
        log.warning("Pixeltable insert failed (non-fatal): %s", exc)

    asyncio.create_task(_run_trellis(job_id, input_path, seed, pipeline_type, texture_size, pxt))

    log.info("TRELLIS job queued job_id=%s pipeline=%s texture=%s", job_id, pipeline_type, texture_size)
    return {"job_id": job_id, "status": "starting"}


# ---------------------------------------------------------------------------
# GET /v1/trellis/jobs
# ---------------------------------------------------------------------------

@router.get("/jobs")
def list_jobs(limit: int = 20, pxt=Depends(get_pxt)):
    """List recent TRELLIS jobs, newest first."""
    try:
        t = pxt.get_table(T_JOBS)
        rows = t.select(
            t.job_id, t.status, t.input_filename, t.created_at,
            t.output_glb_url, t.output_ply_url, t.output_video_url,
            t.error_message,
        ).order_by(t.created_at, asc=False).limit(limit).collect()
        return {"jobs": [_to_dict(r) for r in rows]}
    except Exception as exc:
        log.warning("list_jobs failed: %s", exc)
        return {"jobs": []}


# ---------------------------------------------------------------------------
# GET /v1/trellis/jobs/{job_id}
# ---------------------------------------------------------------------------

@router.get("/jobs/{job_id}")
async def get_job(job_id: str, pxt=Depends(get_pxt)):
    """Get job status. If processing, checks disk for the output GLB."""
    try:
        t = pxt.get_table(T_JOBS)
        rows = list(t.where(t.job_id == job_id).collect())
    except Exception as exc:
        raise HTTPException(500, f"Pixeltable error: {exc}") from exc

    if not rows:
        raise HTTPException(404, f"job_id={job_id!r} not found")

    row = _to_dict(rows[0])

    # If still marked processing but the GLB is already on disk, update now
    if row.get("status") == "processing":
        glb = _OUTPUT_DIR / job_id / "model.glb"
        if glb.exists():
            now = _now()
            try:
                t.update(
                    {"status": "succeeded", "output_glb_url": _glb_url(job_id),
                     "completed_at": now, "updated_at": now},
                    where=t.job_id == job_id,
                )
                row["status"] = "succeeded"
                row["output_glb_url"] = _glb_url(job_id)
            except Exception as exc:
                log.warning("Pixeltable lazy-update failed: %s", exc)

    return row


# ---------------------------------------------------------------------------
# GET /v1/trellis/jobs/{job_id}/log
# ---------------------------------------------------------------------------

@router.get("/jobs/{job_id}/log")
async def get_log(job_id: str):
    """Return the tail of the generation log for a running or finished job."""
    log_path = _OUTPUT_DIR / job_id / "run.log"
    if not log_path.exists():
        return {"log": "(no log yet)"}
    data = log_path.read_text(errors="replace")
    return {"log": data[-8192:] if len(data) > 8192 else data}


# ---------------------------------------------------------------------------
# DELETE /v1/trellis/jobs/{job_id}
# ---------------------------------------------------------------------------

@router.delete("/jobs/{job_id}")
async def cancel_job(job_id: str, pxt=Depends(get_pxt)):
    """Kill the running subprocess (if any) and mark the job cancelled."""
    proc = _RUNNING.pop(job_id, None)
    if proc and proc.returncode is None:
        try:
            proc.terminate()
        except ProcessLookupError:
            pass

    try:
        t = pxt.get_table(T_JOBS)
        rows = list(t.where(t.job_id == job_id).collect())
        if not rows:
            raise HTTPException(404, f"job_id={job_id!r} not found")
        t.update({"status": "cancelled", "updated_at": _now()}, where=t.job_id == job_id)
    except HTTPException:
        raise
    except Exception as exc:
        log.warning("Pixeltable cancel update failed: %s", exc)

    return {"job_id": job_id, "status": "cancelled"}
