import type { RuntimeAdapter } from './base-adapter'

export const openRouterAdapter: RuntimeAdapter = {
  id: 'openrouter',
  async *run(input) {
    const runId = `run-${crypto.randomUUID()}`
    yield { type: 'run.started', eventId: crypto.randomUUID(), threadId: input.threadId, runId, agentId: 'openrouter', createdAt: new Date().toISOString() }
    yield { type: 'stream.delta', eventId: crypto.randomUUID(), threadId: input.threadId, runId, seq: 1, text: `OpenRouter adapter request prepared for: ${input.prompt}`, createdAt: new Date().toISOString() }
    yield { type: 'run.completed', eventId: crypto.randomUUID(), threadId: input.threadId, runId, outcomeId: crypto.randomUUID(), createdAt: new Date().toISOString() }
  },
}
