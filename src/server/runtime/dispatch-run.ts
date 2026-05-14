import { createServerFn } from "@tanstack/react-start";
import { resolveSidecarClient } from "#/runtime/pixeltable/sidecar-client";

function newRunId(): string {
  const ts = new Date().toISOString().replace(/[:.]/g, "-");
  return `run_${ts}_${crypto.randomUUID().slice(0, 8)}`;
}

export const dispatchRun = createServerFn({ method: "POST" })
  .inputValidator(
    (data: { task: string; threadId?: string; agentKind?: string }) => data,
  )
  .handler(async ({ data }) => {
    const runId = newRunId();
    const threadId = data.threadId ?? "thread-local";
    const event = {
      kind: "run.started",
      payload: {
        run_id: runId,
        thread_id: threadId,
        agent_kind: data.agentKind ?? "claude-code",
        status: "pending",
        task: data.task,
        started_at: new Date().toISOString(),
      },
    };

    const client = resolveSidecarClient();
    const res = await client.ingestRuntimeEvents([event]);
    if (res.status < 200 || res.status >= 300) {
      throw new Error(
        `sidecar /v1/runtime/events ${res.status}: ${JSON.stringify(res.body)}`,
      );
    }
    return { runId, threadId, status: "pending" as const };
  });
