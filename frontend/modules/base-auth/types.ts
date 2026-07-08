export interface UrlAction {
  url: string
  method: string
}
type _DeepPartial<T> = {
  [K in keyof T]?: T[K] extends object
    ? T[K] extends () => any
      ? T[K]
      : _DeepPartial<T[K]>
    : T[K] | undefined;
};


// Full interface with all required properties
export interface BaseAuthModuleOptions {
  /**
   * Base URL for authentication API
   * @default process.env.NUXT_PUBLIC_BASE_URL
   */
  originEnvKey: 'NUXT_PUBLIC_BASE_URL',

  /**
   * API prefix for auth routes
   * @default ''
   */
  apiPrefix: string

    /**
   * Nuxt API prefix for auth routes
   * @default '/api/auth'
   */
    nuxtApiPrefix: string

  /**
   * Authentication endpoints configuration
   */
  endpoints: {
    login: UrlAction
    logout: UrlAction
    refresh: UrlAction
    getSession: UrlAction
  }

  /**
   * Cookie configuration - keys for finding correct cookies
   */
  cookies: {
    /**
     * Access token cookie name
     * @default 'access_token'
     */
    accessToken: string
    /**
     * Refresh token cookie name
     * @default 'refresh_token'
     */
    refreshToken: string
  }

  /**
   * Session refresh configuration
   */
  sessionRefresh: {
    /**
     * Refresh before expiration (in seconds)
     * @default 300
     */
    beforeExpiry: number
    /**
     * Refresh interval (in seconds), 0 disables auto-refresh
     * @default 0
     */
    interval: number
  }

  /**
   * Disable server-side authentication middleware
   * @default false
   */
  disableServerSideAuth: boolean

  /**
   * Fetch session automatically after successful login
   * @default true
   */
  fetchSessionAfterLogin: boolean
}



// Optional interface for nuxt.config - all properties are optional
export type BaseAuthModuleConfig = _DeepPartial<BaseAuthModuleOptions>

export interface TokenInfo {
  expiresAt: number // in seconds
  expiresIn: number // in seconds
  isValid: boolean
}

export interface TokenPair {
  access?: TokenInfo
  refresh?: TokenInfo
}

export interface AuthError {
  data: unknown
  message?: string
  statusCode?: number
  statusMessage?: string
}

// Base session interface that can be extended via module augmentation
export interface Session {
  // Base session properties can be added here
  [key: string]: any
}

export interface AuthResponse<T = any> {
  data: T | null
  error: AuthError | null
  tokens?: TokenPair
  cookies?: string[]
}

export interface AuthActionResult<T = any> {
  data: T | null
  error: AuthError | null
  tokens: TokenPair
}

export interface AuthState<TSession = Session> {
  session: TSession | null
  tokens: TokenPair
  isLoading: boolean
  error: AuthError | null
  _tokensInitialized: boolean
}

declare module '@nuxt/schema' {
  interface NuxtConfig {
    baseAuth?: BaseAuthModuleConfig
  }
}
