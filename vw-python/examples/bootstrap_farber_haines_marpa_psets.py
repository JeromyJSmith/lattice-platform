"""Bootstrap MARPA custom record-backed IFC Psets in the active Vectorworks file.

Run inside Vectorworks 2026 with the Farber-Haines VWX file open.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone

import vs  # type: ignore


OUT_PATH = "/tmp/farber_haines_marpa_pset_bootstrap.json"

T_BOOL = 2
T_REAL = 3
T_TEXT = 4
T_DEC = 5
F_FLAG = 0

PSET_REGISTRY = {
    "VwPset_MARPA_Object": [
        ("marpa_object_id", T_TEXT, ""),
        ("manifest_id", T_TEXT, ""),
        ("placement_run_id", T_TEXT, ""),
        ("project_id", T_TEXT, ""),
        ("object_family", T_TEXT, ""),
        ("design_zone", T_TEXT, ""),
        ("source_sheet", T_TEXT, ""),
        ("created_by", T_TEXT, "marpa_symbol_factory"),
    ],
    "VwPset_MARPA_Plant": [
        ("marpa_object_id", T_TEXT, ""),
        ("common_name", T_TEXT, ""),
        ("latin_name", T_TEXT, ""),
        ("species_code", T_TEXT, ""),
        ("scheduled_size", T_TEXT, ""),
        ("water_range", T_TEXT, ""),
        ("bloom_season", T_TEXT, ""),
        ("bloom_color", T_TEXT, ""),
    ],
    "VwPset_MARPA_Cost": [
        ("marpa_object_id", T_TEXT, ""),
        ("cost_item_key", T_TEXT, ""),
        ("unit_cost_usd", T_DEC, "0"),
        ("quantity", T_DEC, "1"),
        ("cost_basis", T_TEXT, ""),
    ],
    "VwPset_MARPA_Maintenance": [
        ("marpa_object_id", T_TEXT, ""),
        ("task_key", T_TEXT, ""),
        ("frequency_str", T_TEXT, ""),
        ("season_window", T_TEXT, ""),
    ],
    "VwPset_MARPA_Source": [
        ("marpa_object_id", T_TEXT, ""),
        ("source_kind", T_TEXT, ""),
        ("source_path", T_TEXT, ""),
        ("source_claim_ids", T_TEXT, ""),
        ("ingest_run_id", T_TEXT, ""),
    ],
    "VwPset_MARPA_ExportQA": [
        ("marpa_object_id", T_TEXT, ""),
        ("export_required", T_BOOL, "0"),
        ("has_3d_geometry", T_BOOL, "0"),
        ("export_entity_target", T_TEXT, ""),
        ("qa_status", T_TEXT, ""),
        ("qa_notes", T_TEXT, ""),
    ],
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_record(record_name: str, fields: list[tuple[str, int, str]]) -> dict[str, object]:
    existing = set()
    handle = vs.GetObject(record_name)
    if handle is not None:
        try:
            count = int(vs.NumFields(handle) or 0)
        except Exception:
            count = 0
        for index in range(1, count + 1):
            try:
                field_name = vs.GetFldName(handle, index) or ""
            except Exception:
                field_name = ""
            if field_name:
                existing.add(field_name)

    created = []
    errors = []
    for field_name, field_type, default in fields:
        if field_name in existing:
            continue
        if len(field_name) > 20:
            errors.append(f"field name > 20 chars: {field_name}")
            continue
        try:
            vs.NewField(record_name, field_name, default, field_type, F_FLAG)
            created.append(field_name)
        except Exception as exc:
            errors.append(f"NewField failed for {field_name}: {exc}")

    handle = vs.GetObject(record_name)
    custom_ok = False
    custom_error = ""
    if handle is not None:
        try:
            custom_ok = bool(vs.IFC_CustPsetFromRec(handle))
        except Exception as exc:
            custom_error = str(exc)
    else:
        custom_error = "record missing after ensure"

    return {
        "record_name": record_name,
        "created_fields": created,
        "preexisting_fields": sorted(existing),
        "ifc_cust_pset_from_rec_ok": custom_ok,
        "ifc_cust_pset_from_rec_error": custom_error,
        "ok": not errors and custom_ok,
        "errors": errors,
    }


def main() -> None:
    rows = [ensure_record(record_name, fields) for record_name, fields in PSET_REGISTRY.items()]
    payload = {
        "ran_at": now_iso(),
        "doc_name": vs.GetFName(),
        "record_count": len(rows),
        "rows": rows,
    }
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


if __name__ == "__main__":
    main()
