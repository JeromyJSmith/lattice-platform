# Plant Asset Library

| LOD | Where | What |
|---|---|---|
| 100 | [`lod-100/`](lod-100/) | Spike placeholder geometry — colored cones/spheres/discs/boxes per [`vw-plugin/config/placeholder_rules.json`](../../vw-plugin/config/placeholder_rules.json) |
| 300 | [`lod-300/`](lod-300/) | Realistic botanical mesh (GLB) — from ComfyUI pipeline or licensed library |
| n/a | [`c4d/`](c4d/) | Cinema 4D project per species, Redshift-ready |

Pixeltable contract: every `lattice/bridge/plant_assets` row carries:

```
lod_100_glb     = "assets/plants/lod-100/{species_code}.glb"
lod_300_glb     = "assets/plants/lod-300/{species_code}.glb"
lod_300_c4d     = "assets/plants/c4d/{species_code}.c4d"
```

Asset binaries themselves aren't committed (see [`../README.md`](../README.md) commit policy). Only the layout is fixed.
