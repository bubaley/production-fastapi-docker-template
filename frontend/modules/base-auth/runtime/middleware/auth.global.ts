import { useAuth } from '../composables/useAuth'
import { getBaseAuthConfig } from '../utils/config-utils'

export default defineNuxtRouteMiddleware(async (to) => {
  if (to.path === '/ui' || to.path === '/ui/') return
  if (to.name === 'ui') return
  if (import.meta.server) {
    const config = getBaseAuthConfig()
    const { getTokens, getSession } = useAuth()
    await getTokens()
    if (!config.disableServerSideAuth) {
      await getSession()
    }
  }
})
