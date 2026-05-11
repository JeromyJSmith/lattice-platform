"""lattice/bridge/semantic/{semantic_sidecars, landscape_entities}.

Embedding indices are added by 0011_add_embedding_indices.py once the tables
exist; the columns themselves are created here.
"""

from __future__ import annotations

from migrations._helpers import banner, ensure_table

MIGRATION_ID = "0008_create_semantic_tables"

NAMESPACE = "lattice/bridge/semantic"


def schemas(pxt) -> dict[str, dict]:
    return {
        f"{NAMESPACE}/semantic_sidecars": {
            "id":                pxt.String,
            "vw_export_hash":    pxt.String,
            "source_element_id": pxt.String,
            "ifc_class":         pxt.String,
            "common_name":       pxt.String,
            "botanical_name":    pxt.String,
            "container_size":    pxt.String,
            "irrigation_zone":   pxt.String,
            "phenology_notes":   pxt.String,
            "marpa_seed":        pxt.Bool,
            "marpa_status":      pxt.String,    # 'success' | 'partial' | 'fail' | 'not_run'
            "marpa_record":      pxt.Json,      # latest parse_run partial_parse_json
            "text_blob":         pxt.String,    # concatenated, embedded
            "raw_sidecar_slice": pxt.Json,      # subset of sidecar.elements[i]
            "harness_run_id":    pxt.String,
            "ingested_at":       pxt.Timestamp,
        },
        f"{NAMESPACE}/landscape_entities": {
            "id":                pxt.String,
            "entity_id":         pxt.String,    # UUIDv7 stable across reconciliations
            "vw_export_hash":    pxt.String,
            "source_element_id": pxt.String,
            "imodel_id":         pxt.String,    # iTwin home model
            "bis_class":         pxt.String,
            "ifc_class":         pxt.String,
            "common_name":       pxt.String,
            "botanical_name":    pxt.String,
            "container_size":    pxt.String,
            "quantity":          pxt.Int,
            "irrigation_zone":   pxt.String,
            "centroid":          pxt.Json,      # [x, y, z]
            "elevation_m":       pxt.Float,
            "kind":              pxt.String,    # planting | irrigation | topography | hardscape
            "summary_text":      pxt.String,    # human-readable; embedded
            "promoted_at":       pxt.Timestamp,
            "promotion_event_id": pxt.String,
            "raw_payload":       pxt.Json,
        },
    }


def apply(pxt, dry_run: bool) -> dict:
    banner("0008 lattice/bridge/semantic tables", dry_run=dry_run)
    out: dict = {}
    for path, schema in schemas(pxt).items():
        action = ensure_table(pxt, path, schema, dry_run)
        out[path] = {"action": action, "cols": len(schema)}
        print(f"  {path:48s} -> {action} ({len(schema)} cols)")
    return out
