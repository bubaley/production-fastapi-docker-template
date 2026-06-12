import { jwtDecode } from 'jwt-decode'
import type { AuthTokenStorage, JwtData, TokenPair, TokenValidationResult } from './types'

// Base implementation of AuthTokenStorage with common logic
abstract class BaseAuthTokenStorage implements AuthTokenStorage {
  // Abstract methods for storage operations - to be implemented by subclasses
  protected abstract _getItem(key: 'access' | 'refresh'): string | null
  protected abstract _setItem(key: 'access' | 'refresh', value: string): void
  protected abstract _removeItem(key: 'access' | 'refresh'): void

  getTokens(): TokenPair {
    return {
      access: this._getItem('access'),
      refresh: this._getItem('refresh'),
    }
  }

  setTokens(access: string | null, refresh: string | null): void {
    if (access) {
      this._setItem('access', access)
    } else {
      this._removeItem('access')
    }
    if (refresh) {
      this._setItem('refresh', refresh)
    } else {
      this._removeItem('refresh')
    }
  }

  removeTokens(): void {
    this._removeItem('access')
    this._removeItem('refresh')
  }

  removeToken(key: 'access' | 'refresh'): void {
    this._removeItem(key)
  }

  validateToken(token: string | null): TokenValidationResult {
    const data = this._getJwtData(token)
    if (!data) return { isValid: false, expiresIn: 0, token: null }
    const currentDate = (Date.now() / 1000) | 0
    return {
      isValid: currentDate < data.unixDate,
      expiresIn: data.unixDate - currentDate,
      token: token,
    }
  }

  isAccessTokenValid(): boolean {
    const token = this.getAccessToken()
    return this.validateToken(token).isValid
  }

  shouldRefreshToken(): boolean {
    const token = this.getAccessToken()
    const validation = this.validateToken(token)
    // Refresh if token expires in less than 60 seconds
    return validation.isValid && validation.expiresIn < 60
  }

  getAccessToken(): string | null {
    return this._getItem('access')
  }

  getRefreshToken(): string | null {
    return this._getItem('refresh')
  }

  private _getJwtData(token?: string | null): JwtData | null {
    if (!token) return null
    try {
      const result = jwtDecode<{ exp: number; user_id: number }>(token)
      return { user: result.user_id, unixDate: result.exp }
    } catch {
      return null
    }
  }
}

// LocalStorage implementation
export class AuthTokenLocalStorage extends BaseAuthTokenStorage {
  accessKey: string
  refreshKey: string

  constructor({ accessKey, refreshKey }: { accessKey: string; refreshKey: string }) {
    super()
    this.accessKey = accessKey
    this.refreshKey = refreshKey
  }

  protected _getItem(key: 'access' | 'refresh'): string | null {
    if (typeof window === 'undefined') return null
    return localStorage.getItem(key)
  }

  protected _setItem(key: 'access' | 'refresh', value: string): void {
    if (typeof window === 'undefined') return
    localStorage.setItem(key, value)
  }

  protected _removeItem(key: 'access' | 'refresh'): void {
    if (typeof window === 'undefined') return
    localStorage.removeItem(key)
  }
}

// Cookie implementation
export class AuthTokenCookieStorage extends BaseAuthTokenStorage {
  private readonly cookieOptions: {
    maxAge: number
    httpOnly: boolean
    secure: boolean
    sameSite: 'strict' | 'lax' | 'none'
  }

  constructor(options?: Partial<AuthTokenCookieStorage['cookieOptions']>) {
    super()
    this.cookieOptions = {
      maxAge: 60 * 60 * 24 * 7, // 7 days
      httpOnly: false, // tokens need to be accessible from client
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      ...options,
    }
  }

  protected _getItem(key: 'access' | 'refresh'): string | null {
    const cookie = useCookie<string | undefined>(key, {
      ...this.cookieOptions,
      default: () => undefined,
    })
    return cookie.value || null
  }

  protected _setItem(key: 'access' | 'refresh', value: string): void {
    const cookie = useCookie<string | undefined>(key, {
      ...this.cookieOptions,
      default: () => undefined,
    })
    cookie.value = value
  }

  protected _removeItem(key: 'access' | 'refresh'): void {
    const cookie = useCookie<string | undefined>(key, {
      ...this.cookieOptions,
      default: () => undefined,
    })
    cookie.value = undefined
  }
}
