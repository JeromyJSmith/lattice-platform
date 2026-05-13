---
description: Manage ComfyUI workflows, plant asset registration, LOD 100/300 pipeline, training run tracking, and quality-gated promotion to the lattice/genai model registry.
---

# LATTICE GenAI Asset Pipeline

The genai section owns the plant-2d-to-3d pipeline: ComfyUI workflow dispatch,
training run tracking in `lattice/genai/training_runs`, asset registration in
`lattice/genai/model_registry`, job status in `lattice/genai/comfyui_jobs`, and
quality-gated promotion from dev to prod. The scoring script `scripts/score-genai.sh`
checks asset sync, model quality averages, training health, orphan counts, and
LOD distribution.

## When this skill applies

- Registering a new `.glb` asset into `lattice/genai/model_registry`
- Dispatching a new ComfyUI training job
- Evaluating asset quality and promoting/holding an asset
- Fixing orphan assets (file exists but no registry row, or row points to missing file)
- Running the genai section cycle: `bash meta/harness/bootstrap/run-autoresearch.sh genai`
- `quality_score` is null or below 0.7 for a promoted asset

## How it works

1. Audit asset inventory:
   ```bash
   find assets/plants -name "*.glb" | sort | wc -l
   ```
   Must match:
   ```python
   t = pxt.get_table("lattice/genai/model_registry")
   print(len(t.collect()))
   ```

2. Check for orphan assets (file missing but row exists):
   ```python
   import os
   registry = pxt.get_table("lattice/genai/model_registry")
   for row in registry.select(registry.asset_path).collect():
       if not os.path.exists(row["asset_path"]):
           print(f"ORPHAN: {row['asset_path']}")
   ```

3. Register a new asset:
   ```python
   pxt.get_table("lattice/genai/model_registry").insert([{
       "asset_id": "<uuid>",
       "asset_path": "assets/plants/lod-300/<species>/<file>.glb",
       "species": "Acer_palmatum",
       "lod_level": 300,
       "quality_score": None,  # set after evaluation
       "status": "dev",
       "source_run_id": "<training-run-id>",
   }])
   ```

4. Dispatch a ComfyUI training job:
   - Generate workflow JSON targeting the ComfyUI server.
   - Insert a row into `lattice/genai/comfyui_jobs` with `status='pending'`.
   - Stream output; update row to `status='running'` on start,
     `status='completed'` with `output_path` on success, `status='failed'` on error.

5. Evaluate quality and promote:
   - Compute `quality_score` (geometry fidelity, texture completeness, botanical features).
   - If `quality_score >= 0.7`: update `status='prod'` in registry.
   - If `quality_score < 0.7`: keep `status='dev'`, log reason to training run record.

6. Verify LOD distribution:
   ```python
   registry = pxt.get_table("lattice/genai/model_registry")
   # LOD 100 count must exceed LOD 300 count (placeholders outnumber detail assets)
   ```

7. Check for failed ComfyUI jobs in last 24 hours:
   ```python
   jobs = pxt.get_table("lattice/genai/comfyui_jobs")
   # filter status='failed', sort by created_at desc, review error_log
   ```

## Files used

- `assets/plants/lod-100/` — LOD 100 placeholder geometries
- `assets/plants/lod-300/` — LOD 300 botanical detail assets
- `genai/GOAL.md` — genai section fitness function
- `pixeltable/service/routes/genai.py` — FastAPI routes for genai endpoints
- `lattice/genai/model_registry` — asset registry (quality_score, lod_level, status)
- `lattice/genai/comfyui_jobs` — ComfyUI job tracking (status, output_path, error_log)
- `lattice/genai/training_runs` — training run records (input_dataset, checkpoint, metrics)
- `runtime-runs/<run-id>/genai-asset-eval.md` — quality evaluation scratch output
- `scripts/score-genai.sh` — section scoring script

## Constraints

- Assets with `quality_score < 0.7` must not be promoted to `status='prod'`.
  Holding in dev is the correct outcome; escalate to manual review if score is
  consistently below threshold after retraining.
- ComfyUI job dispatch is single-writer: acquire `/tmp/vwbridge-genai.lock` before
  starting a training job. Max 1 training job at a time.
- Asset paths in the registry must be relative to repo root and must correspond to
  actual files tracked by git (`git ls-files assets/plants/`).
- All `.glb` files in `assets/plants/` must have a registry row. Orphaned files are
  a scoring penalty.
- Never hardcode plant geometry on individual VW symbol instances — Plant Style Manager
  governs geometry; registry `asset_id` links the style to the 3D asset.
- The `plant-2d-to-3d` pipeline: extract 2D VW symbol → feature detection (species,
  size, maturity) → query registry for best LOD 300 match → return `asset_id` +
  transform. This pipeline must not block the VW plugin UI thread.
