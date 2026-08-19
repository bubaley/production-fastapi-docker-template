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
    retryDelay: 2000,
    async onRequest({ options }) {
      const { state } = useSetupStore()
      const headers = new Headers(options.headers)
      if (state.organization?.key) headers.set('Organization-Key', state.organization.key)
      if (import.meta.server) {
        const cookieHeader = useRequestHeaders(['cookie']).cookie
        if (cookieHeader) headers.set('Cookie', cookieHeader)
      }
      options.headers = headers
    },
  })

  return {
    provide: {
      api: apiFetch,
    },
  }
})
