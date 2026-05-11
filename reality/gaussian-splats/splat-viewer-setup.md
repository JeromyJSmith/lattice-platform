# Splat Viewer Setup

LATTICE renders 3DGS splats in the browser alongside ThatOpen Fragment models.

## Recommended runtime

- **gsplat web** (https://github.com/playcanvas/supersplat) — pure WebGL2, no WebGPU required, runs everywhere
- **Brush** (https://github.com/ArthurBrussee/brush) — WebGPU, faster but requires Chrome/Edge with WebGPU on

## Loading in the viewer

The `/viewer` route looks up the active project's `gaussian_splats` rows and renders the latest one with `processing_status='complete'`. The splat is positioned in the Three.js scene using `transform_to_wgs84` from the row (decomposed into translation + rotation + scale).

A toggle in the viewer toolbar lets the operator show / hide the splat against the IFC Fragment model. The splat is rendered on a separate WebGL layer so it composites cleanly with the IFC mesh.

Tracked in the matching GitHub Issue: "Gaussian splat ingest + georef alignment + 3DGS browser viewer".
