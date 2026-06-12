export const normalizeUrl = (baseUrl?: unknown, ...append: (unknown)[]) => {
  const url =
    [baseUrl, ...append]
      .map((v) => typeof v === 'string' ? v.replace(/^\/+|\/+$/g, "") : null)
      .filter((v) => v)
      .join("/") || "/";
    if (baseUrl) return url
    return url.startsWith("/") ? url : `/${url}`;
};


export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()
  const baseUrl = normalizeUrl(config.public.baseUrl, config.public.apiPrefix)
  const apiFetch = $fetch.create({
    credentials: 'include',
    baseURL: baseUrl,
    async onRequest({options}) {
      const {state} = useSetupStore()
      if(state.organization?.key) options.headers.append('Organization-Key', state.organization?.key)
      if (import.meta.server) {
        const cookieHeader = useRequestHeaders(['cookie']).cookie
        if (cookieHeader) {
          options.headers.append('Cookie', cookieHeader)
        }
      }
    },
  })

  return {
    provide: {
      api: apiFetch,
    },
  }
})
