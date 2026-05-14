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
        events.push(evt);
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
