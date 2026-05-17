"""Portable IFC Data Manager sync for the Farber-Haines workflow.

Run inside Vectorworks 2026.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from typing import Any

import vs  # type: ignore


DEFAULT_SPEC = "/tmp/farber_haines_data_manager_mapping_spec.json"
DEFAULT_OUT = "/tmp/farber_haines_data_manager_sync_last_run.json"
RECORD_PSET_PREFIXES = ("MARPA_", "VwPset_MARPA_")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def call(name: str, *args: Any) -> tuple[bool, Any]:
    fn = getattr(vs, name, None)
    if fn is None:
        return False, f"vs.{name} unavailable"
    try:
        return True, fn(*args)
    except Exception as exc:
        return False, f"{name}{args}: {exc}"


def ok_bool(name: str, *args: Any) -> tuple[bool, str | None]:
    ok, value = call(name, *args)
    if not ok:
        return False, str(value)
    if bool(value):
        return True, None
    return False, f"{name}{args} returned FALSE"


def ok_out(name: str, *args: Any) -> tuple[bool, Any, str | None]:
    ok, value = call(name, *args)
    if not ok:
        return False, None, str(value)
    if isinstance(value, tuple) and len(value) >= 2:
        return bool(value[0]), value[1], None
    return False, None, f"{name} returned unexpected shape: {value!r}"


def snapshot_mapping() -> dict[str, Any]:
    out: dict[str, Any] = {"objects": [], "errors": []}
    ok, count, err = ok_out("IFC_DMGetObjectsCnt")
    if not ok:
        out["errors"].append(err)
        return out

    for object_index in range(1, int(count) + 1):
        ok, object_name, err = ok_out("IFC_DMGetObjNameAt", object_index)
        if not ok:
            out["errors"].append(err)
            continue

        row: dict[str, Any] = {
            "object_name": object_name,
            "object_condition": None,
            "entries": [],
        }
        ok, object_condition, _ = ok_out("IFC_DMGetObjCond", object_name)
        if ok:
            row["object_condition"] = object_condition

        ok, entry_count, err = ok_out("IFC_DMGetEntriesCnt", object_name)
        if not ok:
            out["errors"].append(err)
            out["objects"].append(row)
            continue

        for entry_index in range(1, int(entry_count) + 1):
            ok, entry_name, err = ok_out("IFC_DMGetEntryName", entry_index, object_name)
            if not ok:
                out["errors"].append(err)
                continue
            entry: dict[str, Any] = {
                "entry_name": entry_name,
                "entry_type": None,
                "enabled": bool(call("IFC_DMIsEntryEnabled", object_name, entry_name)[1]),
                "psets": [],
            }
            ok, entry_type, _ = ok_out("IFC_DMGetEntryType", object_name, entry_index)
            if ok:
                entry["entry_type"] = entry_type
            ok, pset_count, _ = ok_out("IFC_DMGetEntPSetsCnt", object_name, entry_name)
            if ok:
                for pset_index in range(1, int(pset_count) + 1):
                    ok, pset_name, _ = ok_out("IFC_DMGetPSetName", object_name, entry_name, pset_index)
                    if not ok:
                        continue
                    entry["psets"].append(pset_name)
            row["entries"].append(entry)
        out["objects"].append(row)

    return out


def is_record_backed_pset(pset_name: str) -> bool:
    return pset_name.startswith(RECORD_PSET_PREFIXES)


def apply_spec(spec: dict[str, Any], dry_run: bool) -> dict[str, Any]:
    changes: list[dict[str, Any]] = []
    errors: list[str] = []

    for record_name in spec.get("custom_psets_from_records", []):
        if dry_run:
            changes.append({"op": "IFC_CustPsetFromRec", "record": record_name, "dry_run": True})
            continue
        handle = vs.GetObject(record_name)
        if handle is None:
            changes.append({"op": "IFC_CustPsetFromRec", "record": record_name, "ok": False, "error": "record not found"})
            continue
        ok, err = ok_bool("IFC_CustPsetFromRec", handle)
        changes.append({"op": "IFC_CustPsetFromRec", "record": record_name, "ok": ok, "error": err})

    for object_spec in spec.get("objects", []):
        object_name = object_spec["object_name"]
        if object_spec.get("enabled") is not None:
            if dry_run:
                changes.append({"op": "IFC_DMEnableObject", "object": object_name, "enable": bool(object_spec["enabled"]), "dry_run": True})
            else:
                ok, err = ok_bool("IFC_DMEnableObject", object_name, bool(object_spec["enabled"]))
                changes.append({"op": "IFC_DMEnableObject", "object": object_name, "ok": ok, "error": err})

        if object_spec.get("object_condition") is not None:
            if dry_run:
                changes.append({"op": "IFC_DMSetObjectCond", "object": object_name, "condition": object_spec["object_condition"], "dry_run": True})
            else:
                ok, err = ok_bool("IFC_DMSetObjectCond", object_name, object_spec["object_condition"])
                changes.append({"op": "IFC_DMSetObjectCond", "object": object_name, "ok": ok, "error": err})

        for entry_spec in object_spec.get("entries", []):
            entry_name = entry_spec["entry_name"]
            if dry_run:
                changes.append({"op": "IFC_DMAddEntry", "object": object_name, "entry": entry_name, "dry_run": True})
            else:
                ok, err = ok_bool("IFC_DMAddEntry", object_name, entry_name, bool(entry_spec.get("enabled", True)))
                changes.append({"op": "IFC_DMAddEntry", "object": object_name, "entry": entry_name, "ok": ok, "error": err})

            if entry_spec.get("enabled") is not None:
                if dry_run:
                    changes.append({"op": "IFC_DMEnableEntry", "object": object_name, "entry": entry_name, "enable": bool(entry_spec["enabled"]), "dry_run": True})
                else:
                    ok, err = ok_bool("IFC_DMEnableEntry", object_name, entry_name, bool(entry_spec["enabled"]))
                    changes.append({"op": "IFC_DMEnableEntry", "object": object_name, "entry": entry_name, "ok": ok, "error": err})

            for pset_spec in entry_spec.get("psets", []):
                pset_name = pset_spec["pset_name"]
                pset_condition = pset_spec.get("condition", "")
                if dry_run:
                    changes.append({"op": "IFC_DMAddPSetForEnt", "object": object_name, "entry": entry_name, "pset": pset_name, "condition": pset_condition, "dry_run": True})
                else:
                    ok, err = ok_bool("IFC_DMAddPSetForEnt", object_name, entry_name, pset_name, bool(pset_spec.get("enabled", True)), pset_condition)
                    changes.append({"op": "IFC_DMAddPSetForEnt", "object": object_name, "entry": entry_name, "pset": pset_name, "ok": ok, "error": err})

                if pset_spec.get("enabled") is not None:
                    if dry_run:
                        changes.append({"op": "IFC_DMEnablePSet", "object": object_name, "entry": entry_name, "pset": pset_name, "enable": bool(pset_spec["enabled"]), "dry_run": True})
                    else:
                        ok, err = ok_bool("IFC_DMEnablePSet", object_name, entry_name, pset_name, bool(pset_spec["enabled"]))
                        changes.append({"op": "IFC_DMEnablePSet", "object": object_name, "entry": entry_name, "pset": pset_name, "ok": ok, "error": err})

                if is_record_backed_pset(pset_name):
                    enabled = bool(pset_spec.get("enabled", True))
                    if dry_run:
                        changes.append({"op": "IFC_AddRecToObjMap", "object": object_name, "record": pset_name, "condition": pset_condition, "enable": enabled, "dry_run": True})
                        changes.append({"op": "IFC_SetRecEnabled", "object": object_name, "record": pset_name, "enable": enabled, "dry_run": True})
                    else:
                        ok, err = ok_bool("IFC_AddRecToObjMap", object_name, pset_name, pset_condition, enabled)
                        changes.append({"op": "IFC_AddRecToObjMap", "object": object_name, "record": pset_name, "ok": ok, "error": err})
                        ok, err = ok_bool("IFC_SetRecEnabled", object_name, pset_name, enabled)
                        changes.append({"op": "IFC_SetRecEnabled", "object": object_name, "record": pset_name, "ok": ok, "error": err})

                for field_spec in pset_spec.get("fields", []):
                    field_name = field_spec["field_name"]
                    if field_spec.get("mapping_src"):
                        if dry_run:
                            changes.append({"op": "IFC_DMSetPSetFldMap", "object": object_name, "entry": entry_name, "pset": pset_name, "field": field_name, "mapping_src": field_spec["mapping_src"], "dry_run": True})
                        else:
                            ok, err = ok_bool("IFC_DMSetPSetFldMap", object_name, entry_name, pset_name, field_name, field_spec["mapping_src"])
                            changes.append({"op": "IFC_DMSetPSetFldMap", "object": object_name, "entry": entry_name, "pset": pset_name, "field": field_name, "ok": ok, "error": err})

    settings_name = spec.get("save_settings_name")
    if settings_name:
        if dry_run:
            changes.append({"op": "IFC_DMSaveSettings", "name": settings_name, "dry_run": True})
        else:
            ok, err = ok_bool("IFC_DMSaveSettings", settings_name, "", True)
            changes.append({"op": "IFC_DMSaveSettings", "name": settings_name, "ok": ok, "error": err})

    for change in changes:
        if change.get("ok") is False and change.get("error"):
            errors.append(str(change["error"]))

    return {"changes": changes, "errors": errors}


def load_json(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["audit", "apply"], default="audit")
    parser.add_argument("--spec", default=DEFAULT_SPEC)
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    payload: dict[str, Any] = {
        "ran_at": now_iso(),
        "doc_name": vs.GetFName(),
        "mode": args.mode,
        "spec": args.spec,
        "dry_run": bool(args.dry_run),
    }
    if args.mode == "audit":
        payload["snapshot"] = snapshot_mapping()
    else:
        spec = load_json(args.spec)
        payload["apply_result"] = apply_spec(spec, dry_run=bool(args.dry_run))
        payload["snapshot_after"] = snapshot_mapping()

    out_dir = os.path.dirname(args.out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, default=str)


if __name__ == "__main__":
    main()
