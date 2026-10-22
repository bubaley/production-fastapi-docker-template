import { useQueryCache } from '@pinia/colada'
import { createApiClient } from '~/shared/api/client'
import { SESSION_KEY } from '~/shared/composables/useSession'

/**
 * Provides `$api`, the generated client for this app instance (one per request on the server):
 * - browser: same-origin `/api/v1/...` (Caddy in production, the dev proxy in `nuxt dev`); on 401 it refreshes the
 *   session once and retries; a failed refresh signs out and sends app routes to `/auth`.
 * - SSR: `NUXT_API_INTERNAL_URL` with the incoming `cookie` header; only GETs run during SSR (CSRF contract).
 * Every request carries `Organization-Key` of the selected organization.
 */
export default defineNuxtPlugin({
  name: 'api',
  setup(nuxtApp) {
    const config = useRuntimeConfig()
    const setupStore = useSetupStore()
    const router = useRouter()
    const cookie = import.meta.server ? useRequestHeaders(['cookie']).cookie : undefined

    let navigating = false
    router.beforeEach(() => {
      navigating = true
    })
    router.afterEach(() => {
      navigating = false
    })
    router.onError(() => {
      navigating = false
    })

    // A navigation in progress handles the missing session itself (route middleware redirects with `redirect`).
    const onSignedOut = () =>
      nuxtApp.runWithContext(() => {
        useQueryCache().setQueryData([...SESSION_KEY], null)
        const route = router.currentRoute.value
        if (navigating || route.meta.auth === false || route.meta.auth === 'guest') return
        void navigateTo({ name: 'auth', query: { redirect: route.fullPath } })
      })

    const api = createApiClient({
      baseUrl: import.meta.server ? config.apiInternalUrl : '',
      refreshOnUnauthorized: import.meta.client,
      onSignedOut,
      headers: () => ({ 'Organization-Key': setupStore.state.organization?.key, cookie }),
    })

    return { provide: { api } }
  },
})
