"""Create `lattice/execution/*` namespace and the 6 runtime-ledger tables.

Schema mirrors the existing TS `RuntimeEvent` protocol in
`src/runtime/protocol/agent-event.ts`. Insert/upsert keys are enforced
in service/upsert.py; PXT itself does not enforce uniqueness, so we add an
explicit `id` column using UUIDv7 written by the sidecar.
"""

from __future__ import annotations

from migrations._helpers import banner, ensure_namespace, ensure_table

MIGRATION_ID = "0002_create_lattice_execution"

NAMESPACE = "lattice/execution"


def schemas(pxt) -> dict[str, dict]:
    return {
        f"{NAMESPACE}/agent_threads": {
            "id":              pxt.String,
            "thread_id":       pxt.String,
            "title":           pxt.String,
            "operator_handle": pxt.String,
            "created_at":      pxt.Timestamp,
            "raw_event":       pxt.Json,
        },
        f"{NAMESPACE}/agent_messages": {
            "id":               pxt.String,
            "thread_id":        pxt.String,
            "message_id":       pxt.String,
            "role":             pxt.String,    # 'user' | 'assistant' | 'system' | 'tool'
            "content_md":       pxt.String,
            "tokens_in":        pxt.Int,
            "tokens_out":       pxt.Int,
            "model_id":         pxt.String,
            "provider":         pxt.String,
            "created_at":       pxt.Timestamp,
            "raw_event":        pxt.Json,
        },
        f"{NAMESPACE}/agent_runs": {
            "id":               pxt.String,
            "run_id":           pxt.String,
            "thread_id":        pxt.String,
            "agent_kind":       pxt.String,    # 'claude_code' | 'pi' | 'hermes' | 'openrouter'
            "model_id":         pxt.String,
            "started_at":       pxt.Timestamp,
            "ended_at":         pxt.Timestamp,
            "status":           pxt.String,    # 'started' | 'completed' | 'failed'
            "exit_code":        pxt.Int,
            "duration_ms":      pxt.Int,
            "tokens_in_total":  pxt.Int,
            "tokens_out_total": pxt.Int,
            "raw_event":        pxt.Json,
        },
        f"{NAMESPACE}/agent_stream_events": {
            "id":               pxt.String,
            "run_id":           pxt.String,
            "event_id":         pxt.String,
            "event_kind":       pxt.String,    # 'stream.delta' | 'tool.started' | 'tool.completed'
            "seq":              pxt.Int,
            "delta_text":       pxt.String,
            "tool_name":        pxt.String,
            "tool_input":       pxt.Json,
            "tool_output":      pxt.Json,
            "created_at":       pxt.Timestamp,
            "raw_event":        pxt.Json,
        },
        f"{NAMESPACE}/agent_artifacts": {
            "id":               pxt.String,
            "run_id":           pxt.String,
            "artifact_path":    pxt.String,
            "artifact_kind":    pxt.String,    # 'file' | 'image' | 'log' | 'report'
            "byte_size":        pxt.Int,
            "sha256":           pxt.String,
            "created_at":       pxt.Timestamp,
            "raw_event":        pxt.Json,
        },
        f"{NAMESPACE}/agent_outcomes": {
            "id":                       pxt.String,
            "run_id":                   pxt.String,
            "thread_id":                pxt.String,
            "terminal_status":          pxt.String,    # 'completed' | 'failed'
            "outcome_md":               pxt.String,
            "evidence_manifest_yaml":   pxt.String,
            "evidence_manifest_parsed": pxt.Json,
            "closed_at":                pxt.Timestamp,
            "raw_event":                pxt.Json,
        },
    }


def apply(pxt, dry_run: bool) -> dict:
    banner("0002 lattice/execution", dry_run=dry_run)
    out: dict = {NAMESPACE: ensure_namespace(pxt, NAMESPACE, dry_run)}
    print(f"  {NAMESPACE} -> {out[NAMESPACE]}")
    for path, schema in schemas(pxt).items():
        action = ensure_table(pxt, path, schema, dry_run)
        out[path] = {"action": action, "cols": len(schema)}
        print(f"  {path:48s} -> {action} ({len(schema)} cols)")
    return out
