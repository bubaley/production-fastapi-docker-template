
export default defineNuxtRouteMiddleware(async (to) => {
  const publicNames = ['auth']
  if (publicNames.includes(to.name as string)) return
  const { getSession } = useAuth()
  if (import.meta.server) {
    const { data } = await getSession()
    if (!data) {
      return navigateTo({ name: 'auth', query: { redirect: to.fullPath } })
    }
  }
})
