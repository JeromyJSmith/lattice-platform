# reality/point-clouds — LiDAR + photogrammetric point cloud ingest

`.las` / `.laz` from drone LiDAR or photogrammetric SfM → PDAL pipeline → `lattice/reality/point_cloud_sessions` → PotreeConverter tiles served at `public/potree/{project_id}/`.

| File | Purpose |
|---|---|
| `pdal-pipeline.json` | Default PDAL pipeline: reproject, classify, filter, tile |
| `las-ingest.py` | Run the PDAL pipeline; write session row; trigger PotreeConverter |
| `classify-vegetation.py` | Separate veg returns for tree extraction |
| `extract-trees.py` | DBSCAN on veg returns → tree crown centroids → `lattice/bridge/existing_trees` (future) |

Tracked in the POINT CLOUD section of [`meta/FEATURE_BACKLOG.md`](../../meta/FEATURE_BACKLOG.md).
