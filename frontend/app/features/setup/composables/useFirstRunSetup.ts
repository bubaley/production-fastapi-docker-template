import { useMutation, useQuery, useQueryCache } from '@pinia/colada'
import { setupComplete, setupStatus } from '~/shared/api/generated'
import type { SetupRequest, SetupStatusSchema } from '~/shared/api/generated'
import type { ApiClient } from '~/shared/api/client'
import { useApiClient } from '~/shared/api/useResource'
import { resetQueryCache } from '~/shared/composables/useSession'

const SETUP_STATUS_KEY = ['setup-status'] as const

const statusQuery = (client: ApiClient) => ({
  key: [...SETUP_STATUS_KEY],
  query: async ({ signal }: { signal: AbortSignal }): Promise<SetupStatusSchema> =>
    (await setupStatus({ client, throwOnError: true, signal })).data,
  staleTime: 0,
})

/**
 * For route middleware: whether the deployment has no users yet. "Done" is final and never asked again;
 * "needs setup" is re-checked, since setup may have been completed elsewhere. A failed check means "no" (sign-in).
 */
export const needsFirstRunSetup = async (): Promise<boolean> => {
  const queryCache = useQueryCache()
  const entry = queryCache.ensure(statusQuery(useApiClient()))
  if (entry.state.value.status === 'success' && !entry.state.value.data.needs_setup) return false
  try {
    return (await queryCache.refresh(entry)).data?.needs_setup ?? false
  } catch {
    return false
  }
}

/** The setup screen: status (is a setup token needed) and the mutation that creates the first administrator. */
export const useFirstRunSetup = () => {
  const client = useApiClient()
  const queryCache = useQueryCache()
  const status = useQuery(statusQuery(client))
  const complete = useMutation({
    mutation: (body: SetupRequest) => setupComplete({ client, body, throwOnError: true }),
    onSuccess: ({ data }) => {
      queryCache.setQueryData([...SETUP_STATUS_KEY], { needs_setup: false, token_required: false })
      resetQueryCache(queryCache, { user: data.user, organizations: data.organizations })
    },
  })
  return { status, complete }
}
