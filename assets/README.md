# LATTICE Asset Library

GLB / C4D / material / HDRI assets used by the 3D pipeline. Most binary assets are NOT committed — they're produced by `genai/3d-asset-pipeline/` and stored locally per machine.

| Subdir | Format | Source |
|---|---|---|
| [`plants/lod-100/`](plants/lod-100/) | `.glb` | Procedural spike geometry from the VW C++ plugin |
| [`plants/lod-300/`](plants/lod-300/) | `.glb` | ComfyUI 2D→3D output, manual Blender, or licensed library |
| [`plants/c4d/`](plants/c4d/) | `.c4d` | Cinema 4D project files (one per species), Redshift-ready |
| [`materials/landscape/`](materials/landscape/) | `.rsmaterial` | Redshift PBR materials: grass, bark, stone, water, concrete, wood |
| [`hdri/`](hdri/) | `.exr` | Lighting environments for Redshift renders |

## Commit policy

| Format | Committed? |
|---|---|
| `.gitkeep` | yes (so the layout is visible in the repo) |
| `.glb` (≤ 5 MB) | yes — small placeholder assets are useful as test fixtures |
| `.glb` (> 5 MB) | no — write the path to Pixeltable, store the binary on the LAN |
| `.c4d` | no — large, licensed |
| `.rsmaterial` | no — licensed |
| `.exr` | no — large |

Paths in Pixeltable always reference these locations (`assets/plants/lod-300/{species}.glb`) so the LATTICE runtime can find them regardless of machine.
