"""0013 — unified georef + reality capture + digital twin mirror.

Adds the canonical per-project coordinate authority and the as-built
reality-capture layer, plus the mirror_state table that tracks platform
sync (VW design, iTwin BIM, DDC admin, Cesium globe, ThatOpen viewer,
deck.gl analytics, Potree point cloud).

What this migration creates:

  lattice/bridge/project_georef          — per-project coord authority (new)
  lattice/reality/drone_flights          — drone capture sessions (new)
  lattice/reality/drone_frames           — per-frame georef + image (new)
  lattice/reality/gaussian_splats        — 3DGS reconstructions (new)
  lattice/reality/point_cloud_sessions   — LiDAR / photogrammetry sessions (new)
  lattice/reality/mirror_state           — 7-platform sync state (new)

What this migration idempotently re-ensures (created by 0012):

  lattice/bridge/plant_assets
  lattice/bridge/marpa_projects
  lattice/bridge/site_zones
  lattice/bridge/reference_images
  lattice/genai/comfyui_jobs
  lattice/genai/model_registry
  lattice/genai/training_runs

And ensures every ifc_elements column from the unified spec is present
(0012 already added all of them — this is a no-op safety net).

Type-surface note: Pixeltable 0.6.0 has no native Geometry / PostGIS column
type. All geometry columns store WKT or GeoJSON text in `pxt.String`. Raw
SQL spatial queries against the underlying PG 16 / PostGIS extension layer
on top (tracked under issue #185).
"""

from __future__ import annotations

from migrations._helpers import (
    OWNED_PARENTS,
    assert_ownership,
    banner,
    ensure_column,
    ensure_namespace,
    ensure_table,
)

MIGRATION_ID = "0013_georef_reality_mirror"

IFC_ELEMENTS = "lattice/bridge/ifc/ifc_elements"


# ---------- project_georef (new) -----------------------------------------

def _project_georef_schema(pxt) -> dict[str, object]:
    return {
        # identity
        "id":                         pxt.String,
        "project_id":                 pxt.String,
        "config_file_hash":           pxt.String,
        "config_version":             pxt.String,
        "source_priority":            pxt.String,    # JSON array, e.g. ["survey","ifc","gps"]

        # canonical WGS84 (master truth)
        "longitude":                  pxt.Float,
        "latitude":                   pxt.Float,
        "elevation_m":                pxt.Float,
        "true_north_degrees":         pxt.Float,

        # coordinate system
        "epsg_code":                  pxt.String,
        "proj_string":                pxt.String,
        "wkt_crs":                    pxt.String,
        "vertical_datum":             pxt.String,
        "units":                      pxt.String,

        # site boundary
        "boundary_wkt_wgs84":         pxt.String,
        "boundary_wkt_project":       pxt.String,
        "boundary_geojson":           pxt.String,
        "bounding_box_json":          pxt.String,
        "area_m2":                    pxt.Float,

        # survey
        "survey_easting":             pxt.Float,
        "survey_northing":            pxt.Float,
        "survey_elevation_units":     pxt.Float,
        "benchmark_elevation_m":      pxt.Float,
        "state_plane_zone":           pxt.String,
        "control_points_json":        pxt.String,
        "benchmark_id":               pxt.String,
        "surveyor_name":              pxt.String,
        "survey_date":                pxt.String,
        "survey_file_path":           pxt.String,

        # IFC georef from IfcSite
        "ifc_ref_latitude":           pxt.Float,
        "ifc_ref_longitude":          pxt.Float,
        "ifc_ref_elevation":          pxt.Float,
        "ifc_placement_matrix":       pxt.String,    # JSON 4x4

        # VW internal
        "vw_origin_x":                pxt.Float,
        "vw_origin_y":                pxt.Float,
        "vw_scale":                   pxt.Float,
        "vw_rotation_deg":            pxt.Float,
        "vw_units":                   pxt.String,

        # OSM
        "osm_node_id":                pxt.String,
        "osm_way_id":                 pxt.String,
        "osm_relation_id":            pxt.String,
        "osm_geojson_file":           pxt.String,
        "osm_last_fetched":           pxt.String,

        # elevation / terrain
        "dem_file_path":              pxt.String,
        "dem_source":                 pxt.String,
        "dem_resolution_m":           pxt.Float,
        "min_elevation_m":            pxt.Float,
        "max_elevation_m":            pxt.Float,

        # aerial imagery
        "orthophoto_file_path":       pxt.String,
        "orthophoto_source":          pxt.String,
        "orthophoto_resolution_cm":   pxt.Float,
        "orthophoto_date":            pxt.String,

        # pre-computed transforms (4x4 matrices, JSON-in-String)
        "transform_vw_to_wgs84":      pxt.String,
        "transform_wgs84_to_ecef":    pxt.String,
        "transform_project_to_utm":   pxt.String,
        "transform_ifc_to_wgs84":     pxt.String,

        # format flags
        "has_kml":                    pxt.Bool,
        "has_shapefile":              pxt.Bool,
        "has_geopackage":             pxt.Bool,
        "has_geotiff_dem":            pxt.Bool,
        "has_orthophoto":             pxt.Bool,
        "has_survey_csv":             pxt.Bool,
        "has_ifc_georef":             pxt.Bool,
        "has_osm":                    pxt.Bool,

        # admin
        "created_at":                 pxt.Timestamp,
        "updated_at":                 pxt.Timestamp,
        "notes":                      pxt.String,
    }


# ---------- reality capture tables (new) ---------------------------------

def _drone_flights_schema(pxt) -> dict[str, object]:
    return {
        "id":                pxt.String,
        "flight_id":         pxt.String,
        "project_id":        pxt.String,
        "pilot":             pxt.String,
        "drone_model":       pxt.String,
        "sensor":            pxt.String,
        "raw_video_path":    pxt.String,
        "flight_path_geojson": pxt.String,
        "boundary_wkt":      pxt.String,
        "epsg_code":         pxt.String,
        "processing_status": pxt.String,
        "notes":             pxt.String,
        "gsd_cm":            pxt.Float,
        "altitude_m":        pxt.Float,
        "overlap_pct":       pxt.Float,
        "coverage_area_m2":  pxt.Float,
        "fps":               pxt.Float,
        "frame_count":       pxt.Int,
        "resolution_w":      pxt.Int,
        "resolution_h":      pxt.Int,
        "has_rtk_gps":       pxt.Bool,
        "flight_date":       pxt.Timestamp,
        "created_at":        pxt.Timestamp,
    }


def _drone_frames_schema(pxt) -> dict[str, object]:
    return {
        "id":                  pxt.String,
        "frame_id":            pxt.String,
        "flight_id":           pxt.String,
        "project_id":          pxt.String,
        "geom_point_wkt":      pxt.String,
        "epsg_code":           pxt.String,
        "image":               pxt.Image,
        "longitude":           pxt.Float,
        "latitude":            pxt.Float,
        "altitude_m":          pxt.Float,
        "heading_deg":         pxt.Float,
        "pitch_deg":           pxt.Float,
        "roll_deg":            pxt.Float,
        "gimbal_pitch":        pxt.Float,
        "timestamp_sec":       pxt.Float,
        "blur_score":          pxt.Float,
        "frame_index":         pxt.Int,
        "embedding":           pxt.String,    # JSON array
        "detected_objects":    pxt.String,    # JSON
        "detected_plants":     pxt.String,    # JSON
        "detected_trees":      pxt.String,    # JSON
        "matched_element_ids": pxt.String,    # JSON
        "is_keyframe":         pxt.Bool,
    }


def _gaussian_splats_schema(pxt) -> dict[str, object]:
    return {
        "id":                      pxt.String,
        "splat_id":                pxt.String,
        "project_id":              pxt.String,
        "flight_id":               pxt.String,
        "name":                    pxt.String,
        "software":                pxt.String,
        "method":                  pxt.String,
        "splat_file_path":         pxt.String,
        "web_viewer_path":         pxt.String,
        "coverage_wkt":            pxt.String,
        "epsg_code":               pxt.String,
        "transform_to_wgs84":      pxt.String,
        "processing_status":       pxt.String,
        "processing_log":          pxt.String,
        "notes":                   pxt.String,
        "matched_ifc_elements":    pxt.String,
        "matched_point_clouds":    pxt.String,
        "matched_existing_trees":  pxt.String,
        "longitude_origin":        pxt.Float,
        "latitude_origin":         pxt.Float,
        "elevation_origin":        pxt.Float,
        "resolution_cm":           pxt.Float,
        "quality_score":           pxt.Float,
        "frame_count":             pxt.Int,
        "point_count":             pxt.Int,
        "created_date":            pxt.Timestamp,
    }


def _point_cloud_sessions_schema(pxt) -> dict[str, object]:
    return {
        "id":                       pxt.String,
        "session_id":               pxt.String,
        "project_id":               pxt.String,
        "flight_id":                pxt.String,
        "sensor_type":              pxt.String,
        "source_format":            pxt.String,
        "raw_file_path":            pxt.String,
        "processed_file_path":      pxt.String,
        "potree_tiles_path":        pxt.String,
        "epsg_code":                pxt.String,
        "boundary_wkt":             pxt.String,
        "pdal_pipeline_json":       pxt.String,
        "c2c_comparison_id":        pxt.String,
        "processing_status":        pxt.String,
        "notes":                    pxt.String,
        "matched_splat_ids":        pxt.String,
        "longitude_origin":         pxt.Float,
        "latitude_origin":          pxt.Float,
        "elevation_origin":         pxt.Float,
        "density_pts_per_m2":       pxt.Float,
        "min_elevation_m":          pxt.Float,
        "max_elevation_m":          pxt.Float,
        "avg_elevation_m":          pxt.Float,
        "classified_ground_pct":    pxt.Float,
        "classified_veg_pct":       pxt.Float,
        "classified_building_pct":  pxt.Float,
        "point_count":              pxt.Int,
        "has_rgb":                  pxt.Bool,
        "has_intensity":            pxt.Bool,
        "has_classification":       pxt.Bool,
        "existing_trees_extracted": pxt.Bool,
        "terrain_mesh_generated":   pxt.Bool,
        "capture_date":             pxt.Timestamp,
        "created_at":               pxt.Timestamp,
    }


def _mirror_state_schema(pxt) -> dict[str, object]:
    return {
        "id":                            pxt.String,
        "mirror_id":                     pxt.String,
        "project_id":                    pxt.String,
        "latest_flight_id":              pxt.String,
        "latest_splat_id":                pxt.String,
        "latest_point_cloud_id":         pxt.String,
        "vw_last_export_hash":           pxt.String,
        "sync_warnings":                 pxt.String,   # JSON array
        "design_reality_divergence_m":   pxt.Float,
        "ifc_element_count":             pxt.Int,
        "plant_element_count":           pxt.Int,
        "new_objects_in_reality":        pxt.Int,
        "missing_objects_in_scan":       pxt.Int,
        "cesium_globe_synced":           pxt.Bool,
        "thatopen_viewer_synced":        pxt.Bool,
        "deckgl_layer_synced":           pxt.Bool,
        "potree_tiles_synced":           pxt.Bool,
        "vw_placeholders_synced":        pxt.Bool,
        "itwin_bis_synced":              pxt.Bool,
        "erp_boq_synced":                pxt.Bool,
        "checked_at":                    pxt.Timestamp,
        "reality_capture_date":          pxt.Timestamp,
        "vw_last_export_date":           pxt.Timestamp,
        "erp_boq_last_sync":             pxt.Timestamp,
        "cwicr_cost_last_sync":          pxt.Timestamp,
        "linear_last_sync":              pxt.Timestamp,
        "notes":                         pxt.String,
    }


# ---------- 0012 tables (idempotent re-ensure, for migration coherence) --

def _plant_assets_schema(pxt) -> dict[str, object]:
    return {
        "id":                pxt.String,
        "asset_id":          pxt.String,
        "species_code":      pxt.String,
        "common_name":       pxt.String,
        "scientific_name":   pxt.String,
        "family":            pxt.String,
        "lod_100_glb":       pxt.String,
        "lod_300_glb":       pxt.String,
        "lod_300_c4d":       pxt.String,
        "vw_style_name":     pxt.String,
        "asset_source":      pxt.String,
        "comfyui_workflow_id": pxt.String,
        "cesium_pin_icon":   pxt.String,
        "crown_radius_m":    pxt.Float,
        "mature_height_m":   pxt.Float,
        "canopy_density":    pxt.Float,
        "reference_images":  pxt.Json,
        "capabilities":      pxt.Json,
        "is_custom":         pxt.Bool,
        "created_at":        pxt.Timestamp,
        "updated_at":        pxt.Timestamp,
        "raw_event":         pxt.Json,
    }


def _marpa_projects_schema(pxt) -> dict[str, object]:
    # NB: this matches what 0012 actually created; if the table is missing
    # (fresh PXT instance) we create with this shape.
    return {
        "id":                  pxt.String,
        "project_id":          pxt.String,
        "name":                pxt.String,
        "address":             pxt.String,
        "longitude":           pxt.Float,
        "latitude":            pxt.Float,
        "elevation_m":         pxt.Float,
        "geom_point_wkt":      pxt.String,
        "geom_boundary_wkt":   pxt.String,
        "epsg_code":           pxt.String,
        "status":              pxt.String,
        "phase":               pxt.String,
        "project_manager":     pxt.String,
        "client_name":         pxt.String,
        "start_date":          pxt.Timestamp,
        "end_date":            pxt.Timestamp,
        "ifc_path":            pxt.String,
        "fragment_cache_path": pxt.String,
        "thumbnail_url":       pxt.String,
        "total_area_m2":       pxt.Float,
        "estimated_value":     pxt.Float,
        "actual_cost":         pxt.Float,
        "erp_project_id":      pxt.String,
        "linear_project_id":   pxt.String,
        "open_issues":         pxt.Int,
        "tasks_complete":      pxt.Int,
        "tasks_total":         pxt.Int,
        "last_activity":       pxt.Timestamp,
        "cesium_fly_height":   pxt.Float,
        "notes":               pxt.String,
        "raw_event":           pxt.Json,
    }


def _site_zones_schema(pxt) -> dict[str, object]:
    return {
        "id":                pxt.String,
        "zone_id":           pxt.String,
        "project_id":        pxt.String,
        "zone_name":         pxt.String,
        "zone_type":         pxt.String,
        "geom_polygon_wkt":  pxt.String,
        "epsg_code":         pxt.String,
        "area_m2":           pxt.Float,
        "irrigation_zone":   pxt.String,
        "maintenance_zone":  pxt.String,
        "solar_exposure":    pxt.String,
        "notes":             pxt.String,
    }


def _reference_images_schema(pxt) -> dict[str, object]:
    return {
        "id":              pxt.String,
        "image_id":        pxt.String,
        "project_id":      pxt.String,
        "image":           pxt.Image,
        "longitude":       pxt.Float,
        "latitude":        pxt.Float,
        "geom_point_wkt":  pxt.String,
        "epsg_code":       pxt.String,
        "captured_at":     pxt.Timestamp,
        "source":          pxt.String,
        "species_tag":     pxt.String,
        "element_id":      pxt.String,
        "used_in_comfyui": pxt.Bool,
        "comfyui_job_id":  pxt.String,
        "embedding":       pxt.Json,
        "notes":           pxt.String,
    }


def _comfyui_jobs_schema(pxt) -> dict[str, object]:
    return {
        "id":                pxt.String,
        "job_id":            pxt.String,
        "species_code":      pxt.String,
        "input_images":      pxt.Json,
        "cesium_location":   pxt.Json,
        "workflow_name":     pxt.String,
        "workflow_params":   pxt.Json,
        "status":            pxt.String,
        "output_images":     pxt.Json,
        "output_mesh_path":  pxt.String,
        "output_glb_path":   pxt.String,
        "c4d_project_path":  pxt.String,
        "vw_style_assigned": pxt.Bool,
        "quality_score":     pxt.Float,
        "created_at":        pxt.Timestamp,
        "completed_at":      pxt.Timestamp,
        "run_id":            pxt.String,
    }


def _model_registry_schema(pxt) -> dict[str, object]:
    return {
        "id":              pxt.String,
        "model_id":        pxt.String,
        "model_name":      pxt.String,
        "model_type":      pxt.String,
        "provider":        pxt.String,
        "endpoint":        pxt.String,
        "context_length":  pxt.Int,
        "capabilities":    pxt.Json,
        "quantization":    pxt.String,
        "size_gb":         pxt.Float,
        "vram_gb":         pxt.Float,
        "apple_silicon":   pxt.Bool,
        "use_cases":       pxt.Json,
        "status":          pxt.String,
        "last_used":       pxt.Timestamp,
        "notes":           pxt.String,
    }


def _training_runs_schema(pxt) -> dict[str, object]:
    return {
        "id":              pxt.String,
        "run_id":          pxt.String,
        "model_name":      pxt.String,
        "task_type":       pxt.String,
        "dataset_source":  pxt.String,
        "input_table":     pxt.String,
        "n_samples":       pxt.Int,
        "epochs":          pxt.Int,
        "val_accuracy":    pxt.Float,
        "checkpoint_path": pxt.String,
        "status":          pxt.String,
        "started_at":      pxt.Timestamp,
        "completed_at":    pxt.Timestamp,
        "notes":           pxt.String,
    }


# ---------- ifc_elements extension list (idempotent) ----------------------

def _ifc_elements_extensions(pxt) -> dict[str, object]:
    """Columns called out in the unified spec. All were added by 0012;
    ensure_column reports 'exists' for every one — this block is a safety
    net so re-running the migration trail produces a consistent result."""
    return {
        "erp_item_id":            pxt.String,
        "unit_cost":              pxt.Float,
        "unit_cost_region":       pxt.String,
        "quantity_unit":          pxt.String,
        "boq_phase":              pxt.String,
        "asset_id":               pxt.String,
        "asset_source":           pxt.String,
        "glb_path":               pxt.String,
        "thumbnail_url":          pxt.String,
        "geom_point_wkt":         pxt.String,
        "epsg_code":              pxt.String,
        "bis_class":              pxt.String,
        "bis_subclass":           pxt.String,
        "bis_federation_guid":    pxt.String,
        "ifc_global_id":          pxt.String,
        "ifc_version":            pxt.String,
        "lod_level":              pxt.Int,
        "placeholder_color":      pxt.String,
        "placeholder_height_m":   pxt.Float,
        "reference_images":       pxt.Json,
    }


# ---------- entry point ---------------------------------------------------

def apply(pxt, dry_run: bool) -> dict:
    assert_ownership(pxt, OWNED_PARENTS)
    banner("0013 georef + reality + digital twin mirror", dry_run=dry_run)
    out: dict = {}

    # 1. Namespace (lattice/reality is new; lattice/genai is idempotent).
    out["lattice/reality"] = ensure_namespace(pxt, "lattice/reality", dry_run)
    print(f"  lattice/reality                              -> {out['lattice/reality']}")

    # 2. Bridge tables — project_georef is new; the rest are 0012 no-ops.
    bridge = {
        "lattice/bridge/project_georef":   _project_georef_schema(pxt),
        "lattice/bridge/plant_assets":     _plant_assets_schema(pxt),
        "lattice/bridge/marpa_projects":   _marpa_projects_schema(pxt),
        "lattice/bridge/site_zones":       _site_zones_schema(pxt),
        "lattice/bridge/reference_images": _reference_images_schema(pxt),
    }
    for path, schema in bridge.items():
        out[path] = ensure_table(pxt, path, schema, dry_run)
        print(f"  {path:46s} -> {out[path]} ({len(schema)} cols)")

    # 3. GenAI tables — all 0012 no-ops.
    genai = {
        "lattice/genai/comfyui_jobs":   _comfyui_jobs_schema(pxt),
        "lattice/genai/model_registry": _model_registry_schema(pxt),
        "lattice/genai/training_runs":  _training_runs_schema(pxt),
    }
    for path, schema in genai.items():
        out[path] = ensure_table(pxt, path, schema, dry_run)
        print(f"  {path:46s} -> {out[path]} ({len(schema)} cols)")

    # 4. Reality tables (all new).
    reality = {
        "lattice/reality/drone_flights":        _drone_flights_schema(pxt),
        "lattice/reality/drone_frames":         _drone_frames_schema(pxt),
        "lattice/reality/gaussian_splats":      _gaussian_splats_schema(pxt),
        "lattice/reality/point_cloud_sessions": _point_cloud_sessions_schema(pxt),
        "lattice/reality/mirror_state":         _mirror_state_schema(pxt),
    }
    for path, schema in reality.items():
        out[path] = ensure_table(pxt, path, schema, dry_run)
        print(f"  {path:46s} -> {out[path]} ({len(schema)} cols)")

    # 5. ifc_elements column safety-net (all from 0012; should report 'exists').
    ext = _ifc_elements_extensions(pxt)
    ifc_results = {col: ensure_column(pxt, IFC_ELEMENTS, col, ctype, dry_run)
                   for col, ctype in ext.items()}
    out[IFC_ELEMENTS] = ifc_results
    added = sum(1 for v in ifc_results.values() if v in ("added", "would add"))
    skipped = sum(1 for v in ifc_results.values() if v == "exists")
    print(f"  {IFC_ELEMENTS:46s} -> +{added} cols, {skipped} pre-existing")

    return out
