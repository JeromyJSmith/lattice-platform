import { queryOptions } from '@tanstack/react-query'

export const threadsQueryOptions = queryOptions({
  queryKey: ['runtime', 'threads'],
  queryFn: async () => [],
})
