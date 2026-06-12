import type { TokenInfo, TokenPair } from '../../types'

export const decodeJWT = (token?: string | null): any => {
  if (!token) return null
  try {
    const parts = token.split('.')
    if (parts.length !== 3) return null
    const payload = parts[1] || ''
    return JSON.parse(Buffer.from(payload.replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString())
  } catch {
    return null
  }
}

export const parseToken = (token?: string | null): TokenInfo | undefined => {
  const decoded = decodeJWT(token)
  if (!decoded?.exp) return undefined
  const now = Math.floor(Date.now() / 1000)
  const expiresAt = decoded.exp
  const expiresIn = Math.max(0, expiresAt - now)
  return {
    expiresAt: expiresAt,
    expiresIn: expiresIn,
    isValid: expiresIn > 0,
  }
}

export const updateTokenInfo = (tokenInfo?: TokenInfo | null): TokenInfo | undefined => {
  if (!tokenInfo) return undefined
  const expiresAt = new Date((tokenInfo?.expiresAt || 0) * 1000)
  const expiresIn = Math.max(expiresAt.getTime() - new Date().getTime(), 0)
  return {
    ...tokenInfo,
    expiresIn,
    isValid: expiresIn > 0,
  }
}

export const shouldRefresh = (tokenPair: TokenPair, refreshBeforeExpiry: number = 300) => {
  const expiresIn = tokenPair.access?.expiresIn || 0
  const _refreshBeforeExpiry = refreshBeforeExpiry * 1000
  return expiresIn < _refreshBeforeExpiry && tokenPair.refresh?.isValid
}
