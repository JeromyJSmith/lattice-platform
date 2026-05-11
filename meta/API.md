# LATTICE FastAPI Endpoint Reference

Canonical reference for the LATTICE sidecar FastAPI surface.

## Overview

- **Base URL:** `http://127.0.0.1:8765` (TCP dev) or `unix:///tmp/vwbridge-pxt.sock` (production)
- **33 endpoints** across 10 routers (2 app-level + 31 router-level)
- **Sidecar entrypoint:** `pixeltable/service/main.py`
- **Auth:** none (local dev). `LATTICE_API_KEY` header planned for Phase 3.
- **Idempotency:** all write routes require an `Idempotency-Key` header (8..256 chars). Replays within 24h are returned from cache.

## App-level

| Method | Path | Status | Purpose |
|---|---|---|---|
| GET | `/healthz` | live | Process liveness probe |
| GET | `/version` | live | Build + migration metadata |

## /v1/runtime (4 endpoints)

| Method | Path | Status | Purpose |
|---|---|---|---|
| POST | `/v1/runtime/events` | live | Append agent stream events |
| GET | `/v1/runtime/runs` | live | List recent `agent_runs` rows |
| GET | `/v1/runtime/stream-events` | live | Polling fetch for stream deltas (1s cadence) |
| GET | `/v1/runtime/stream-events/sse` | live | SSE push stream (replaces polling) |

## /v1/vw (1 endpoint)

| Method | Path | Status | Purpose |
|---|---|---|---|
| POST | `/v1/vw/sidecars` | live | Register a VW export sidecar |

## /v1/itwin (3 endpoints)

| Method | Path | Status | Purpose |
|---|---|---|---|
| POST | `/v1/itwin/sync-jobs` | live | Create iTwin sync job |
| POST | `/v1/itwin/changed-elements` | live | Submit changed-element manifest |
| POST | `/v1/itwin/poll` | live | Poll for new changes |

## /v1/marpa (1 endpoint)

| Method | Path | Status | Purpose |
|---|---|---|---|
| POST | `/v1/marpa/parse-runs` | live | Record a MARPA parse run |

## /v1/semantic (1 endpoint)

| Method | Path | Status | Purpose |
|---|---|---|---|
| POST | `/v1/semantic/search` | live | Embedding-based semantic search across `landscape_entities` |

## /v1/evidence (1 endpoint)

| Method | Path | Status | Purpose |
|---|---|---|---|
| POST | `/v1/evidence/promotions` | live | Record QA promotion event |

## /v1/health (2 endpoints)

| Method | Path | Status | Purpose |
|---|---|---|---|
| POST | `/v1/health/drift` | live | Record schema drift event |
| GET | `/v1/health/gap-matrix/{vw_export_hash}` | live | Read bridge gap matrix |

## /v1/georef (11 endpoints)

| Method | Path | Status | Purpose |
|---|---|---|---|
| POST | `/v1/georef/ingest/config` | [stub 501] | Ingest `georef.config.json` for a project |
| POST | `/v1/georef/ingest/kml` | [stub 501] | Ingest KML boundary |
| POST | `/v1/georef/ingest/shapefile` | [stub 501] | Ingest Shapefile boundary |
| POST | `/v1/georef/ingest/geotiff` | [stub 501] | Ingest GeoTIFF DEM / orthophoto |
| POST | `/v1/georef/ingest/survey-csv` | [stub 501] | Ingest surveyor CSV (control points) |
| POST | `/v1/georef/ingest/ifc` | [stub 501] | Extract georef from IFC `IfcSite` |
| POST | `/v1/georef/ingest/osm` | [stub 501] | Ingest OSM way/area by ID |
| POST | `/v1/georef/compute-transforms/{project_id}` | [stub 501] | Compute all 4 transform matrices |
| GET | `/v1/georef/{project_id}` | live | Read full georef record |
| GET | `/v1/georef/{project_id}/transforms` | live | Read only the 4 transform matrices |
| GET | `/v1/georef/{project_id}/boundary.geojson` | live | Boundary as GeoJSON Feature |

## /v1/reality (7 endpoints)

| Method | Path | Status | Purpose |
|---|---|---|---|
| POST | `/v1/reality/drone/ingest-video` | [stub 501] | Stream-decode MP4 → `drone_frames` |
| POST | `/v1/reality/drone/ingest-frames` | [stub 501] | Bulk ingest pre-extracted frames |
| POST | `/v1/reality/splat/ingest` | [stub 501] | Ingest .ply/.splat from nerfstudio/Luma/Polycam |
| POST | `/v1/reality/pointcloud/ingest` | [stub 501] | Ingest .las/.laz via PDAL |
| GET | `/v1/reality/mirror/{project_id}` | live | Read `mirror_state` for project |
| POST | `/v1/reality/mirror/{project_id}/sync` | [stub 501] | Trigger full 7-platform sync |
| GET | `/v1/reality/mirror/{project_id}/divergence` | live | Read C2C divergence report |

## Stub Policy

Endpoints marked `[stub 501]` return HTTP 501 Not Implemented until the underlying converter or pipeline lands. They are intentional placeholders — **do not remove them**. They define the contract the implementation must satisfy.

Tracking issues:
- Georef converters → [GH #224](https://github.com/) labeled `georef`, `agent-ready`
- Reality ingest pipelines → [GH #225](https://github.com/) labeled `reality-capture`, `agent-ready`

## Adding endpoints

When you add a new endpoint:
1. Add the route to the appropriate file under `pixeltable/service/routes/`
2. If creating a new router, register it in `pixeltable/service/main.py`
3. Update this file (`meta/API.md`) AND `meta/ARCHITECTURE.md` endpoint count in the same commit
4. The `docs-sync-check` workflow will block merge if counts drift
