export default defineNuxtRouteMiddleware(async (to) => {
  const routeName = String(to.name || '')
  const isSetupRoute = routeName.startsWith('home-setup')
  if (routeName.startsWith('auth')) return

  const setupStore = useSetupStore()

  if (import.meta.server) return

  try {
    if (!setupStore.state.restored) await setupStore.restore()
  } catch {
    setupStore.state.organization = null
  }

  if (!setupStore.state.organization) {
    if (isSetupRoute) return
    return navigateTo({ name: 'home-setup' })
  }
})
