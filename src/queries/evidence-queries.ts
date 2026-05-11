import { queryOptions } from '@tanstack/react-query'

export const evidenceQueryOptions = queryOptions({
  queryKey: ['runtime', 'evidence'],
  queryFn: async () => [],
})
