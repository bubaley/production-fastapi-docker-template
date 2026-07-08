import type { AuthActionResult, AuthResponse, AuthState, Session } from '../../types'
import { getBaseAuthConfig } from '../utils/config-utils'
import { shouldRefresh } from '../utils/token-utils'

let intervalId: NodeJS.Timeout | null = null
const dateIntervalId: NodeJS.Timeout | null = null

export const useAuth = () => {
  // Cookies
  const requestCookie = useRequestHeader('cookie')
  const responseCookie = useResponseHeader('set-cookie')

  // State
  const config = getBaseAuthConfig()
  const state = useState<AuthState<Session>>('baseAuthState', () => ({
    session: null,
    tokens: {},
    isLoading: false,
    error: null,
    _tokensInitialized: false,
  }))

  const isAuthenticated = computed(() => !!state.value.session)

  // Intervals
  const startUpdateDate = () => {
    if (dateIntervalId) return
    // dateIntervalId = setInterval(() => {
    //   state.value.tokens.access = updateTokenInfo(state.value.tokens.access)
    //   state.value.tokens.refresh = updateTokenInfo(state.value.tokens.refresh)
    //   if (shouldRefresh(state.value.tokens)) refresh()
    // }, 1000)
  }

  const startAutoRefresh = () => {
    if (intervalId || !config.sessionRefresh.interval) return
    intervalId = setInterval(async () => {
      await refresh()
    }, config.sessionRefresh.interval * 1000)
  }

  if (import.meta.client) {
    startAutoRefresh()
    startUpdateDate()
  }

  // Base request
  const request = async <T = any>(endpoint: string, body?: any): Promise<AuthActionResult<T>> => {
    state.value.isLoading = true
    state.value.error = null

    let response: AuthResponse<T> | null = null
    try {
      const rawResponse = await $fetch.raw<AuthResponse<T>>(`${config.nuxtApiPrefix}${endpoint}`, {
        method: 'POST',
        body,
        credentials: 'include',
        headers: {
          cookie: requestCookie || '',
        },
      })
      response = rawResponse._data || null
      if (import.meta.server) {
        const responseCookies = rawResponse.headers.get('set-cookie') || ''
        if (responseCookies) responseCookie.value = responseCookies.split(',')
      }

    } finally {
      state.value.isLoading = false
    }
    if (!response) {
      return {
        data: null,
        error: {
          statusCode: 500,
          statusMessage: 'Internal Server Error',
          data: null,
        },
        tokens: {},
      }
    }
    if (response.tokens) {
      state.value.tokens = response.tokens
      state.value._tokensInitialized = true
    }
    state.value.error = response.error
    return {
      data: response.data,
      error: response.error,
      tokens: response.tokens || {},
    }
  }

  const loadTokensAsyncData = useAsyncData(
    'base-auth-load-tokens',
    async () => {
      return await request('/tokens')
    },
    { immediate: false }
  )

  const getSessionAsyncData = useAsyncData(
    'base-auth-session',
    async () => {
      const { tokens } = await getTokens()
      if (shouldRefresh(tokens, config.sessionRefresh.beforeExpiry)) await refresh()
      if (!state.value.tokens.access?.isValid) {
        return {
          data: null,
          error: 'Tokens are not valid',
          tokens: {},
        }
      }
      const response = await request<Session>('/session')
      if (response.data) {
        state.value.session = response.data
      }
      return response
    },
    { immediate: false }
  )

  // Async handler
  const _asyncHandler = async (asyncData: any) => {
    if (import.meta.client) {
      await asyncData.refresh()
      return asyncData.data.value
    }
    if (!asyncData.data.value) {
      await asyncData.execute()
    }
    return asyncData.data.value
  }

  // Expose actions
  const login = async (credentials: any): Promise<AuthActionResult> => {
    const response = await request('/login', credentials)
    if (config.fetchSessionAfterLogin && !response.error) {
      await getSession()
    }
    return response
  }

  const getTokens = async (): Promise<AuthActionResult> => {
    if (state.value._tokensInitialized)
      return {
        data: null,
        error: null,
        tokens: state.value.tokens,
      }
    return await _asyncHandler(loadTokensAsyncData)
  }

  const logout = async () => {
    const response = await request('/logout')
    if (response.error) return response
    state.value.session = null
    state.value.tokens = {}
    return response
  }

  const getSession = async (): Promise<AuthActionResult<Session>> => {
    return await _asyncHandler(getSessionAsyncData)
  }
  const refresh = async (): Promise<AuthActionResult> => {
    return await request('/refresh')
  }

  return {
    session: computed((): Session | null => state.value.session),
    isLoading: computed(() => state.value.isLoading),
    error: computed(() => state.value.error),
    _state: state,

    isAuthenticated,
    accessToken: computed(() => state.value.tokens.access),
    refreshToken: computed(() => state.value.tokens.refresh),
    shouldRefresh,

    fetchTokens: loadTokensAsyncData.refresh,

    login,
    logout,
    getSession,
    getTokens,
    refresh,
    // startAutoRefresh,
    // stopAutoRefresh,
  }
}
