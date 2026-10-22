import type { $Fetch } from 'ofetch'
import { createCookieCodec } from '~/shared/toolkits/authentication/authTokenPairCodec'

interface AuthUser {
  id: number | null
  email: string
  is_staff: boolean
}

export const useAuthRepo = defineStore('authRepo', () => {
  const { state, actions } = createAuthAppRepo<AuthUser>({
    urls: {
      login: 'users/login',
      register: 'users/register',
      refresh: 'refresh',
      me: 'users/me',
    },
    tokenPairCodec: createCookieCodec({
      decodeAccessKey: 'access_token',
      decodeRefreshKey: 'refresh_token',
      storageAccessKey: 'access_token',
      storageRefreshKey: 'refresh_token',
    }),
    parseUser: (v) => v,
    apiClient: useNuxtApp().$api as $Fetch,
  })()

  return {
    ...state,
    ...actions,
  }
})
