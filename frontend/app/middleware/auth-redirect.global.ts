
export default defineNuxtRouteMiddleware(async (to) => {
  if (to.path === '/ui' || to.path === '/ui/') return
  const publicNames = ['auth', 'ui']
  if (publicNames.includes(to.name as string)) return
  const { getSession } = useAuth()
  if (import.meta.server) {
    const { data } = await getSession()
    if (!data) {
      return navigateTo({ name: 'auth', query: { redirect: to.fullPath } })
    }
  }
})
