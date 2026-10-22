import { useMutation, useQuery, useQueryCache, type QueryCache } from '@pinia/colada'
import { computed } from 'vue'
import { isApiError, type ApiClient } from '~/shared/api/client'
import { authLogin, authLogout, authLogoutAll, authMe } from '~/shared/api/generated'
import type { LoginRequest, MeSchema } from '~/shared/api/generated'
import { useApiClient } from '~/shared/api/useResource'

/** `GET /auth/me`: the user and their organizations; `null` when signed out. */
export type Session = MeSchema
export const SESSION_KEY = ['session'] as const
const SESSION_STALE_TIME = 5 * 60_000

const fetchSession = async (client: ApiClient, signal?: AbortSignal): Promise<Session | null> => {
  try {
    return (await authMe({ client, throwOnError: true, signal })).data
  } catch (error) {
    // 401 after the client already tried to refresh: signed out. On SSR there is no refresh, so this renders anonymous.
    if (isApiError(error, 401)) return null
    throw error
  }
}

const sessionQuery = (client: ApiClient) => ({
  key: [...SESSION_KEY],
  query: ({ signal }: { signal: AbortSignal }) => fetchSession(client, signal),
  staleTime: SESSION_STALE_TIME,
})

/**
 * Another identity starts (login, sign-out): other users' data must not survive. Entries no component uses are
 * dropped; the ones on screen are refetched with the new cookies.
 */
export const resetQueryCache = (queryCache: QueryCache, session: Session | null) => {
  const isSession = (key: readonly unknown[]) => key[0] === SESSION_KEY[0]
  for (const entry of queryCache.getEntries()) {
    if (!entry.active && !isSession(entry.key)) queryCache.remove(entry)
  }
  queryCache.setQueryData([...SESSION_KEY], session)
  void queryCache.invalidateQueries({ predicate: (entry) => entry.active && !isSession(entry.key) })
}

/**
 * The session for route middleware: cached for a few minutes, but a cached "signed out" is always re-checked,
 * because the browser may still hold a refresh cookie (SSR cannot use it).
 */
export const ensureSession = async (): Promise<Session | null> => {
  const queryCache = useQueryCache()
  const entry = queryCache.ensure(sessionQuery(useApiClient()))
  if (entry.state.value.status === 'success' && entry.state.value.data === null) queryCache.invalidate(entry)
  try {
    return (await queryCache.refresh(entry)).data ?? null
  } catch {
    return null
  }
}

export const useSession = () => {
  const client = useApiClient()
  const queryCache = useQueryCache()
  const setupStore = useSetupStore()
  const toast = useToast()
  const query = useQuery(sessionQuery(client))
  const session = computed(() => query.data.value ?? null)

  // Leave the app first, so its queries are no longer on screen, then drop the previous user's data.
  const signedOut = async () => {
    queryCache.setQueryData([...SESSION_KEY], null)
    setupStore.reset()
    toast.dismiss()
    await navigateTo({ name: 'auth' })
    resetQueryCache(queryCache, null)
  }

  const login = useMutation({
    mutation: (body: LoginRequest) => authLogin({ client, body, throwOnError: true }),
    onSuccess: ({ data }) => {
      resetQueryCache(queryCache, { user: data.user, organizations: data.organizations })
    },
  })
  const logout = useMutation({
    mutation: () => authLogout({ client, throwOnError: true }),
    onSuccess: signedOut,
  })
  const logoutAll = useMutation({
    mutation: () => authLogoutAll({ client, throwOnError: true }),
    onSuccess: signedOut,
  })

  return {
    session,
    user: computed(() => session.value?.user ?? null),
    organizations: computed(() => session.value?.organizations ?? []),
    isSignedIn: computed(() => Boolean(session.value)),
    query,
    login,
    logout,
    logoutAll,
  }
}
