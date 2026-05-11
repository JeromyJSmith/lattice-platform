import { createServerFn } from '@tanstack/react-start'
import { createFilesystemLedger } from '#/runtime/evidence/filesystem-ledger'
import { routeTaskToAgent } from '#/runtime/router/runtime-router'

export const runAgent = createServerFn({ method: 'POST' })
  .inputValidator((data: { threadId: string; prompt: string }) => data)
  .handler(async ({ data }) => {
    const runId = `${new Date().toISOString().replace(/[:.]/g, '-')}-${crypto.randomUUID()}`
    const ledger = createFilesystemLedger({ runId, prompt: data.prompt })
    const route = routeTaskToAgent({ message: data.prompt })

    ledger.append({
      type: 'run.started',
      eventId: crypto.randomUUID(),
      threadId: data.threadId,
      runId,
      agentId: route.agent,
      createdAt: new Date().toISOString(),
    })

    ledger.append({
      type: 'stream.delta',
      eventId: crypto.randomUUID(),
      threadId: data.threadId,
      runId,
      seq: 1,
      text: `Routed to ${route.agent}: ${route.reason}`,
      createdAt: new Date().toISOString(),
    })

    ledger.append({
      type: 'run.completed',
      eventId: crypto.randomUUID(),
      threadId: data.threadId,
      runId,
      outcomeId: crypto.randomUUID(),
      createdAt: new Date().toISOString(),
    })

    ledger.complete(`Completed by ${route.agent}`)
    return { runId, agentId: route.agent }
  })
