"""Extended schema (migration 0012).

Adds the spatial + administrative + 3D-asset + GenAI surface that everything
in Phase 2+ builds on:

- PostGIS-ish georeferencing columns on `lattice/bridge/ifc/ifc_elements`
  (WKT in pxt.String + lon/lat/elev floats — Pixeltable 0.6.0 has no
  native Geometry type; spatial joins layer on top via raw SQL once needed)
- BIS classification columns on `ifc_elements`
- DDC admin columns on `ifc_elements`
- 3D asset pipeline columns on `ifc_elements`
- A new `lattice/bridge/plant_assets` table (it didn't exist before)
- `lattice/bridge/marpa_projects` registry
- `lattice/bridge/site_zones` for spatial joins
- `lattice/bridge/reference_images` for geo-tagged site photos
- `lattice/genai/` namespace with `comfyui_jobs`, `model_registry`,
  `training_runs`

This is the only place we extend the bridge namespace beyond the seven
sub-namespaces created in 0003. Both `lattice/bridge` and `lattice/genai`
are owned per `_helpers.OWNED_PARENTS`.
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

MIGRATION_ID = "0012_extended_schema"

IFC_ELEMENTS = "lattice/bridge/ifc/ifc_elements"


# ---- column extensions on ifc_elements ----------------------------------

def _ifc_elements_extensions(pxt) -> dict[str, object]:
    """Map column-name -> Pixeltable type. Order is documentation-only.

    Note on geometry storage: `geom_point_wkt` / `geom_footprint_wkt` carry
    OGC Well-Known Text. Pixeltable 0.6.0 has no native Geometry type, so
    we keep WKT in String and run spatial queries (ST_Within, ST_Distance)
    via raw SQL against the underlying PG 16 / PostGIS extension. The
    canonical SRID is EPSG:4326 (WGS84) unless `epsg_code` says otherwise.
    """
    return {
        # PostGIS-ish columns
        "geom_point_wkt":      pxt.String,   # WKT: 'POINT(lon lat)' in WGS84
        "geom_footprint_wkt":  pxt.String,   # WKT: 'POLYGON((...))'
        "epsg_code":           pxt.String,   # e.g. 'EPSG:4326'
        "longitude":           pxt.Float,
        "latitude":            pxt.Float,
        "elevation_m":         pxt.Float,
        "site_zone_id":        pxt.String,   # FK -> site_zones.zone_id

        # BIS / iTwin classification
        "bis_class":              pxt.String,
        "bis_subclass":           pxt.String,
        "bis_federation_guid":    pxt.String,
        "ifc_global_id":          pxt.String,
        "ifc_version":            pxt.String,

        # DDC admin
        "erp_item_id":         pxt.String,
        "unit_cost":           pxt.Float,
        "unit_cost_region":    pxt.String,
        "quantity":            pxt.Float,
        "quantity_unit":       pxt.String,
        "boq_phase":           pxt.String,
        "cost_last_updated":   pxt.Timestamp,

        # 3D asset pipeline
        "asset_id":              pxt.String,
        "lod_level":             pxt.Int,
        "placeholder_color":     pxt.String,
        "placeholder_height_m":  pxt.Float,
        "asset_source":          pxt.String,
        "glb_path":              pxt.String,
        "thumbnail_url":         pxt.String,
        "reference_images":      pxt.Json,
    }


# ---- new table schemas ---------------------------------------------------

def _plant_assets_schema(pxt) -> dict[str, object]:
    return {
        "asset_id":            pxt.String,
        "species_code":        pxt.String,
        "common_name":         pxt.String,
        "scientific_name":     pxt.String,
        "family":              pxt.String,
        "lod_100_glb":         pxt.String,   # spike geometry GLB path
        "lod_300_glb":         pxt.String,   # realistic mesh GLB path
        "lod_300_c4d":         pxt.String,   # Cinema 4D native path
        "crown_radius_m":      pxt.Float,
        "mature_height_m":     pxt.Float,
        "canopy_density":      pxt.Float,    # 0.0-1.0, used by shadow calc
        "asset_source":        pxt.String,   # manual / comfyui / laubwerk / blender
        "vw_style_name":       pxt.String,   # VW Plant Style Manager name
        "reference_images":    pxt.Json,
        "comfyui_workflow_id": pxt.String,   # FK -> genai/comfyui_jobs
        "is_custom":           pxt.Bool,
        "cesium_pin_icon":     pxt.String,
        "created_at":          pxt.Timestamp,
        "updated_at":          pxt.Timestamp,
        "raw_event":           pxt.Json,
    }


def _marpa_projects_schema(pxt) -> dict[str, object]:
    return {
        "id":                  pxt.String,
        "project_id":          pxt.String,
        "name":                pxt.String,
        "address":             pxt.String,
        "longitude":           pxt.Float,
        "latitude":            pxt.Float,
        "elevation_m":         pxt.Float,
        "geom_point_wkt":      pxt.String,   # POINT(lon lat)
        "geom_boundary_wkt":   pxt.String,   # POLYGON((...))
        "epsg_code":           pxt.String,
        "status":              pxt.String,   # active / complete / prospect / archived
        "phase":               pxt.String,
        "project_manager":     pxt.String,
        "client_name":         pxt.String,
        "start_date":          pxt.Timestamp,
        "end_date":            pxt.Timestamp,
        "ifc_path":            pxt.String,
        "fragment_cache_path": pxt.String,   # path to cached .frag (binary too large for pxt.Json)
        "thumbnail_url":       pxt.String,
        "total_area_m2":       pxt.Float,
        "estimated_value":     pxt.Float,
        "actual_cost":         pxt.Float,
        "erp_project_id":      pxt.String,   # FK -> OpenConstructionERP
        "linear_project_id":   pxt.String,   # FK -> Linear
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
        "id":                  pxt.String,
        "zone_id":             pxt.String,
        "project_id":          pxt.String,
        "zone_name":           pxt.String,
        "zone_type":           pxt.String,   # planting / irrigation / hardscape / pool / lawn
        "geom_polygon_wkt":    pxt.String,   # POLYGON((...))
        "epsg_code":           pxt.String,
        "area_m2":             pxt.Float,
        "irrigation_zone":    pxt.String,
        "maintenance_zone":   pxt.String,
        "solar_exposure":     pxt.String,    # full-sun / part-shade / full-shade
        "notes":               pxt.String,
    }


def _reference_images_schema(pxt) -> dict[str, object]:
    return {
        "id":                  pxt.String,
        "image_id":            pxt.String,
        "project_id":          pxt.String,
        "image":               pxt.Image,    # Pixeltable-native image column
        "longitude":           pxt.Float,
        "latitude":            pxt.Float,
        "geom_point_wkt":      pxt.String,
        "epsg_code":           pxt.String,
        "captured_at":         pxt.Timestamp,
        "source":              pxt.String,   # field-photo / streetview / drone / satellite
        "species_tag":         pxt.String,
        "element_id":          pxt.String,   # FK -> ifc_elements.source_element_id
        "used_in_comfyui":     pxt.Bool,
        "comfyui_job_id":      pxt.String,
        "embedding":           pxt.Json,
        "notes":               pxt.String,
    }


def _comfyui_jobs_schema(pxt) -> dict[str, object]:
    return {
        "id":                pxt.String,
        "job_id":            pxt.String,
        "species_code":      pxt.String,
        "input_images":      pxt.Json,
        "cesium_location":   pxt.Json,        # {lon, lat}
        "workflow_name":     pxt.String,
        "workflow_params":   pxt.Json,
        "status":            pxt.String,      # pending / running / complete / failed
        "output_images":     pxt.Json,
        "output_mesh_path":  pxt.String,
        "output_glb_path":   pxt.String,
        "c4d_project_path":  pxt.String,
        "vw_style_assigned": pxt.Bool,
        "quality_score":     pxt.Float,
        "created_at":        pxt.Timestamp,
        "completed_at":      pxt.Timestamp,
        "run_id":            pxt.String,      # FK -> agent_runs
    }


def _model_registry_schema(pxt) -> dict[str, object]:
    return {
        "id":              pxt.String,
        "model_id":        pxt.String,
        "model_name":      pxt.String,
        "model_type":      pxt.String,        # llm / vision / image-gen / 3d-gen / embedding / geoai
        "provider":        pxt.String,        # ollama / lm-studio / comfyui / huggingface / custom
        "endpoint":        pxt.String,
        "context_length":  pxt.Int,
        "capabilities":    pxt.Json,
        "quantization":    pxt.String,
        "size_gb":         pxt.Float,
        "vram_gb":         pxt.Float,
        "apple_silicon":   pxt.Bool,
        "use_cases":       pxt.Json,
        "status":          pxt.String,        # available / loading / unavailable
        "last_used":       pxt.Timestamp,
        "notes":           pxt.String,
    }


def _training_runs_schema(pxt) -> dict[str, object]:
    return {
        "id":              pxt.String,
        "run_id":          pxt.String,
        "model_name":      pxt.String,
        "task_type":       pxt.String,        # tree-detection / species-classification / shadow-seg
        "dataset_source":  pxt.String,        # lidar / orthophoto / streetview / custom
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


# ---- entry point ---------------------------------------------------------

def apply(pxt, dry_run: bool) -> dict:
    assert_ownership(pxt, OWNED_PARENTS)
    banner("0012 extended schema (PostGIS / DDC / 3D / GenAI)", dry_run=dry_run)
    out: dict = {}

    # 1. Ensure the new top-level namespace exists.
    out["lattice/genai"] = ensure_namespace(pxt, "lattice/genai", dry_run)
    print(f"  lattice/genai                              -> {out['lattice/genai']}")

    # 2. Extend ifc_elements with the new columns.
    ext = _ifc_elements_extensions(pxt)
    ifc_results: dict[str, str] = {}
    for col, ctype in ext.items():
        ifc_results[col] = ensure_column(pxt, IFC_ELEMENTS, col, ctype, dry_run)
    out[IFC_ELEMENTS] = ifc_results
    added = sum(1 for v in ifc_results.values() if v in ("added", "would add"))
    skipped = sum(1 for v in ifc_results.values() if v == "exists")
    print(f"  {IFC_ELEMENTS:42s} -> +{added} cols, {skipped} pre-existing")

    # 3. Create plant_assets (new table — did not exist before 0012).
    plant_assets_path = "lattice/bridge/plant_assets"
    out[plant_assets_path] = ensure_table(pxt, plant_assets_path, _plant_assets_schema(pxt), dry_run)
    print(f"  {plant_assets_path:42s} -> {out[plant_assets_path]} ({len(_plant_assets_schema(pxt))} cols)")

    # 4. New bridge-level tables (flat under lattice/bridge/, per the
    #    extended-schema spec — distinct from the per-system sub-namespaces).
    new_bridge_tables = {
        "lattice/bridge/marpa_projects":    _marpa_projects_schema(pxt),
        "lattice/bridge/site_zones":        _site_zones_schema(pxt),
        "lattice/bridge/reference_images":  _reference_images_schema(pxt),
    }
    for path, schema in new_bridge_tables.items():
        out[path] = ensure_table(pxt, path, schema, dry_run)
        print(f"  {path:42s} -> {out[path]} ({len(schema)} cols)")

    # 5. GenAI tables.
    genai_tables = {
        "lattice/genai/comfyui_jobs":   _comfyui_jobs_schema(pxt),
        "lattice/genai/model_registry": _model_registry_schema(pxt),
        "lattice/genai/training_runs":  _training_runs_schema(pxt),
    }
    for path, schema in genai_tables.items():
        out[path] = ensure_table(pxt, path, schema, dry_run)
        print(f"  {path:42s} -> {out[path]} ({len(schema)} cols)")

    return out
