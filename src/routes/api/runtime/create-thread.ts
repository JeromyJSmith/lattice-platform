import { createFileRoute } from '@tanstack/react-router'
import { createThread } from '#/server/runtime/create-thread'

export const Route = createFileRoute('/api/runtime/create-thread')({
  server: {
    handlers: {
      POST: async ({ request }) => {
        const body = (await request.json()) as { title?: string }
        const result = await createThread({ data: body })
        return Response.json(result)
      },
    },
  },
})
