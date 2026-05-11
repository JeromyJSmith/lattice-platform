import { createServerFn } from '@tanstack/react-start'

export type StreamEventRow = {
  event_id: string
  event_kind: string
  seq: number
  delta_text: string
  tool_name: string
  created_at: string | null
}

export const listStreamEvents = createServerFn({ method: 'GET' })
  .inputValidator((data: { runId: string; afterSeq?: number }) => data)
  .handler(async ({ data }) => {
    const base = process.env.PIXELTABLE_SERVICE_URL ?? 'http://127.0.0.1:7770'
    const params = new URLSearchParams({
      run_id: data.runId,
      after_seq: String(data.afterSeq ?? 0),
    })
    const res = await fetch(`${base}/v1/runtime/stream-events?${params}`)
    if (!res.ok) {
      throw new Error(`sidecar /v1/runtime/stream-events ${res.status}: ${await res.text()}`)
    }
    const body = (await res.json()) as { rows: Array<StreamEventRow>; count: number }
    return body.rows
  })
