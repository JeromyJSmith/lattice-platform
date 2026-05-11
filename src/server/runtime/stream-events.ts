import { createServerFn } from '@tanstack/react-start'

export const streamEvents = createServerFn({ method: 'GET' })
  .inputValidator((data: { runId: string }) => data)
  .handler(async ({ data }) => {
    return {
      runId: data.runId,
      stream: 'TODO: attach live SSE stream for RuntimeEvent records',
    }
  })
