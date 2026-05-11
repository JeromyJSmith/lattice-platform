# Reality Capture Pipeline — One Ground Truth, Mirrored Everywhere

```
                         project_georef (master coord authority)
                                       │
              ┌────────────────────────┼─────────────────────────┐
              ▼                        ▼                         ▼
       drone video                gaussian splats          LiDAR .las/.laz
              │                        │                         │
              │ ffmpeg + EXIF          │ georef align            │ PDAL pipeline
              │ (streaming, not blocking)                        │ classify, ground extract
              ▼                        ▼                         ▼
       drone_frames               gaussian_splats         point_cloud_sessions
       (pxt.Image + georef)       (.splat + WGS84 origin)  (point cloud + classification)
              │                        │                         │
              │ Pixeltable computed columns:                     │ PotreeConverter
              │  - CLIP embedding                                 │ → public/potree/{project}/
              │  - YOLO detections                                │
              │  - plant/tree detection                           │
              │  - blur_score                                     │
              │  - matched_element_ids (spatial proximity)        │
              ▼                        ▼                         ▼
       ifc_elements.matched   ifc_elements.matched        existing_trees (DBSCAN
       _from_frames           _from_splat                  on veg returns)
              │                        │                         │
              └────────────────────────┼─────────────────────────┘
                                       ▼
                          mirror_state row updated
                          (one per project, 7 sync flags)
                                       │
              ┌────────────────────────┼─────────────────────────┐
              ▼                        ▼                         ▼
     Cesium globe pin       ThatOpen viewer           deck.gl HeatmapLayer
     color-coded by         elements highlighted      of C2C divergence
     sync status            by match status
                                       │
              ┌────────────────────────┼─────────────────────────┐
              ▼                        ▼                         ▼
     VW Plant Style Mgr     iTwin BIS classifier      OpenConstructionERP
     (vwx-mcp push)         (bis_class update)        BOQ refresh
```

Every step writes evidence to `lattice/execution/evidence` so the entire chain is auditable in `/admin`.

## The mirror invariant

After ANY capture event (new flight, new splat, new point cloud) the platform broadcaster fires:

1. Updates `mirror_state.{reality_capture_date, latest_*_id}`
2. Recomputes `design_reality_divergence_m` via CloudComPy C2C
3. Sets `cesium_globe_synced`, `thatopen_viewer_synced`, etc. to false until each layer refetches
4. Posts SSE events to each subscribed layer; layers refresh and set their flag back to true

A pin on the Cesium globe is **green** only when all 7 sync flags are true and the divergence score is below the project threshold.

Tracked in [`meta/FEATURE_BACKLOG.md`](../meta/FEATURE_BACKLOG.md) §§ REALITY CAPTURE and DIGITAL TWIN MIRROR.
