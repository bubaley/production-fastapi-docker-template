import { ensureSession } from '~/shared/composables/useSession'
import { needsFirstRunSetup } from '~/features/setup/composables/useFirstRunSetup'

declare module '#app' {
  interface PageMeta {
    /**
     * `false`: public page (SSR, no session needed). `'guest'`: only for signed-out users (`/auth`). `'setup'`: the
     * first-run setup (`/setup`), only while the deployment has no users.
     */
    auth?: false | 'guest' | 'setup'
    /** `false`: reachable before an organization is selected (setup, profile). */
    organization?: false
  }
}

/**
 * App routes need a session; public pages never wait for one. App routes render client-only (`routeRules`), so on
 * the server this only sees public pages. While the deployment has no users, signed-out visitors go to `/setup`.
 */
export default defineNuxtRouteMiddleware(async (to) => {
  if (to.meta.auth === false) return
  if (import.meta.server) return
  const session = await ensureSession()
  if (to.meta.auth === 'setup') {
    if (session) return navigateTo({ name: 'home' })
    if (!(await needsFirstRunSetup())) return navigateTo({ name: 'auth' })
    return
  }
  if (to.meta.auth === 'guest') {
    if (session) return navigateTo(safeRedirect(to.query.redirect) ?? { name: 'home' })
    if (await needsFirstRunSetup()) return navigateTo({ name: 'setup' })
    return
  }
  if (!session) {
    if (await needsFirstRunSetup()) return navigateTo({ name: 'setup' })
    return navigateTo({ name: 'auth', query: { redirect: to.fullPath } })
  }
})
