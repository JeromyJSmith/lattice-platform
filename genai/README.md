# Local AI / GenAI / GeoAI in LATTICE

All AI compute that LATTICE controls runs **locally on Apple Silicon**. There's no cloud GenAI spend in the LATTICE budget — the only externally-billed AI usage is the `claude -p` CLI, and that's covered by the operator's Claude Max subscription (see [`pixeltable/service/worker.py`](../pixeltable/service/worker.py)).

| Subdir | What it owns |
|---|---|
| [`llm/`](llm/) | Ollama + LM Studio routing: local 70B-class models, code models, embeddings. The `model-router.py` picks per task. |
| [`comfyui/`](comfyui/) | ComfyUI server + workflow JSON. The 2D→3D plant pipeline lives here. |
| [`geoai/`](geoai/) | Tree detection, species classification, shadow segmentation — fine-tunable on MARPA project imagery. |
| [`3d-asset-pipeline/`](3d-asset-pipeline/) | End-to-end pipeline: geo-tagged reference image → ComfyUI → C4D → VW Plant Style. |

## How LATTICE uses local AI

1. **Pixeltable computed columns** — `lattice/bridge/reference_images.embedding` is filled by a local embedding model (nomic-embed-text), no API key.
2. **Agent runs** — the worker prefers `claude -p` for complex AEC reasoning but the `model-router.py` falls back to Ollama for cheap classification / extraction.
3. **3D asset creation** — the operator drops geo-tagged photos on the `/globe` Cesium map; a Pixeltable trigger dispatches a ComfyUI job; the resulting GLB is pushed to the VW Plant Style Manager via `vwx-mcp`.
4. **GeoAI** — point clouds + orthophotos go through trained models in `geoai/` to produce existing-tree rows in `lattice/bridge/existing_trees`.

## Locked invariants

- **No cloud GenAI APIs** in the default agent path. Cloud calls are an explicit user-driven choice (e.g., a `--use-anthropic-api` flag we don't ship yet).
- **All model state is auditable** — `lattice/genai/model_registry` lists every model with status, size, capabilities.
- **All training runs are auditable** — `lattice/genai/training_runs` captures task, dataset, val accuracy, checkpoint path.
- **All ComfyUI jobs are auditable** — `lattice/genai/comfyui_jobs` captures every workflow invocation + output asset.

See [`AGENTS.md`](../AGENTS.md), [`meta/FEATURE_BACKLOG.md`](../meta/FEATURE_BACKLOG.md), and the Pixeltable tables created in migration `0012_extended_schema.py`.
