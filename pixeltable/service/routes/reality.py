"""Reality routes — drone, gaussian splats, point clouds, mirror state.

All endpoints are stubs (501) until the matching pipeline scripts in
`reality/` are implemented. Handler shape and contract are stable.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Body, Depends, File, Form, HTTPException, UploadFile

from service.deps import (
    get_idem_store,
    get_pxt,
    require_idempotency_key,
    require_local_socket_or_token,
)

router = APIRouter(dependencies=[Depends(require_local_socket_or_token)])
log = logging.getLogger("vwbridge.reality")

T_DRONE_FLIGHTS = "lattice/reality/drone_flights"
T_DRONE_FRAMES  = "lattice/reality/drone_frames"
T_SPLATS        = "lattice/reality/gaussian_splats"
T_POINT_CLOUDS  = "lattice/reality/point_cloud_sessions"
T_MIRROR        = "lattice/reality/mirror_state"


# ----- drone --------------------------------------------------------------

@router.post("/drone/ingest-video")
async def drone_ingest_video(
    project_id: str = Form(...),
    flight_id: str = Form(...),
    file: UploadFile = File(...),
    pxt=Depends(get_pxt),
    idem_key: str = Depends(require_idempotency_key),
):
    """Stream-decode an MP4: per frame extract GPS EXIF + insert one
    `drone_frames` row with `image` column. Non-blocking — frames flow into
    Pixeltable as ffmpeg decodes them. See `reality/drone/video-ingest.py`."""
    raise HTTPException(501, "drone/ingest-video stub")


@router.post("/drone/ingest-frames")
async def drone_ingest_frames(
    project_id: str = Form(...),
    flight_id: str = Form(...),
    files: list[UploadFile] = File(...),
    pxt=Depends(get_pxt),
    idem_key: str = Depends(require_idempotency_key),
):
    """Folder of geotagged JPGs (with EXIF) → drone_frames inserts."""
    raise HTTPException(501, "drone/ingest-frames stub")


# ----- gaussian splats ----------------------------------------------------

@router.post("/splat/ingest")
async def splat_ingest(
    project_id: str = Form(...),
    flight_id: str = Form(""),
    transform_to_wgs84: str = Form(""),  # JSON 4x4
    file: UploadFile = File(...),
    pxt=Depends(get_pxt),
    idem_key: str = Depends(require_idempotency_key),
):
    """.ply or .splat + transform → gaussian_splats row. See
    `reality/gaussian-splats/splat-georef.py`."""
    raise HTTPException(501, "splat/ingest stub")


# ----- point clouds -------------------------------------------------------

@router.post("/pointcloud/ingest")
async def pointcloud_ingest(
    project_id: str = Form(...),
    sensor_type: str = Form(...),  # 'lidar' | 'photogrammetry'
    file: UploadFile = File(...),
    pxt=Depends(get_pxt),
    idem_key: str = Depends(require_idempotency_key),
):
    """.las / .laz → PDAL pipeline → point_cloud_sessions row + PotreeConverter.

    See `reality/point-clouds/pdal-pipeline.json` + `las-ingest.py`."""
    raise HTTPException(501, "pointcloud/ingest stub")


# ----- mirror state -------------------------------------------------------

@router.get("/mirror/{project_id}")
def mirror_get(project_id: str, pxt=Depends(get_pxt)):
    """Return the latest mirror_state row for a project (7 sync flags +
    divergence + counts)."""
    t = pxt.get_table(T_MIRROR)
    rows = list(t.where(t.project_id == project_id).collect())
    if not rows:
        raise HTTPException(404, f"no mirror_state row for project_id={project_id!r}")
    return {"project_id": project_id, "row": dict(rows[0])}


@router.post("/mirror/{project_id}/sync")
def mirror_sync(project_id: str, pxt=Depends(get_pxt)):
    """Run the 7-layer sync check, upsert mirror_state. See
    `reality/mirror/sync-checker.py` for the per-layer probes."""
    raise HTTPException(501, "mirror/sync stub")


@router.get("/mirror/{project_id}/divergence")
def mirror_divergence(project_id: str, pxt=Depends(get_pxt)):
    """Return the latest CloudComPy C2C divergence report. See
    `reality/mirror/divergence-report.py`."""
    raise HTTPException(501, "mirror/divergence stub")
