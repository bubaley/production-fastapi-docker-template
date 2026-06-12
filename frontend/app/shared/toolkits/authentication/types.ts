export interface TokenPair {
  access: string | null
  refresh: string | null
}

export type TokenPairCodec = {
  decode: (v: Record<string, unknown>) => TokenPair
  setToStorage?: (v: TokenPair) => void
  getFromStorage?: () => TokenPair
}

export interface TokenValidationResult {
  isValid: boolean
  expiresIn: number
  token: string | null
}

export interface AuthTokenStorage {
  // High-level token management methods
  getTokens(): TokenPair
  setTokens(access: string | null, refresh: string | null): void
  removeTokens(): void
  removeToken(key: 'access' | 'refresh'): void

  // Token validation methods
  validateToken(token: string | null): TokenValidationResult
  isAccessTokenValid(): boolean
  shouldRefreshToken(): boolean

  // Token getters
  getAccessToken(): string | null
  getRefreshToken(): string | null
}

export interface JwtData {
  user: number
  unixDate: number
}
