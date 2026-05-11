# 3D Plant Asset Creation Pipeline

This is the loop that solves LATTICE's missing-plant-catalog problem. When VW's stock Plant Style library doesn't have a high-fidelity 3D asset for a species we need, we generate one from geo-tagged reference photos — and the resulting GLB flows all the way into VW Plant Style Manager so the LOD100 spike placeholder swaps to LOD300 botanical mesh for every instance globally.

See [`PIPELINE.md`](PIPELINE.md) for the step-by-step.

## Stubs in this directory

- `image-collector.py` — pulls geo-tagged reference images from Cesium map pins
- `mesh-generator.py` — wraps `comfyui-client.py` for the plant-2d-to-3d workflow
- `c4d-exporter.py` — GLB → Cinema 4D project skeleton with Redshift materials
- `vw-style-importer.py` — pushes GLB to VW Plant Style Manager via vwx-mcp
- `quality-reviewer.py` — surfaces generated assets in `/admin` for human review
