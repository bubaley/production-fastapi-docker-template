import { useAuth } from '../composables/useAuth'
import { getBaseAuthConfig } from '../utils/config-utils'

export default defineNuxtRouteMiddleware(async () => {
  if (import.meta.server) {
    const config = getBaseAuthConfig()
    const { getTokens, getSession } = useAuth()
    await getTokens()
    if (!config.disableServerSideAuth) {
      await getSession()
    }
  }
})
