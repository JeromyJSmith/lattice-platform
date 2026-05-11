import { createFileRoute } from '@tanstack/react-router'
import { listRuns } from '#/server/runtime/list-runs'

export const Route = createFileRoute('/api/runtime/list-runs')({
  server: {
    handlers: {
      GET: async () => {
        const result = await listRuns()
        return Response.json(result)
      },
    },
  },
})
