# Reality Capture agent

LiDAR + drone + 360° capture pipelines. Drives `laspy` + `pdal` + `open3d` + `PotreeConverter` locally, writes results to `lattice/bridge/point_clouds` and serves Potree octrees from `public/potree/`.

All processing is local — no Bentley Reality Data cloud (see [`meta/ITWIN_MAPPING.md`](../../meta/ITWIN_MAPPING.md) Tier 4).

See [`AGENTS.md`](../../AGENTS.md) and the Point Cloud section of [`meta/FEATURE_BACKLOG.md`](../../meta/FEATURE_BACKLOG.md).
