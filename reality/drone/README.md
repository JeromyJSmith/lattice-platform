# reality/drone — Drone video + frame ingest

| File | Purpose |
|---|---|
| `video-ingest.py` | Stream-decode an MP4 with ffmpeg; per-frame: extract GPS/IMU EXIF, write `lattice/reality/drone_frames` row with `image` column |
| `frame-extractor.py` | Sample 1 frame / N seconds from a video, write keyframes |
| `exif-reader.py` | Helper: pull GPS + camera pose from frame EXIF |

The Pixeltable `image` column stores frames inline. Computed columns auto-run CLIP + YOLO + blur scoring on insert. Frames within camera-frustum proximity of an `ifc_elements` row write that row's id into `matched_element_ids`.

Tracked in the REALITY CAPTURE section of [`meta/FEATURE_BACKLOG.md`](../../meta/FEATURE_BACKLOG.md).
