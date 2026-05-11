# reality/gaussian-splats — 3D Gaussian Splat capture

3DGS reconstructions from nerfstudio, Luma AI, or Polycam land here. Each `.ply`/`.splat` file is aligned to `lattice/bridge/project_georef` via control points or ICP, then registered as a `lattice/reality/gaussian_splats` row.

| File | Purpose |
|---|---|
| `nerfstudio-ingest.py` | Wrap a nerfstudio export → write splat row |
| `splat-georef.py` | Align an arbitrary splat to project_georef (control points / ICP) |
| `splat-viewer-setup.md` | How to render the splat in the ThatOpen viewer alongside an IFC |

The splat is served to the browser viewer via the `web_viewer_path` column. Compatible viewers: SuperSplat, Brush, gsplat web renderer.
