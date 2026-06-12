import { jwtDecode } from 'jwt-decode'
import type { JwtData, TokenValidationResult } from './types'

export const validateJwtToken = (token: string | null): TokenValidationResult => {
  const data = _getJwtData(token)
  if (!data) return { isValid: false, expiresIn: 0, token: null }
  const currentDate = (Date.now() / 1000) | 0
  return {
    isValid: currentDate < data.unixDate,
    expiresIn: data.unixDate - currentDate,
    token: token,
  }
}

const _getJwtData = (token?: string | null): JwtData | null => {
  if (!token) return null
  try {
    const result = jwtDecode<{ exp: number; user_id: number }>(token)
    return { user: result.user_id, unixDate: result.exp }
  } catch {
    return null
  }
}
