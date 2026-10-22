export default defineNuxtRouteMiddleware(async (to) => {
  if (to.path === '/ui' || to.path === '/ui/') return
  const routeName = String(to.name || '')
  const isSetupRoute = routeName.startsWith('home-setup')
  if (routeName.startsWith('auth') || routeName === 'ui') return

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
