import { createServerFn } from '@tanstack/react-start'

export type RunRow = {
  run_id: string
  status: string
  agent_kind: string
  task: string
  started_at: string | null
}

export const listRuns = createServerFn({ method: 'GET' }).handler(async () => {
  const base = process.env.PIXELTABLE_SERVICE_URL ?? 'http://127.0.0.1:7770'
  const res = await fetch(`${base}/v1/runtime/runs?limit=100`)
  if (!res.ok) {
    throw new Error(`sidecar /v1/runtime/runs ${res.status}: ${await res.text()}`)
  }
  const body = (await res.json()) as { rows: Array<RunRow>; count: number }
  return body.rows
})
