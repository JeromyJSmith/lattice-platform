import { createFileRoute } from '@tanstack/react-router'
import { generateOpenRouterText } from '#/server/ai/openrouter'

export const Route = createFileRoute('/api/runtime/openrouter')({
  server: {
    handlers: {
      POST: async ({ request }) => {
        try {
          const body = (await request.json()) as { prompt?: string }
          const prompt = body.prompt ?? ''
          const text = await generateOpenRouterText(prompt)
          return Response.json({ text })
        } catch (error) {
          return Response.json(
            { error: 'OpenRouter request failed', details: String(error) },
            { status: 500 },
          )
        }
      },
    },
  },
})
