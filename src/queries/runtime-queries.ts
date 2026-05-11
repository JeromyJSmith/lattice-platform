import { queryOptions } from '@tanstack/react-query'
import { listRuns } from '#/server/runtime/list-runs'

export const runsQueryOptions = queryOptions({
  queryKey: ['runtime', 'runs'],
  queryFn: () => listRuns(),
})

// Stream events are no longer polled — see `src/hooks/use-stream-events.ts`
// for the EventSource-based subscription that replaces the old query.
