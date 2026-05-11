# Tree Detection

Input: point cloud from `lattice/bridge/point_clouds` (future) + orthophoto from `lattice/bridge/reference_images` (where `source = 'drone'` or `'satellite'`).

Output: tree crown polygons + species confidence written to `lattice/bridge/existing_trees` (future table).

Files (stubs):
- `detect-trees.py` — inference script
- `train.py` — fine-tune on MARPA project data

Tracked in [`meta/FEATURE_BACKLOG.md`](../../../meta/FEATURE_BACKLOG.md) § LOCAL AI / GENAI / GEOAI / ML → "GeoAI tree detection".
