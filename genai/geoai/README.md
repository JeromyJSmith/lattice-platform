# GeoAI — Tree detection, species ID, shadow segmentation

All models run locally on Apple Silicon (MPS backend) and are fine-tunable on MARPA project imagery. Training runs are tracked in `lattice/genai/training_runs`.

| Sub | What |
|---|---|
| [`tree-detection/`](tree-detection/) | Detect existing tree crowns from LiDAR + orthophoto |
| [`species-classifier/`](species-classifier/) | Classify plant species from site reference photos |
| [`shadow-segmentation/`](shadow-segmentation/) | Segment shadow areas from orthophoto for solar analysis |

Outputs feed back into Pixeltable: tree detections become `lattice/bridge/existing_trees` rows (future table — tracked); shadow polygons become deck.gl layers in Context B.
