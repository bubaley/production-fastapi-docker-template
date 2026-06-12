import type { TokenPair, TokenPairCodec } from './types'

export interface StorageCodec {
  decodeAccessKey?: string | null
  decodeRefreshKey?: string | null
  storageAccessKey?: string | null
  storageRefreshKey?: string | null
}

export const decodeTokenPair = (
  data: Record<string, unknown>,
  accessKey?: string | null,
  refreshKey?: string | null
): TokenPair => {
  const access = data[accessKey || '']
  const refresh = data[refreshKey || '']
  return {
    access: typeof access === 'string' ? access : null,
    refresh: typeof refresh === 'string' ? refresh : null,
  }
}

export const createLocalStorageCodec = (options: StorageCodec): TokenPairCodec => {
  return {
    decode: (v: Record<string, unknown>): TokenPair => {
      return decodeTokenPair(v, options.decodeAccessKey, options.decodeRefreshKey)
    },
    setToStorage: (v: TokenPair) => {
      const _processToken = (token?: string | null, key?: string | null) => {
        if (key) {
          if (token) localStorage.setItem(key, token)
          else localStorage.removeItem(key)
        }
      }
      _processToken(v.access, options.storageAccessKey)
      _processToken(v.refresh, options.storageRefreshKey)
    },
    getFromStorage: (): TokenPair => {
      return {
        access: localStorage.getItem(options.decodeAccessKey || '') || null,
        refresh: localStorage.getItem(options.decodeRefreshKey || '') || null,
      }
    },
  }
}

export const createCookieCodec = (options: StorageCodec): TokenPairCodec => {
  return {
    decode: (v: Record<string, unknown>): TokenPair => {
      return decodeTokenPair(v, options.decodeAccessKey, options.decodeRefreshKey)
    },
    getFromStorage: () => {
      return {
        access: useCookie(options.decodeAccessKey || '').value || null,
        refresh: useCookie(options.decodeRefreshKey || '').value || null,
      }
    },
  }
}
