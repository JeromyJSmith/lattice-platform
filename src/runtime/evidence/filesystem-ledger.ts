import { writeFileSync } from "node:fs";
import { resolve } from "node:path";
import type { RuntimeEvent } from "../protocol/agent-event";
import { appendEvent } from "./event-log";
import { ensureRunDirectory } from "./run-directory";

export function createFilesystemLedger(input: {
  runId: string;
  prompt: string;
}) {
  const runDir = ensureRunDirectory(input.runId);
  writeFileSync(resolve(runDir, "prompt.md"), `${input.prompt}\n`, "utf8");
  writeFileSync(
    resolve(runDir, "run.yaml"),
    `run_id: ${input.runId}\n`,
    "utf8",
  );
  return {
    runDir,
    append: (event: RuntimeEvent) => appendEvent(runDir, event),
    complete: (summary: string) => {
      writeFileSync(resolve(runDir, "outcome.md"), `${summary}\n`, "utf8");
      writeFileSync(
        resolve(runDir, "evidence-manifest.yaml"),
        "version: 1\nartifacts:\n  - prompt.md\n  - events.jsonl\n  - outcome.md\n",
        "utf8",
      );
    },
  };
}
