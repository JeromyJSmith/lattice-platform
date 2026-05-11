import type { RuntimeEvent } from '../protocol/agent-event'
import type { RuntimeAdapter } from './base-adapter'

export const claudeCodeAdapter: RuntimeAdapter = {
  id: 'claude-code',
  async *run(input) {
    const now = new Date().toISOString()
    const runId = `run-${crypto.randomUUID()}`
    yield { type: 'run.started', eventId: crypto.randomUUID(), threadId: input.threadId, runId, agentId: 'claude-code', createdAt: now }
    yield { type: 'stream.delta', eventId: crypto.randomUUID(), threadId: input.threadId, runId, seq: 1, text: `Claude Code adapter accepted prompt: ${input.prompt}`, createdAt: new Date().toISOString() }
    yield { type: 'run.completed', eventId: crypto.randomUUID(), threadId: input.threadId, runId, outcomeId: crypto.randomUUID(), createdAt: new Date().toISOString() }
  },
}
