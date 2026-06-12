import { getBaseAuthConfig } from './../../utils/config-utils'
import type { H3Event } from 'h3'
import type { FetchResponse, FetchError } from 'ofetch'
import type { AuthError, AuthResponse, BaseAuthModuleOptions } from '../../../types'
import { parseToken } from '../../utils/token-utils'

export class AuthClient {
  private config: BaseAuthModuleOptions = getBaseAuthConfig()

  // Utils
  private getTokenPair(event: H3Event, cookies?: string[]) {
    const { cookies: cookieConfig } = this.config

    return {
      access: parseToken(getCookieValue(cookieConfig.accessToken || 'access_token', event, cookies)),
      refresh: parseToken(getCookieValue(cookieConfig.refreshToken || 'refresh_token', event, cookies)),
    }
  }

  private setCookiesFromResponse(event: H3Event, response: FetchResponse<any>) {
    const setCookies = response.headers.getSetCookie()
    for (const cookie of setCookies) {
      appendHeader(event, 'set-cookie', cookie)
    }
    return setCookies
  }

  // Request
  private async request(attrs: {
    event: H3Event
    method: string
    endpoint: string
    body?: any
    cookie?: string[]
  }): Promise<AuthResponse> {
    const options: any = {
      method: attrs.method,
      timeout: 3000,
      headers: {
        cookie: attrs.cookie?.join('; ') || attrs.event.node.req.headers.cookie || '',
      },
    }
    if (attrs.body) options.body = attrs.body

    let cookies: string[] = []
    let data: any = null
    let error: AuthError | null = null
    try {

      const baseUrl = useRuntimeConfig().public.baseUrl
      const response = await $fetch.raw(
        this._normalizeUrl(baseUrl, this.config.apiPrefix, attrs.endpoint),
        options,
      )
      cookies = this.setCookiesFromResponse(attrs.event, response).concat(attrs.cookie || [])
      data = response._data
    } catch (err) {
      const e = err as FetchError
      error = {
        statusCode: e.statusCode,
        statusMessage: e.statusMessage,
        data: e.data,
      }
    }

    return {
      data,
      error,
      tokens: this.getTokenPair(attrs.event, cookies),
      cookies,
    }
  }

  // Actions
  async login(event: H3Event, credentials: any): Promise<AuthResponse> {
    const { login } = this.config.endpoints
    return this.request({ event, method: login.method, endpoint: login.url, body: credentials })
  }

  async logout(event: H3Event): Promise<AuthResponse> {
    const { logout } = this.config.endpoints
    return this.request({ event, method: logout.method, endpoint: logout.url })
  }

  async getTokens(event: H3Event): Promise<AuthResponse> {
    const tokenPair = this.getTokenPair(event)
    return {
      tokens: tokenPair,
      data: null,
      error: null,
    }
  }

  async getSession(event: H3Event): Promise<AuthResponse> {
    const tokenPair = this.getTokenPair(event)
    let refreshResponse: AuthResponse | null = null

    if (!tokenPair.access?.isValid && tokenPair.refresh?.isValid) {
      refreshResponse = await this.refresh(event)
    }

    const { getSession } = this.config.endpoints
    return this.request({
      event,
      method: getSession.method,
      endpoint: getSession.url,
      cookie: refreshResponse?.cookies,
    })
  }

  async refresh(event: H3Event): Promise<AuthResponse> {
    const { refresh } = this.config.endpoints
    return this.request({ event, method: refresh.method, endpoint: refresh.url })
  }

  private _normalizeUrl(baseUrl?: unknown, ...append: unknown[]) {
    const url =
      [baseUrl, ...append]
        .map((v) => (typeof v === 'string' ? v.replace(/^\/+|\/+$/g, '') : null))
        .filter((v) => v)
        .join('/') || '/'
    if (baseUrl) return url
    return url.startsWith('/') ? url : `/${url}`
  }
}

// Singleton
let authClientInstance: AuthClient | null = null

export function createAuthClient(): AuthClient {
  if (!authClientInstance) {
    authClientInstance = new AuthClient()
  }
  return authClientInstance
}

export const useAuthClient = () => createAuthClient()
