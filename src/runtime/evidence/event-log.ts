import { appendFileSync } from "node:fs";
import { resolve } from "node:path";
import type { RuntimeEvent } from "../protocol/agent-event";

export function appendEvent(runDir: string, event: RuntimeEvent) {
  const eventsPath = resolve(runDir, "events.jsonl");
  appendFileSync(eventsPath, `${JSON.stringify(event)}\n`, "utf8");
}
