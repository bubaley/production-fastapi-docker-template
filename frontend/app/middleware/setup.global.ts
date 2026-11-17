import { ensureSession } from '~/shared/composables/useSession'
import { fetchItem } from '~/shared/api/resource'
import { useApiClient } from '~/shared/api/useResource'
import { organizationResource } from '~/features/organization/resources/organization'

/**
 * Every app route works inside the selected organization, chosen without asking (see `useSetupStore().restore`).
 * A user with no organization at all lands on `home`, where the shell asks to create one.
 */
export default defineNuxtRouteMiddleware(async (to) => {
  if (import.meta.server || to.meta.auth === false || to.meta.auth === 'guest' || to.meta.auth === 'setup') return
  const setupStore = useSetupStore()
  if (!setupStore.state.restored) {
    const session = await ensureSession()
    if (!session) return
    const client = useApiClient()
    await setupStore.restore({
      userId: session.user.id,
      organizations: session.organizations,
      // A member's organizations are all in the session; only a superuser may have stored one outside them.
      retrieve: session.user.is_superuser ? (id) => fetchItem(organizationResource, client, id) : undefined,
    })
  }
  if (setupStore.state.organization || to.meta.organization === false || to.name === 'home') return
  return navigateTo({ name: 'home' })
})
