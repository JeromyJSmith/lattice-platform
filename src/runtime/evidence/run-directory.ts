import { mkdirSync } from "node:fs";
import { resolve } from "node:path";

export function ensureRunDirectory(runId: string) {
  const base = process.env.RUNTIME_RUNS_DIR ?? "./runtime-runs";
  const runDir = resolve(base, runId);
  mkdirSync(resolve(runDir, "artifacts"), { recursive: true });
  return runDir;
}
