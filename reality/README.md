# reality — As-Built Reality Capture

LATTICE's reality-capture layer turns site observation into Pixeltable rows that mirror onto every platform surface (Cesium globe, ThatOpen viewer, deck.gl analytics, Potree, VW Plant Style, iTwin BIS, OpenConstructionERP).

| Subdir | Capture mode |
|---|---|
| [`drone/`](drone/) | Video streaming + GPS EXIF → `lattice/reality/drone_frames` (image column with georef) |
| [`gaussian-splats/`](gaussian-splats/) | nerfstudio / Luma / Polycam `.ply`/`.splat` → `lattice/reality/gaussian_splats` |
| [`point-clouds/`](point-clouds/) | LiDAR `.las`/`.laz` → PDAL → `lattice/reality/point_cloud_sessions` → Potree tiles |
| [`mirror/`](mirror/) | Cross-platform sync state in `lattice/reality/mirror_state`, divergence reports, broadcaster |

See [`PIPELINE.md`](PIPELINE.md) for the end-to-end flow. Every capture event writes a row to `lattice/reality/*` AND fires the mirror broadcaster so all 7 platform layers update simultaneously. The ground truth lives in `lattice/bridge/project_georef`; every coordinate in this directory traces back to it.
