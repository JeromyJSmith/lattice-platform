#!/usr/bin/env python3
"""Fail-closed georef policy for Farber-Haines IFC exports.

This module is pure Python so tests can exercise the policy without a live
Vectorworks process. Vectorworks scripts pass live `vs.*` snapshots into
`evaluate_gate()` immediately before `IFC_ExportNoUI`.
"""

from __future__ import annotations

import re
from typing import Any


PROJECT_ID = "farber-haines-2521"
DEFAULT_MAX_RMSE = 5.0
DEFAULT_MAX_RESIDUAL = 15.0


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on", "pass", "passed"}
    return False


def _as_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_int(value: Any) -> int | None:
    try:
        if value is None or value == "":
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _selected_payload_is_live(payload: dict[str, Any]) -> bool:
    if payload.get("export_kind") != "vectorworks_selected_reference_points":
        return False
    if payload.get("project_id") != PROJECT_ID:
        return False
    version = str(payload.get("export_version") or "").lower()
    signature = str(payload.get("object_signature_sha256") or "").lower()
    source = str(payload.get("source_vwx") or "").lower()
    if "recreated" in version or "recreated" in signature or "mock" in source:
        return False
    if _as_int(payload.get("selected_count")) != len(payload.get("objects") or []):
        return False
    if not payload.get("objects"):
        return False
    for obj in payload.get("objects") or []:
        uuid = str(obj.get("object_uuid") or "").strip().lower()
        if not uuid or uuid.startswith("recreated-"):
            return False
    return True


def _binding_is_approved(cycle_report: dict[str, Any], binding_artifact: dict[str, Any]) -> bool:
    if _as_bool(cycle_report.get("apply_performed")):
        return True
    status = str(binding_artifact.get("binding_status") or "").strip().lower()
    if status in {"resolved", "runtime_apply", "applied"} and _as_bool(binding_artifact.get("allow_apply")):
        return True
    return False


def evaluate_gate(
    inputs: dict[str, Any],
    *,
    max_rmse: float = DEFAULT_MAX_RMSE,
    max_residual: float = DEFAULT_MAX_RESIDUAL,
) -> dict[str, Any]:
    """Return an export decision for the active Farber-Haines VW document."""

    block_reasons: list[str] = []
    warnings: list[str] = []

    doc = inputs.get("doc_snapshot") or {}
    selected = inputs.get("selected_payload") or {}
    cycle_report = inputs.get("cycle_report") or {}
    binding_artifact = inputs.get("binding_artifact") or {}
    fit_report = inputs.get("fit_report") or {}
    expected_epsg = _as_int(inputs.get("expected_epsg_code"))
    project_id = str(inputs.get("project_id") or "")

    if project_id != PROJECT_ID:
        block_reasons.append(f"project_id_mismatch:{project_id or 'missing'}")

    if not _as_bool(doc.get("document_is_georeferenced")):
        block_reasons.append("document_not_georeferenced")

    doc_epsg = _as_int(doc.get("epsg_code"))
    if expected_epsg is not None:
        if doc_epsg is not None and doc_epsg != expected_epsg:
            block_reasons.append(f"document_epsg_mismatch:expected={expected_epsg},actual={doc_epsg}")
        binding_epsg = _as_int(binding_artifact.get("epsg_code"))
        if binding_epsg is not None and binding_epsg != expected_epsg:
            block_reasons.append(f"binding_epsg_mismatch:expected={expected_epsg},actual={binding_epsg}")
        if doc_epsg is None:
            warnings.append("document_epsg_unreadable_from_vectorworks_sdk")

    origin = doc.get("gis_origin") or {}
    if origin:
        if _as_float(origin.get("x")) is None and _as_float(origin.get("lat")) is None:
            block_reasons.append("gis_origin_unreadable")
    else:
        block_reasons.append("gis_origin_missing")

    if not _selected_payload_is_live(selected):
        block_reasons.append("selected_reference_export_not_live_vectorworks_payload")

    if not _binding_is_approved(cycle_report, binding_artifact):
        block_reasons.append("binding_not_approved_for_export")

    rmse = _as_float(fit_report.get("fit_rmse_project_units"))
    max_err = _as_float(fit_report.get("fit_max_residual_project_units"))
    if rmse is not None and rmse > max_rmse:
        block_reasons.append(f"fit_rmse_too_high:{rmse}>{max_rmse}")
    if max_err is not None and max_err > max_residual:
        block_reasons.append(f"fit_max_residual_too_high:{max_err}>{max_residual}")

    return {
        "ok": not block_reasons,
        "project_id": PROJECT_ID,
        "block_reasons": block_reasons,
        "warnings": warnings,
        "thresholds": {
            "max_rmse": max_rmse,
            "max_residual": max_residual,
        },
        "expected_epsg_code": expected_epsg,
        "observed": {
            "document_is_georeferenced": _as_bool(doc.get("document_is_georeferenced")),
            "document_epsg_code": doc_epsg,
            "binding_status": binding_artifact.get("binding_status"),
            "binding_allow_apply": _as_bool(binding_artifact.get("allow_apply")),
            "selected_count": selected.get("selected_count"),
            "fit_rmse_project_units": rmse,
            "fit_max_residual_project_units": max_err,
        },
    }


def parse_epsg_from_projection_text(text: str) -> int | None:
    """Extract an EPSG authority code from WKT/Proj text when Vectorworks exposes it."""

    matches = re.findall(r"EPSG[\"',:\s]+(\d{4,6})", text or "", re.IGNORECASE)
    if not matches:
        return None
    # In WKT1 the top-level projected CRS AUTHORITY appears after nested
    # authorities for spheroid/datum/unit. The final EPSG code is the CRS.
    return _as_int(matches[-1])
