import { createFileRoute } from '@tanstack/react-router'
import { runAgent } from '#/server/runtime/run-agent'

export const Route = createFileRoute('/api/runtime/run-agent')({
  server: {
    handlers: {
      POST: async ({ request }) => {
        const body = (await request.json()) as { threadId: string; prompt: string }
        const result = await runAgent({ data: body })
        return Response.json(result)
      },
    },
  },
})
