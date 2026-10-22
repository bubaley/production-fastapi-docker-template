import { ensureSession } from '~/shared/composables/useSession'
import { fetchItem } from '~/shared/api/resource'
import { useApiClient } from '~/shared/api/useResource'
import { organizationResource } from '~/features/organization/resources/organization'

/** Every app route works inside the selected organization; without one the user goes to `/home/setup` first. */
export default defineNuxtRouteMiddleware(async (to) => {
  if (import.meta.server || to.meta.auth === false || to.meta.auth === 'guest') return
  const setupStore = useSetupStore()
  if (!setupStore.state.restored) {
    const session = await ensureSession()
    if (!session) return
    const client = useApiClient()
    await setupStore.restore({
      userId: session.user.id,
      organizations: session.organizations,
      retrieve: (id) => fetchItem(organizationResource, client, id),
    })
  }
  if (setupStore.state.organization || to.meta.organization === false) return
  return navigateTo({ name: 'home-setup' })
})
