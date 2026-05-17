import json
import os
import sys
from datetime import datetime, timezone

import vs  # type: ignore


CONFIG = {
    "out_dir": "/tmp/farber_haines_ifc_probe",
    "require_georef_gate": True,
    "expected_epsg_code": 2231,
    "selected_reference_path": (
        "/Volumes/PixelTable/VW_iTWIN_Bridge/VW_iTwin_Bridge/"
        "projects/farber-haines-2521/artifacts/georef/"
        "farber_haines_selected_reference_points.json"
    ),
    "binding_artifact_path": (
        "/Volumes/PixelTable/VW_iTWIN_Bridge/VW_iTwin_Bridge/"
        "projects/farber-haines-2521/artifacts/georef/"
        "document_georef_binding.vectorworks_hardwired.json"
    ),
    "cycle_report_path": (
        "/Volumes/PixelTable/VW_iTWIN_Bridge/VW_iTwin_Bridge/"
        "projects/farber-haines-2521/artifacts/georef/"
        "farber_haines_georef_cycle_report.json"
    ),
    "fit_report_path": "/tmp/farber_haines_georef_fit.json",
}

PRESET = globals().get("PRESET")
if isinstance(PRESET, dict):
    CONFIG.update(PRESET)

OUT_DIR = str(CONFIG["out_dir"])
OUT_JSON = OUT_DIR + "/export_result.json"
REPO_ROOT = "/Volumes/PixelTable/VW_iTWIN_Bridge/VW_iTwin_Bridge"
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

GATE_PATH = os.path.join(
    REPO_ROOT,
    "georef/converters/farber_haines_georef_preexport_gate.py",
)
GATE_SCOPE = {"__name__": "farber_haines_georef_preexport_gate_live"}
with open(GATE_PATH, "r", encoding="utf-8") as gate_handle:
    exec(compile(gate_handle.read(), GATE_PATH, "exec"), GATE_SCOPE, GATE_SCOPE)
evaluate_gate = GATE_SCOPE["evaluate_gate"]
parse_epsg_from_projection_text = GATE_SCOPE["parse_epsg_from_projection_text"]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: str) -> dict:
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            if isinstance(data, dict):
                return data
    except Exception:
        return {}
    return {}


def safe_call(fn, *args, default=None):
    try:
        return fn(*args)
    except Exception:
        return default


def get_projection_epsg() -> int | None:
    for layer in (None, safe_call(vs.ActLayer, default=None)):
        for esri_style in (False, True):
            result = safe_call(vs.GetProjectionWKT, layer, esri_style, default=None)
            if result and result[0]:
                epsg = parse_epsg_from_projection_text(str(result[1] or ""))
                if epsg is not None:
                    return epsg
            result = safe_call(vs.GetProjectionProj4, layer, esri_style, default=None)
            if result and result[0]:
                epsg = parse_epsg_from_projection_text(str(result[1] or ""))
                if epsg is not None:
                    return epsg
    return None


def get_doc_snapshot() -> dict:
    gis = safe_call(vs.GetGISOriginN, default=None)
    if not (gis and gis[0]):
        gis = safe_call(vs.GetGISOrigin, default=None)
    origin = safe_call(vs.GetOriginInDocUnits, default=None)
    if origin is None:
        origin = safe_call(vs.GetOrigin, default=None)
    return {
        "document_is_georeferenced": bool(safe_call(vs.IsGeoreferenced, None, default=False)),
        "epsg_code": get_projection_epsg(),
        "gis_origin": {
            "lat": float(gis[1]) if gis and gis[0] else None,
            "lon": float(gis[2]) if gis and gis[0] else None,
            "angle_to_north": float(gis[3]) if gis and gis[0] else None,
        },
        "user_origin": {
            "x": float(origin[0]) if origin else None,
            "y": float(origin[1]) if origin else None,
        },
    }


def run_georef_gate() -> dict:
    return evaluate_gate(
        {
            "project_id": "farber-haines-2521",
            "expected_epsg_code": int(CONFIG["expected_epsg_code"]),
            "doc_snapshot": get_doc_snapshot(),
            "selected_payload": load_json(str(CONFIG["selected_reference_path"])),
            "cycle_report": load_json(str(CONFIG["cycle_report_path"])),
            "binding_artifact": load_json(str(CONFIG["binding_artifact_path"])),
            "fit_report": load_json(str(CONFIG["fit_report_path"])),
        }
    )


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    ifc_path = OUT_DIR + "/farber_haines_probe_" + stamp + ".ifc"
    out = {
        "started_at": now_iso(),
        "doc_name": "",
        "doc_path": "",
        "ifc_path": ifc_path,
        "ok": False,
        "export_return": None,
        "georef_gate": None,
        "error": "",
    }
    try:
        out["doc_name"] = vs.GetFName() or ""
    except Exception:
        pass
    try:
        out["doc_path"] = vs.GetFPathName() or ""
    except Exception:
        pass
    try:
        if CONFIG.get("require_georef_gate", True):
            gate = run_georef_gate()
            out["georef_gate"] = gate
            if not gate.get("ok"):
                out["error"] = "blocked_by_georef_gate: " + ";".join(gate.get("block_reasons") or [])
                out["finished_at"] = now_iso()
                with open(OUT_JSON, "w", encoding="utf-8") as fh:
                    json.dump(out, fh, indent=2)
                return
        try:
            vs.DSelectAll()
        except Exception:
            pass
        rc = vs.IFC_ExportNoUI(ifc_path)
        out["export_return"] = bool(rc)
        out["ok"] = bool(rc) and os.path.exists(ifc_path)
        if not os.path.exists(ifc_path):
            out["error"] = "IFC_ExportNoUI returned but output file was not found"
    except Exception as exc:
        out["error"] = str(exc)
    out["finished_at"] = now_iso()
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)


if __name__ == "__main__":
    main()
