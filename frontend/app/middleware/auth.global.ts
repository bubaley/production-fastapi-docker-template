import { ensureSession } from '~/shared/composables/useSession'

declare module '#app' {
  interface PageMeta {
    /** `false`: public page (SSR, no session needed). `'guest'`: only for signed-out users (`/auth`). */
    auth?: false | 'guest'
    /** `false`: reachable before an organization is selected (setup, profile). */
    organization?: false
  }
}

/**
 * App routes need a session; public pages never wait for one. App routes render client-only (`routeRules`), so on
 * the server this only sees public pages.
 */
export default defineNuxtRouteMiddleware(async (to) => {
  if (to.meta.auth === false) return
  if (import.meta.server) return
  const session = await ensureSession()
  if (to.meta.auth === 'guest') {
    if (session) return navigateTo(safeRedirect(to.query.redirect) ?? { name: 'home' })
    return
  }
  if (!session) return navigateTo({ name: 'auth', query: { redirect: to.fullPath } })
})
