import type { PiniaColadaOptions } from '@pinia/colada'

// Global Pinia Colada defaults (read by @pinia/colada-nuxt). Mutations invalidate what they change, so data can
// stay fresh for a while; switching back to the tab refetches stale queries.
export default {
  queryOptions: {
    staleTime: 30_000,
  },
} satisfies PiniaColadaOptions
