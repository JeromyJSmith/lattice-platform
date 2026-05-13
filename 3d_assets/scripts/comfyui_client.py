"""Thin ComfyUI API client — submit text-to-image jobs and poll for output.

ComfyUI must be running at COMFYUI_URL (default http://127.0.0.1:8188).

Start ComfyUI:
    cd /Volumes/Comfy/ComfyUI/ComfyUI
    uv run python main.py --port 8188

Outputs land in:
    /Volumes/Comfy/ComfyUI/ComfyUI/output/
"""
from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any

COMFYUI_URL = "http://127.0.0.1:8188"
OUTPUT_DIR = Path("/Volumes/Comfy/ComfyUI/ComfyUI/output")


def _build_workflow(
    positive: str,
    negative: str,
    model: str,
    width: int,
    height: int,
    steps: int,
    cfg: float,
    sampler: str,
    seed: int,
    filename_prefix: str,
) -> dict[str, Any]:
    return {
        "4":  {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": model},
        },
        "5":  {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": width, "height": height, "batch_size": 1},
        },
        "6":  {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": positive, "clip": ["4", 1]},
        },
        "7":  {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": negative, "clip": ["4", 1]},
        },
        "3":  {
            "class_type": "KSampler",
            "inputs": {
                "model":        ["4", 0],
                "positive":     ["6", 0],
                "negative":     ["7", 0],
                "latent_image": ["5", 0],
                "seed":         seed,
                "steps":        steps,
                "cfg":          cfg,
                "sampler_name": sampler,
                "scheduler":    "karras",
                "denoise":      1.0,
            },
        },
        "8":  {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
        },
        "9":  {
            "class_type": "SaveImage",
            "inputs": {"images": ["8", 0], "filename_prefix": filename_prefix},
        },
    }


def submit_job(
    positive: str,
    negative: str,
    model: str,
    width: int = 1024,
    height: int = 1024,
    steps: int = 35,
    cfg: float = 7.0,
    sampler: str = "dpmpp_2m",
    seed: int | None = None,
    filename_prefix: str = "trellis_source",
) -> str:
    """Submit a text-to-image job. Returns prompt_id (str)."""
    import urllib.request

    if seed is None:
        import random
        seed = random.randint(0, 2**31)

    workflow = _build_workflow(
        positive, negative, model, width, height, steps, cfg, sampler, seed,
        filename_prefix,
    )
    client_id = uuid.uuid4().hex
    payload = json.dumps({"prompt": workflow, "client_id": client_id}).encode()
    req = urllib.request.Request(
        f"{COMFYUI_URL}/prompt",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read())
    return result["prompt_id"]


def poll_job(prompt_id: str, timeout: int = 600, interval: int = 5) -> dict[str, Any] | None:
    """Poll until job completes. Returns history entry or None on timeout."""
    import urllib.request

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            url = f"{COMFYUI_URL}/history/{prompt_id}"
            with urllib.request.urlopen(url, timeout=10) as resp:
                history = json.loads(resp.read())
            if prompt_id in history:
                return history[prompt_id]
        except Exception:
            pass
        time.sleep(interval)
    return None


def get_output_path(history_entry: dict) -> Path | None:
    """Extract the saved image path from a completed history entry."""
    try:
        outputs = history_entry.get("outputs", {})
        for node_output in outputs.values():
            for img in node_output.get("images", []):
                subfolder = img.get("subfolder", "")
                filename  = img["filename"]
                if subfolder:
                    return OUTPUT_DIR / subfolder / filename
                return OUTPUT_DIR / filename
    except (KeyError, TypeError):
        return None


def is_running() -> bool:
    """Return True if ComfyUI is responding on COMFYUI_URL."""
    import urllib.request
    try:
        with urllib.request.urlopen(f"{COMFYUI_URL}/system_stats", timeout=3):
            return True
    except Exception:
        return False
