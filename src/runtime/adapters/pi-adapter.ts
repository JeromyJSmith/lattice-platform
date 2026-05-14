import type { RuntimeAdapter } from "./base-adapter";

export const piAdapter: RuntimeAdapter = {
  id: "pi",
  async *run(input) {
    const runId = `run-${crypto.randomUUID()}`;
    yield {
      type: "run.started",
      eventId: crypto.randomUUID(),
      threadId: input.threadId,
      runId,
      agentId: "pi",
      createdAt: new Date().toISOString(),
    };
    yield {
      type: "stream.delta",
      eventId: crypto.randomUUID(),
      threadId: input.threadId,
      runId,
      seq: 1,
      text: `Pi adapter queued: ${input.prompt}`,
      createdAt: new Date().toISOString(),
    };
    yield {
      type: "run.completed",
      eventId: crypto.randomUUID(),
      threadId: input.threadId,
      runId,
      outcomeId: crypto.randomUUID(),
      createdAt: new Date().toISOString(),
    };
  },
};
