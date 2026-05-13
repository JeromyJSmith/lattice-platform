# GenAI Pipeline Harness — LATTICE Meta-Harness Control

Owns ComfyUI workflows, model registry, training runs, asset registry under `assets/`, plant-2d-to-3d pipeline, quality scoring for LOD 100/300 plants, asset promotion from dev to prod.

## Fitness Function

Score genai health against **asset registry completeness**, **model quality**, and **training pipeline health**:

1. **Asset inventory sync**: every `.glb` in `assets/plants/lod-*/*` has a corresponding row in `lattice/genai/model_registry` with `asset_path` matching, `quality_score >= 0.7` for promoted assets
2. **ComfyUI job tracking**: all jobs spawned to ComfyUI have a row in `lattice/genai/comfyui_jobs` with `status` (pending/running/completed/failed) and `output_path` populated on success
3. **Training run completeness**: each plant training run has input dataset, model checkpoint, output asset, and quality evaluation metrics recorded in `lattice/genai/training_runs`
4. **No orphan assets**: `git ls-files assets/plants/` all have registry entries; no registry rows point to missing `.glb` files
5. **LOD progression**: plants available at LOD 100 (placeholder geometry) and LOD 300 (botanical detail); LOD 100 > LOD 300 in table row count

**Baseline score**: `scripts/score-genai.sh` runs in < 8s, outputs JSON with `asset_sync`, `model_quality_avg`, `training_health`, `orphan_count`, `lod_coverage`.

## Improvement Loop

Autoresearch loop (on every new asset or training run):

1. Run `scripts/score-genai.sh` → baseline snapshot
2. Auto-scan `assets/plants/` for new `.glb` files, check Pixeltable for matching rows
3. Spawn `claude -p` subprocess to evaluate asset quality (geometry fidelity, texture completeness, botanical accuracy), compute quality_score, suggest promotion threshold
4. Write evaluation + promotion decision to `runtime-runs/<run-id>/genai-asset-eval.md`
5. If quality_score >= threshold, promote to prod registry; else hold in dev
6. Flock concurrency: max 1 training job at a time via `/tmp/vwbridge-genai.lock`

## Action Catalog

- **Asset audit**: `find assets/plants -name "*.glb" | sort | while read f; do echo "$f"; done | wc -l` should match `SELECT COUNT(*) FROM lattice.genai.model_registry`
- **Quality check**: `pixeltable select asset_id, quality_score from lattice.genai.model_registry where quality_score < 0.7 order by quality_score` identifies candidates for retraining
- **Training queue**: `pixeltable select id, status from lattice.genai.training_runs where status='pending' or status='running'` shows active training
- **ComfyUI health**: `pixeltable select count(*) from lattice.genai.comfyui_jobs where status='failed'` recent failures (last 24h)
- **LOD audit**: `pixeltable select lod_level, count(*) from lattice.genai.model_registry group by lod_level` verifies LOD distribution

## Operating Mode

- **Asset registration**: new `.glb` → `POST /v1/genai/infer` or direct Pixeltable insert with `asset_path`, `species`, `lod_level`, `quality_score=null` (TBD)
- **ComfyUI dispatch**: training run → generate workflow JSON → spawn ComfyUI server → stream output → store asset path in registry
- **Quality evaluation**: manual human review OR scriptable heuristics (geometry bounds, texture presence, botanical feature detection)
- **Plant-2d-to-3d pipeline**: extract 2D VW symbol → feature detection (species, size, maturity) → query registry for best LOD 300 match → return asset_id + transform
- **Failure mode**: training fails → comfyui_jobs.status='failed'; asset missing → registry orphan; quality_score unset → hold in dev registry until evaluated
