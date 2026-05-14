import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import type { RuntimeEvent } from "../protocol/agent-event";

export function replayEvents(runDir: string): RuntimeEvent[] {
  const raw = readFileSync(resolve(runDir, "events.jsonl"), "utf8").trim();
  if (!raw) return [];
  return raw.split("\n").map((line) => JSON.parse(line) as RuntimeEvent);
}
