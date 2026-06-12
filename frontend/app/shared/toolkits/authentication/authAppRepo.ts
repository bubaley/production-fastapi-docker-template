import type { $Fetch } from 'ofetch'
import type { TokenPair, TokenPairCodec } from './types'
import { validateJwtToken } from './utils'

export interface AuthUrls {
  login: string
  refresh: string
  register: string
  me: string
}

export type AuthOptions<T extends AppModel> = {
  urls: AuthUrls
  parseUser: (v: any) => T
  apiClient: $Fetch
  tokenPairCodec: TokenPairCodec
}

export const createAuthAppRepo = <T extends AppModel>(options: AuthOptions<T>) => {
  return () => {
    const api = new BaseApi({ resource: '', client: options.apiClient })

    const user: Ref<T | null> = ref(null)
    const loading: Ref<boolean> = ref(false)
    const tokens: Ref<TokenPair | null> = ref(null)

    const ensureTokenPair = async () => {
      const _processTokensResult = (tokens: TokenPair | null) => {
        return { success: !!tokens?.access, tokens }
      }
      if (!tokens.value) {
        tokens.value = options.tokenPairCodec.getFromStorage?.() || { access: null, refresh: null }
      }
      const accessData = validateJwtToken(tokens.value.access)
      if (accessData.isValid && accessData.expiresIn >= 60) return _processTokensResult(tokens.value)

      const refreshData = validateJwtToken(tokens.value.refresh)
      if (refreshData.isValid && refreshData.expiresIn >= 5) {
        try {
          return _processTokensResult(await refresh(refreshData.token!))
        } catch (e) {
          console.error(e)
        }
      }
      return _processTokensResult(null)
    }

    const me = async (params?: Record<string, any>): Promise<T | null> => {
      const { tokens } = await ensureTokenPair()
      if (!tokens?.access) throw new Error('Access token is not valid')
      loading.value = true
      try {
        const response = await api.send({
          method: 'get',
          action: options.urls.me,
          params,
        })
        user.value = options.parseUser(response)
        return user.value
      } catch (e) {
        console.error(e)
        throw new Error('Failed to load user')
      } finally {
        loading.value = false
      }
    }

    const login = async (data: any, config?: { me?: boolean }) => {
      loading.value = true
      try {
        const response = await api.send<Record<string, unknown>>({
          method: 'post',
          action: options.urls.login,
          data,
        })
        _processTokenPair(options.tokenPairCodec.decode(response))
        let userResult: T | null = null
        if (config?.me !== false) {
          userResult = await me()
        }
        return {
          tokens: tokens.value,
          raw: response,
          user: userResult,
        }
      } finally {
        loading.value = false
      }
    }

    const register = async (data: any) => {
      logout()
      loading.value = true
      try {
        await api.send({
          method: 'post',
          action: options.urls.register,
          data,
        })
        return await login(data)
      } finally {
        loading.value = false
      }
    }

    const refresh = async (token: string): Promise<TokenPair> => {
      const response = await api.send<Record<string, unknown>>({
        method: 'post',
        action: options.urls.refresh,
        data: { refresh: token },
      })
      return _processTokenPair(options.tokenPairCodec.decode(response))
    }

    const logout = () => {
      options.tokenPairCodec.setToStorage?.({ access: null, refresh: null })
      tokens.value = null
      user.value = null
    }

    const _processTokenPair = (tokenPair: TokenPair) => {
      tokens.value = tokenPair
      options.tokenPairCodec.setToStorage?.(tokens.value)
      return tokens.value
    }

    const state = {
      user,
      tokens,
      loading,
      // isAuthenticated,
    }

    const actions = {
      login,
      register,
      me,
      refresh,
      logout,
      ensureTokenPair,
    }

    return { state, actions }
  }
}
