"""Build a starter Data Manager spec for Farber-Haines IFC export work."""

from __future__ import annotations

import json
import os


OUT_PATHS = [
    os.path.expanduser("~/Desktop/farber_haines_data_manager_mapping_spec.json"),
    "/tmp/farber_haines_data_manager_mapping_spec.json",
]

CUSTOM_PSETS = [
    "VwPset_MARPA_Object",
    "VwPset_MARPA_Plant",
    "VwPset_MARPA_Cost",
    "VwPset_MARPA_Source",
    "VwPset_MARPA_ExportQA",
]


def object_entry(object_name: str) -> dict[str, object]:
    return {
        "object_name": object_name,
        "enabled": True,
        "entries": [
            {
                "entry_name": "IfcGeographicElement",
                "enabled": True,
                "psets": (
                    [{"pset_name": "Pset_VegetationCommon", "enabled": True, "condition": ""}]
                    + [{"pset_name": pset_name, "enabled": True, "condition": ""} for pset_name in CUSTOM_PSETS]
                ),
            }
        ],
    }


def main() -> None:
    payload = {
        "save_settings_name": "FarberHaines_IFC4x3_EstimationExport",
        "custom_psets_from_records": CUSTOM_PSETS,
        "objects": [
            object_entry("Plant"),
            object_entry("Existing Tree"),
        ],
        "manual_followup": [
            {
                "family": "boulder",
                "class_name": "L-Boulder",
                "required_action": "Create a criteria-based object mapping in Data Manager, then attach IfcGeographicElement and record-backed MARPA Psets.",
                "reason": "Direct IFC setters return false on sampled boulder objects, and the current sync API edits mappings but does not create new criteria-based object rows from scratch.",
            },
            {
                "family": "curb_edging",
                "class_name": "L-Edge-Roll Top Metal",
                "required_action": "Create a criteria-based object mapping in Data Manager, then attach IfcKerb and record-backed MARPA Psets.",
                "reason": "Direct IFC setters return false on sampled edging objects, and the current sync API edits mappings but does not create new criteria-based object rows from scratch.",
            },
        ],
        "evidence": {
            "ifc_diagnostic": "/Users/ojeromyo/Desktop/fh_ifc_diag.json",
            "ifc_update_report": "/Users/ojeromyo/Desktop/farber_haines_ifc_entity_update_report.csv",
            "ifc_actionable_families": "/Users/ojeromyo/Desktop/farber_haines_ifc_actionable_families.csv",
        },
    }
    for path in OUT_PATHS:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
        print(path)


if __name__ == "__main__":
    main()
