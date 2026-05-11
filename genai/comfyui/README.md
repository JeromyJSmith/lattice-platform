# ComfyUI in LATTICE

ComfyUI is LATTICE's local image / 3D generation runtime. We use it to turn geo-tagged reference photos (taken on site, dropped on the `/globe` Cesium map) into 3D plant assets ready for Cinema 4D + Vectorworks Plant Style Manager.

## Setup (Apple Silicon)

```bash
git clone https://github.com/comfyanonymous/ComfyUI ~/ComfyUI
cd ~/ComfyUI
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py --listen --port 8188  # MPS backend auto-detected on Apple Silicon
```

LATTICE talks to ComfyUI at `http://localhost:8188` via [`comfyui-client.py`](comfyui-client.py) (Python API client) and dispatches jobs through [`job-dispatcher.py`](job-dispatcher.py).

## Workflows (JSON in `workflows/`)

| File | Pipeline |
|---|---|
| `plant-2d-to-3d.json` | 3–6 reference photos → textured 3D mesh → GLB |
| `tree-crown-gen.json` | Species parameters → procedural crown texture |
| `texture-from-photo.json` | Site photo → tiling PBR texture set |

The JSON workflows are ComfyUI-native — pull them with `comfyui-client.py --pull-default-workflows` (stub for now).

## Job lifecycle

```
Operator drops pin + photo on /globe
       │
       ▼
POST /v1/ingest/reference-image  (sidecar)
       │
       ▼
INSERT lattice/bridge/reference_images  (Pixeltable)
       │
       │  trigger: enough_images_for_species(species_code) >= 3
       ▼
INSERT lattice/genai/comfyui_jobs  status='pending'
       │
       ▼
job-dispatcher.py picks pending row, POSTs to ComfyUI
       │
       ▼
Polls ComfyUI status → writes output_glb_path back to row → status='complete'
       │
       │  trigger on status='complete'
       ▼
UPDATE lattice/bridge/plant_assets.lod_300_glb
       │
       ▼
Push to VW Plant Style Manager via vwx-mcp (replaces LOD100 spike)
```

Tracked in [`meta/FEATURE_BACKLOG.md`](../../meta/FEATURE_BACKLOG.md) § 3D PLANT ASSET CREATION PIPELINE.
