/**
 * ingest-run-to-pixeltable.ts
 *
 * Walk a runtime run directory, transform every recorded event into the
 * Python sidecar's RuntimeEvent shape, and POST them to /v1/runtime/events.
 *
 * Run directory layout (current MVP):
 *   <runDir>/run.yaml           (metadata + outcome)
 *   <runDir>/events.jsonl       (one TS RuntimeEvent per line; optional)
 *   <runDir>/evidence-manifest.yaml  (optional)
 *   <runDir>/artifacts/...      (optional)
 *
 * Exit codes:
 *   0  success
 *   2  bad arguments
 *   3  run directory missing required files
 *   4  sidecar rejected the request
 *   5  network or transport failure
 */

import { existsSync, readFileSync, statSync } from "node:fs";
import { readdir } from "node:fs/promises";
import { basename, join, resolve } from "node:path";
import process from "node:process";

import { SidecarClient } from "../src/runtime/pixeltable/sidecar-client";

const runDir = process.argv[2];
if (!runDir) {
  console.error("Usage: bun run scripts/ingest-run-to-pixeltable.ts <run-dir>");
  process.exit(2);
}

const absRunDir = resolve(runDir);
if (!existsSync(absRunDir) || !statSync(absRunDir).isDirectory()) {
  console.error(`run-dir does not exist or is not a directory: ${absRunDir}`);
  process.exit(3);
}

main().catch((err) => {
  console.error("ingest failed:", err);
  process.exit(5);
});

async function main(): Promise<void> {
  const harnessRunId = basename(absRunDir);
  const events: Array<Record<string, unknown>> = [];

  const eventsJsonl = join(absRunDir, "events.jsonl");
  if (existsSync(eventsJsonl)) {
    const lines = readFileSync(eventsJsonl, "utf8").split("\n");
    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed) continue;
      try {
        const evt = JSON.parse(trimmed) as Record<string, unknown>;
        const mapped = toSidecarEvent(evt, harnessRunId);
        if (mapped) events.push(mapped);
      } catch (err) {
        console.warn(
          `skipping malformed event line: ${(err as Error).message}`,
        );
      }
    }
  }

  const runYaml = join(absRunDir, "run.yaml");
  if (existsSync(runYaml)) {
    events.push({
      kind: "run.terminal",
      payload: {
        run_id: harnessRunId,
        thread_id: harnessRunId,
        status: "completed",
        outcome_md: "",
        evidence_manifest_yaml:
          tryRead(join(absRunDir, "evidence-manifest.yaml")) ?? "",
        closed_at: new Date().toISOString(),
      },
    });
  }

  const artifactsDir = join(absRunDir, "artifacts");
  if (existsSync(artifactsDir)) {
    const entries = await readdir(artifactsDir, { withFileTypes: true });
    for (const e of entries) {
      if (!e.isFile()) continue;
      const fullPath = join(artifactsDir, e.name);
      const st = statSync(fullPath);
      events.push({
        kind: "artifact.added",
        payload: {
          run_id: harnessRunId,
          artifact_path: fullPath,
          artifact_kind: detectArtifactKind(e.name),
          byte_size: st.size,
          sha256: "",
          created_at: new Date(st.mtimeMs).toISOString(),
        },
      });
    }
  }

  if (events.length === 0) {
    console.warn(`no events derived from ${absRunDir}; nothing to send`);
    return;
  }

  const client = new SidecarClient();
  console.log(
    `posting ${events.length} events to sidecar (mode=${client.mode}` +
      (client.mode === "uds"
        ? ` socket=${client.socketPath}`
        : ` baseUrl=${client.baseUrl}`) +
      `)`,
  );

  const idemKey = `harness:${harnessRunId}:v1`;
  const res = await client.ingestRuntimeEvents(events, idemKey);
  if (res.status >= 200 && res.status < 300) {
    console.log(`sidecar OK status=${res.status} idem=${res.idempotencyKey}`);
    console.log(JSON.stringify(res.body, null, 2));
    return;
  }
  console.error(`sidecar rejected: status=${res.status}`);
  console.error(JSON.stringify(res.body, null, 2));
  process.exit(4);
}

function toSidecarEvent(
  evt: Record<string, unknown>,
  fallbackRunId: string,
): Record<string, unknown> | null {
  const existingPayload = asRecord(evt.payload);
  const existingKind = asString(evt.kind) ?? asString(evt.event_kind);
  if (existingKind && existingPayload?.run_id) {
    return evt;
  }

  const kind = asString(evt.type) ?? existingKind;
  if (!kind) return null;

  if (kind === "run.started") {
    return {
      kind,
      payload: {
        run_id: asString(evt.runId) ?? fallbackRunId,
        thread_id: asString(evt.threadId) ?? fallbackRunId,
        agent_kind: asString(evt.agentId) ?? "router",
        status: "running",
        started_at: asString(evt.createdAt) ?? new Date().toISOString(),
      },
    };
  }

  if (kind === "run.completed") {
    return {
      kind,
      payload: {
        run_id: asString(evt.runId) ?? fallbackRunId,
        thread_id: asString(evt.threadId) ?? fallbackRunId,
        status: "completed",
        ended_at: asString(evt.createdAt) ?? new Date().toISOString(),
      },
    };
  }

  if (kind === "run.failed") {
    return {
      kind,
      payload: {
        run_id: asString(evt.runId) ?? fallbackRunId,
        thread_id: asString(evt.threadId) ?? fallbackRunId,
        status: "failed",
        outcome_md: asString(evt.error) ?? "run.failed",
        closed_at: asString(evt.createdAt) ?? new Date().toISOString(),
      },
    };
  }

  if (kind === "stream.delta") {
    return {
      kind,
      payload: {
        run_id: asString(evt.runId) ?? fallbackRunId,
        event_id: asString(evt.eventId) ?? "",
        seq: asNumber(evt.seq) ?? 0,
        delta_text: asString(evt.text) ?? asString(evt.delta_text) ?? "",
        created_at: asString(evt.createdAt) ?? new Date().toISOString(),
      },
    };
  }

  if (kind === "tool.started" || kind === "tool.completed") {
    return {
      kind,
      payload: {
        run_id: asString(evt.runId) ?? fallbackRunId,
        event_id: asString(evt.eventId) ?? "",
        seq: asNumber(evt.seq) ?? 0,
        tool_name: asString(evt.toolName) ?? "",
        tool_input: evt.toolInput ?? null,
        tool_output: evt.toolOutput ?? null,
        created_at: asString(evt.createdAt) ?? new Date().toISOString(),
      },
    };
  }

  if (kind === "artifact.created" || kind === "artifact.added") {
    return {
      kind: "artifact.added",
      payload: {
        run_id: asString(evt.runId) ?? fallbackRunId,
        artifact_path: asString(evt.path) ?? asString(evt.artifact_path) ?? "",
        artifact_kind:
          asString(evt.mimeType) ??
          detectArtifactKind(asString(evt.path) ?? ""),
        byte_size: asNumber(evt.byte_size) ?? 0,
        sha256: asString(evt.sha256) ?? "",
        created_at: asString(evt.createdAt) ?? new Date().toISOString(),
      },
    };
  }

  if (kind === "thread.created") {
    return {
      kind,
      payload: {
        thread_id: asString(evt.threadId) ?? fallbackRunId,
        created_at: asString(evt.createdAt) ?? new Date().toISOString(),
      },
    };
  }

  if (kind === "message.created" || kind === "message.added") {
    return {
      kind: "message.added",
      payload: {
        thread_id: asString(evt.threadId) ?? fallbackRunId,
        message_id: asString(evt.messageId) ?? asString(evt.eventId) ?? "",
        role: asString(evt.sourceAgent) ?? "agent",
        content_md: asString(evt.content) ?? "",
        created_at: asString(evt.createdAt) ?? new Date().toISOString(),
      },
    };
  }

  return null;
}

function asRecord(value: unknown): Record<string, unknown> | null {
  if (typeof value !== "object" || value === null) return null;
  return value as Record<string, unknown>;
}

function asString(value: unknown): string | null {
  return typeof value === "string" ? value : null;
}

function asNumber(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

function tryRead(path: string): string | null {
  try {
    return readFileSync(path, "utf8");
  } catch {
    return null;
  }
}

function detectArtifactKind(name: string): string {
  const lower = name.toLowerCase();
  if (lower.endsWith(".ifc")) return "ifc";
  if (lower.endsWith(".vwx")) return "vwx";
  if (lower.endsWith(".json")) return "sidecar_json";
  if (lower.endsWith(".yaml") || lower.endsWith(".yml")) return "manifest_yaml";
  if (lower.endsWith(".md")) return "markdown";
  if (
    lower.endsWith(".png") ||
    lower.endsWith(".jpg") ||
    lower.endsWith(".jpeg") ||
    lower.endsWith(".webp")
  )
    return "image";
  return "other";
}
