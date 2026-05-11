"""In-process upsert helpers.

These are the *only* place that writes to Pixeltable. Routes, fixture loaders,
and tests all funnel through these. Logical upsert is implemented as
"delete-where(key) + insert" because pixeltable 0.6.0 has no native upsert.
"""

from __future__ import annotations

import datetime as dt
from typing import Any, Iterable

from service.ids import uuidv7

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def _coalesce(d: dict, *keys: str, default: Any = None) -> Any:
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return default


def _delete_by(table, where_expr) -> int:
    fn = getattr(table, "delete", None)
    if fn is None:
        return 0
    try:
        fn(where=where_expr)
    except TypeError:
        try:
            fn(where_expr)
        except Exception:
            return 0
    return 1


def _insert(table, rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0
    table.insert(rows)
    return len(rows)


# ---------------------------------------------------------------------------
# Runtime ledger (lattice/execution/*)
# ---------------------------------------------------------------------------


def _exec(pxt, name: str):
    return pxt.get_table(f"lattice/execution/{name}")


def upsert_runtime_event(pxt, event: dict[str, Any]) -> dict[str, Any]:
    """Route a single TS RuntimeEvent into the right execution table.

    Insert units (per contracts/runtime-ledger.v1.yaml):
      thread.created  -> agent_threads
      message.added   -> agent_messages
      run.started     -> agent_runs (creates row)
      run.completed   -> agent_runs (updates row by run_id)
      stream.delta    -> agent_stream_events
      tool.started    -> agent_stream_events
      tool.completed  -> agent_stream_events
      artifact.added  -> agent_artifacts
      run.terminal    -> agent_outcomes
    """
    kind = event.get("kind") or event.get("event_kind") or event.get("type")
    payload = event.get("payload", event)

    if kind == "thread.created":
        t = _exec(pxt, "agent_threads")
        thread_id = payload["thread_id"]
        _delete_by(t, t.thread_id == thread_id)
        _insert(t, [{
            "id":              uuidv7(),
            "thread_id":       thread_id,
            "title":           payload.get("title", ""),
            "operator_handle": payload.get("operator_handle", ""),
            "created_at":      payload.get("created_at") or _now(),
            "raw_event":       event,
        }])
        return {"table": "agent_threads", "thread_id": thread_id}

    if kind == "message.added":
        t = _exec(pxt, "agent_messages")
        message_id = payload["message_id"]
        _delete_by(t, t.message_id == message_id)
        _insert(t, [{
            "id":         uuidv7(),
            "thread_id":  payload.get("thread_id", ""),
            "message_id": message_id,
            "role":       payload.get("role", ""),
            "content_md": payload.get("content_md", payload.get("content", "")),
            "tokens_in":  int(_coalesce(payload, "tokens_in", "input_tokens", default=0)),
            "tokens_out": int(_coalesce(payload, "tokens_out", "output_tokens", default=0)),
            "model_id":   payload.get("model_id", ""),
            "provider":   payload.get("provider", ""),
            "created_at": payload.get("created_at") or _now(),
            "raw_event":  event,
        }])
        return {"table": "agent_messages", "message_id": message_id}

    if kind in ("run.started", "run.completed"):
        t = _exec(pxt, "agent_runs")
        run_id = payload["run_id"]
        _delete_by(t, t.run_id == run_id)
        row = {
            "id":               uuidv7(),
            "run_id":           run_id,
            "thread_id":        payload.get("thread_id", ""),
            "agent_kind":       payload.get("agent_kind", ""),
            "model_id":         payload.get("model_id", ""),
            "started_at":       payload.get("started_at") or _now(),
            "ended_at":         payload.get("ended_at"),
            "status":           payload.get("status") or ("started" if kind == "run.started" else "completed"),
            "exit_code":        int(_coalesce(payload, "exit_code", default=0) or 0),
            "duration_ms":      int(_coalesce(payload, "duration_ms", default=0) or 0),
            "tokens_in_total":  int(_coalesce(payload, "tokens_in_total", default=0) or 0),
            "tokens_out_total": int(_coalesce(payload, "tokens_out_total", default=0) or 0),
            "raw_event":        event,
        }
        _insert(t, [row])
        return {"table": "agent_runs", "run_id": run_id, "status": row["status"]}

    if kind in ("stream.delta", "tool.started", "tool.completed"):
        t = _exec(pxt, "agent_stream_events")
        event_id = payload.get("event_id") or uuidv7()
        _delete_by(t, t.event_id == event_id)
        _insert(t, [{
            "id":         uuidv7(),
            "run_id":     payload.get("run_id", ""),
            "event_id":   event_id,
            "event_kind": kind,
            "seq":        int(payload.get("seq", 0)),
            "delta_text": payload.get("delta_text", ""),
            "tool_name":  payload.get("tool_name", ""),
            "tool_input": payload.get("tool_input"),
            "tool_output": payload.get("tool_output"),
            "created_at": payload.get("created_at") or _now(),
            "raw_event":  event,
        }])
        return {"table": "agent_stream_events", "event_id": event_id}

    if kind == "artifact.added":
        t = _exec(pxt, "agent_artifacts")
        artifact_path = payload["artifact_path"]
        run_id = payload.get("run_id", "")
        _delete_by(t, (t.run_id == run_id) & (t.artifact_path == artifact_path))
        _insert(t, [{
            "id":            uuidv7(),
            "run_id":        run_id,
            "artifact_path": artifact_path,
            "artifact_kind": payload.get("artifact_kind", ""),
            "byte_size":     int(payload.get("byte_size", 0)),
            "sha256":        payload.get("sha256", ""),
            "created_at":    payload.get("created_at") or _now(),
            "raw_event":     event,
        }])
        return {"table": "agent_artifacts", "artifact_path": artifact_path}

    if kind in ("run.terminal", "run.failed"):
        t = _exec(pxt, "agent_outcomes")
        run_id = payload["run_id"]
        _delete_by(t, t.run_id == run_id)
        _insert(t, [{
            "id":                       uuidv7(),
            "run_id":                   run_id,
            "thread_id":                payload.get("thread_id", ""),
            "terminal_status":          payload.get("status") or ("failed" if kind == "run.failed" else "completed"),
            "outcome_md":               payload.get("outcome_md", ""),
            "evidence_manifest_yaml":   payload.get("evidence_manifest_yaml", ""),
            "evidence_manifest_parsed": payload.get("evidence_manifest_parsed"),
            "closed_at":                payload.get("closed_at") or _now(),
            "raw_event":                event,
        }])
        return {"table": "agent_outcomes", "run_id": run_id}

    return {"table": None, "skipped": True, "reason": f"unknown kind {kind!r}"}


def upsert_runtime_events(pxt, events: Iterable[dict[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    skipped = 0
    for evt in events:
        out = upsert_runtime_event(pxt, evt)
        if out.get("skipped"):
            skipped += 1
            continue
        tbl = out["table"]
        counts[tbl] = counts.get(tbl, 0) + 1
    return {"counts": counts, "skipped": skipped}


# ---------------------------------------------------------------------------
# VW + IFC + semantic (lattice/bridge/{vw,ifc,semantic})
# ---------------------------------------------------------------------------


def upsert_vw_sidecar(pxt, payload: dict[str, Any]) -> dict[str, Any]:
    """Atomic write of a VWX export sidecar.

    Writes to:
      lattice/bridge/vw/vectorworks_exports
      lattice/bridge/ifc/ifc_elements
      lattice/bridge/ifc/ifc_property_sets
      lattice/bridge/semantic/semantic_sidecars
      lattice/bridge/evidence/harness_run_refs
    """
    vw_export_hash = payload["vw_export_hash"]
    vw_meta = payload.get("vectorworks", {})
    ifc_meta = payload.get("ifc", {})
    elements = payload.get("elements", []) or []
    harness_run_id = payload.get("harness_run_id", "")
    operator_handle = payload.get("operator_handle", "")
    ingested_at = _now()

    counts: dict[str, int] = {}

    # 1. vectorworks_exports (one row per export)
    vw_t = pxt.get_table("lattice/bridge/vw/vectorworks_exports")
    _delete_by(vw_t, vw_t.vw_export_hash == vw_export_hash)
    _insert(vw_t, [{
        "id":               uuidv7(),
        "vw_export_hash":   vw_export_hash,
        "vw_export_id":     payload.get("vw_export_id", ""),
        "schema_version":   payload.get("schema_version", "vwx-sidecar.v1"),
        "vw_version":       vw_meta.get("version", ""),
        "drawing_name":     vw_meta.get("drawing_name", ""),
        "sheet_layer":      vw_meta.get("sheet_layer", ""),
        "ifc_filename":     ifc_meta.get("filename", ""),
        "ifc_byte_size":    int(ifc_meta.get("byte_size", 0)),
        "ifc_schema":       ifc_meta.get("schema", ""),
        "lane_ar_path":     payload.get("lane_ar_path", ""),
        "vwx_filename":     vw_meta.get("vwx_filename", ""),
        "vwx_byte_size":    int(vw_meta.get("vwx_byte_size", 0)),
        "exported_at":      payload.get("exported_at") or ingested_at,
        "ingested_at":      ingested_at,
        "ingested_by":      operator_handle,
        "harness_run_id":   harness_run_id,
        "raw_sidecar":      payload,
        "exporter_warnings": payload.get("exporter_warnings", []),
    }])
    counts["vectorworks_exports"] = 1

    # 2. ifc_elements + ifc_property_sets + semantic_sidecars (per element)
    ifc_el_t   = pxt.get_table("lattice/bridge/ifc/ifc_elements")
    ifc_pset_t = pxt.get_table("lattice/bridge/ifc/ifc_property_sets")
    sem_t      = pxt.get_table("lattice/bridge/semantic/semantic_sidecars")

    _delete_by(ifc_el_t,   ifc_el_t.vw_export_hash   == vw_export_hash)
    _delete_by(ifc_pset_t, ifc_pset_t.vw_export_hash == vw_export_hash)
    _delete_by(sem_t,      sem_t.vw_export_hash      == vw_export_hash)

    el_rows: list[dict[str, Any]] = []
    pset_rows: list[dict[str, Any]] = []
    sem_rows: list[dict[str, Any]] = []

    for elt in elements:
        sid = elt["source_element_id"]
        ifc_class = elt.get("ifc_class", "")
        is_marpa_seed = bool(elt.get("marpa_seed", False))

        el_rows.append({
            "id":                 uuidv7(),
            "vw_export_hash":     vw_export_hash,
            "source_element_id":  sid,
            "ifc_class":          ifc_class,
            "ifc_predefined_type": elt.get("ifc_predefined_type", ""),
            "name":               elt.get("name", ""),
            "long_name":          elt.get("long_name", ""),
            "object_type":        elt.get("object_type", ""),
            "tag":                elt.get("tag", ""),
            "description":        elt.get("description", ""),
            "spatial_container_guid":  elt.get("spatial_container_guid", ""),
            "spatial_container_class": elt.get("spatial_container_class", ""),
            "bbox_min":           elt.get("bbox_min"),
            "bbox_max":           elt.get("bbox_max"),
            "centroid":           elt.get("centroid"),
            "elevation_m":        float(elt.get("elevation_m") or 0.0),
            "is_marpa_seed":      is_marpa_seed,
            "parsed_at":          ingested_at,
            "ifc_schema":         ifc_meta.get("schema", ""),
            "raw_attributes":     elt.get("raw_attributes", {}),
        })

        for pset in elt.get("property_sets", []) or []:
            pset_rows.append({
                "id":                uuidv7(),
                "vw_export_hash":    vw_export_hash,
                "source_element_id": sid,
                "pset_name":         pset.get("pset_name", ""),
                "is_marpa_seed":     bool(pset.get("is_marpa_seed", is_marpa_seed)),
                "record_kind":       pset.get("record_kind", "other"),
                "selected_keys":     pset.get("selected_keys", []),
                "properties":        pset.get("properties", {}),
                "parsed_at":         ingested_at,
            })

        sidecar_slice = elt.get("semantic", {})
        if sidecar_slice or is_marpa_seed:
            text_blob = sidecar_slice.get("text_blob") or " ".join(
                str(v) for v in (
                    sidecar_slice.get("common_name", ""),
                    sidecar_slice.get("botanical_name", ""),
                    sidecar_slice.get("container_size", ""),
                    sidecar_slice.get("phenology_notes", ""),
                ) if v
            ).strip()
            sem_rows.append({
                "id":                uuidv7(),
                "vw_export_hash":    vw_export_hash,
                "source_element_id": sid,
                "ifc_class":         ifc_class,
                "common_name":       sidecar_slice.get("common_name", ""),
                "botanical_name":    sidecar_slice.get("botanical_name", ""),
                "container_size":    sidecar_slice.get("container_size", ""),
                "irrigation_zone":   sidecar_slice.get("irrigation_zone", ""),
                "phenology_notes":   sidecar_slice.get("phenology_notes", ""),
                "marpa_seed":        is_marpa_seed,
                "marpa_status":      "not_run",
                "marpa_record":      None,
                "text_blob":         text_blob,
                "raw_sidecar_slice": sidecar_slice,
                "harness_run_id":    harness_run_id,
                "ingested_at":       ingested_at,
            })

    counts["ifc_elements"]       = _insert(ifc_el_t, el_rows)
    counts["ifc_property_sets"]  = _insert(ifc_pset_t, pset_rows)
    counts["semantic_sidecars"]  = _insert(sem_t, sem_rows)

    # 3. harness_run_refs (one ref per ingested artifact kind)
    if harness_run_id:
        ref_t = pxt.get_table("lattice/bridge/evidence/harness_run_refs")
        _delete_by(
            ref_t,
            (ref_t.harness_run_id == harness_run_id)
            & (ref_t.artifact_id == vw_export_hash)
            & (ref_t.artifact_kind == "vw_export"),
        )
        _insert(ref_t, [{
            "id":             uuidv7(),
            "harness_run_id": harness_run_id,
            "artifact_kind":  "vw_export",
            "artifact_id":    vw_export_hash,
            "artifact_table": "lattice/bridge/vw/vectorworks_exports",
            "relation":       "produced",
            "linked_at":      ingested_at,
            "raw_event":      {"vw_export_hash": vw_export_hash},
        }])
        counts["harness_run_refs"] = 1

    return {"vw_export_hash": vw_export_hash, "counts": counts}


# ---------------------------------------------------------------------------
# iTwin (lattice/bridge/itwin/*)
# ---------------------------------------------------------------------------


def upsert_itwin_sync_job(pxt, payload: dict[str, Any]) -> dict[str, Any]:
    t = pxt.get_table("lattice/bridge/itwin/itwin_sync_jobs")
    sync_run_id = payload["sync_run_id"]
    _delete_by(t, t.sync_run_id == sync_run_id)
    _insert(t, [{
        "id":               uuidv7(),
        "itwin_id":         payload.get("itwin_id", ""),
        "imodel_id":        payload.get("imodel_id", ""),
        "sync_run_id":      sync_run_id,
        "state":            payload.get("state", ""),
        "result":           payload.get("result", ""),
        "started_at":       payload.get("started_at"),
        "ended_at":         payload.get("ended_at"),
        "duration_ms":      int(payload.get("duration_ms", 0) or 0),
        "vw_export_hash":   payload.get("vw_export_hash", ""),
        "connector_count":  int(payload.get("connector_count", 0) or 0),
        "raw_payload":      payload,
        "observed_at":      _now(),
    }])
    return {"sync_run_id": sync_run_id}


def upsert_itwin_changed_elements(pxt, payload: dict[str, Any]) -> dict[str, Any]:
    t = pxt.get_table("lattice/bridge/itwin/itwin_changed_elements")
    page = int(payload.get("page", 0))
    page_size = int(payload.get("page_size", 0))
    rows = []
    observed = _now()
    for ce in payload.get("changed_elements", []) or []:
        rows.append({
            "id":                uuidv7(),
            "itwin_id":          payload.get("itwin_id", ""),
            "imodel_id":         payload.get("imodel_id", ""),
            "changeset_id":      ce.get("changeset_id", payload.get("changeset_id", "")),
            "source_element_id": ce.get("source_element_id", ce.get("element_id", "")),
            "change_kind":       ce.get("change_kind", ""),
            "bis_class":         ce.get("bis_class", ""),
            "bis_subcategory":   ce.get("bis_subcategory", ""),
            "before_hash":       ce.get("before_hash", ""),
            "after_hash":        ce.get("after_hash", ""),
            "page":              page,
            "page_size":         page_size,
            "observed_at":       observed,
            "raw_payload":       ce,
        })
    n = _insert(t, rows)
    return {"inserted": n, "page": page}


# ---------------------------------------------------------------------------
# MARPA (lattice/bridge/marpa/marpa_parse_runs)
# ---------------------------------------------------------------------------


def upsert_marpa_parse_run(pxt, payload: dict[str, Any]) -> dict[str, Any]:
    t = pxt.get_table("lattice/bridge/marpa/marpa_parse_runs")
    parse_run_id = payload.get("parse_run_id") or uuidv7()
    _insert(t, [{
        "id":                 uuidv7(),
        "parse_run_id":       parse_run_id,
        "vw_export_hash":     payload.get("vw_export_hash", ""),
        "source_element_id":  payload.get("source_element_id", ""),
        "pset_name":          payload.get("pset_name", ""),
        "record_kind":        payload.get("record_kind", "other"),
        "grammar_version":    payload.get("grammar_version", ""),
        "input_tokens":       payload.get("input_tokens", []),
        "parse_status":       payload.get("parse_status", "fail"),
        "ambiguity_score":    float(payload.get("ambiguity_score", 0.0) or 0.0),
        "partial_parse_json": payload.get("partial_parse_json"),
        "error_message":      payload.get("error_message", ""),
        "duration_ms":        int(payload.get("duration_ms", 0) or 0),
        "runner_kind":        payload.get("runner_kind", "python.fallback"),
        "started_at":         payload.get("started_at"),
        "ended_at":           payload.get("ended_at"),
        "harness_run_id":     payload.get("harness_run_id", ""),
    }])

    # Side-effect: if successful, write through to semantic_sidecars.marpa_*.
    if payload.get("parse_status") in ("success", "partial") and payload.get("source_element_id"):
        sem_t = pxt.get_table("lattice/bridge/semantic/semantic_sidecars")
        try:
            sem_t.update(
                {"marpa_status": payload["parse_status"],
                 "marpa_record": payload.get("partial_parse_json")},
                where=(sem_t.vw_export_hash == payload.get("vw_export_hash", ""))
                      & (sem_t.source_element_id == payload["source_element_id"]),
            )
        except Exception:
            pass

    return {"parse_run_id": parse_run_id}


# ---------------------------------------------------------------------------
# Evidence + health
# ---------------------------------------------------------------------------


def upsert_promotion_event(pxt, payload: dict[str, Any]) -> dict[str, Any]:
    t = pxt.get_table("lattice/bridge/evidence/promotion_events")
    pe_id = payload.get("promotion_event_id") or uuidv7()
    _insert(t, [{
        "id":                       uuidv7(),
        "promotion_event_id":       pe_id,
        "promotion_kind":           payload.get("promotion_kind", "validate"),
        "target_kind":              payload.get("target_kind", ""),
        "target_id":                payload.get("target_id", ""),
        "verdict":                  payload.get("verdict", "inconclusive"),
        "triggered_by":             payload.get("triggered_by", ""),
        "operator_handle":          payload.get("operator_handle", ""),
        "harness_run_id":           payload.get("harness_run_id", ""),
        "outcome_md":               payload.get("outcome_md", ""),
        "evidence_manifest_yaml":   payload.get("evidence_manifest_yaml", ""),
        "evidence_manifest_parsed": payload.get("evidence_manifest_parsed"),
        "skill_id":                 payload.get("skill_id", ""),
        "skill_version":            payload.get("skill_version", ""),
        "created_at":               payload.get("created_at") or _now(),
    }])
    return {"promotion_event_id": pe_id}


def insert_drift_event(pxt, payload: dict[str, Any]) -> dict[str, Any]:
    t = pxt.get_table("lattice/bridge/health/schema_drift_events")
    de_id = payload.get("drift_event_id") or uuidv7()
    _insert(t, [{
        "id":             uuidv7(),
        "drift_event_id": de_id,
        "severity":       payload.get("severity", "info"),
        "drift_kind":     payload.get("drift_kind", ""),
        "scope":          payload.get("scope", ""),
        "summary":        payload.get("summary", ""),
        "before":         payload.get("before"),
        "after":          payload.get("after"),
        "detected_by":    payload.get("detected_by", "service"),
        "detected_at":    payload.get("detected_at") or _now(),
        "harness_run_id": payload.get("harness_run_id", ""),
    }])
    return {"drift_event_id": de_id}
