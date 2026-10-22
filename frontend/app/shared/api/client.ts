import { authRefresh } from './generated'
import { createClient, createConfig, type Client } from './generated/client'

export type ApiClient = Client

type ErrorEnvelope = { error?: { code?: string; message?: string; details?: Record<string, unknown> } }

/** Every failed request rejects with this: HTTP status plus the backend error envelope (`ErrorResponse`). */
export class ApiError extends Error {
  readonly status: number
  readonly code?: string
  readonly details?: Record<string, unknown>
  readonly body: unknown

  constructor(status: number, body: unknown) {
    const envelope = (typeof body === 'object' && body !== null ? body : {}) as ErrorEnvelope
    const message =
      envelope.error?.message ||
      (body instanceof Error ? body.message : typeof body === 'string' && body ? body : `HTTP ${status}`)
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = envelope.error?.code
    this.details = envelope.error?.details
    this.body = body
  }
}

export const isApiError = (error: unknown, status?: number): error is ApiError =>
  error instanceof ApiError && (status === undefined || error.status === status)

// 401 from these means "wrong credentials" or "signed out", never "access cookie expired".
const NO_REFRESH_PATHS = new Set(['/api/v1/auth/login', '/api/v1/auth/refresh', '/api/v1/auth/logout'])

export type AuthFetchOptions = {
  fetch: typeof fetch
  /** Resolves to true when the session was renewed (`POST /auth/refresh` → 200). */
  refresh: () => Promise<boolean>
  /** Called when the refresh failed: the session is gone. */
  onSignedOut?: () => void
}

/**
 * Wraps fetch: a 401 triggers one `POST /auth/refresh` shared by every request that fails meanwhile
 * (single flight), then the request is replayed once. A request that was sent before another request's
 * refresh finished is replayed without a second refresh.
 */
export const createAuthFetch = ({ fetch: baseFetch, refresh, onSignedOut }: AuthFetchOptions): typeof fetch => {
  let pending: Promise<boolean> | null = null
  let generation = 0
  const refreshOnce = () => {
    pending ??= refresh()
      .catch(() => false)
      .then((ok) => {
        if (ok) generation++
        return ok
      })
      .finally(() => {
        pending = null
      })
    return pending
  }
  return (async (input: RequestInfo | URL, init?: RequestInit) => {
    const request = new Request(input, init)
    const replay = request.clone()
    const sentAt = generation
    const response = await baseFetch(request)
    if (response.status !== 401 || NO_REFRESH_PATHS.has(new URL(request.url).pathname)) return response
    const renewed = sentAt !== generation || (await refreshOnce())
    if (!renewed) {
      onSignedOut?.()
      return response
    }
    return baseFetch(replay)
  }) as typeof fetch
}

export type ApiClientOptions = {
  /** `''` in the browser (same origin, `/api/v1/...`), the internal API origin during SSR. */
  baseUrl: string
  /** Headers added to every request, read at request time (`Organization-Key`, the forwarded `cookie` on SSR). */
  headers?: () => Record<string, string | null | undefined>
  /** Refresh-and-retry on 401. Browser only: during SSR a 401 means "render signed out". */
  refreshOnUnauthorized?: boolean
  onSignedOut?: () => void
  fetch?: typeof fetch
}

export const createApiClient = (options: ApiClientOptions): ApiClient => {
  const baseFetch = options.fetch ?? ((...args: Parameters<typeof fetch>) => globalThis.fetch(...args))
  const client = createClient(createConfig({ baseUrl: options.baseUrl, credentials: 'same-origin' }))
  if (options.refreshOnUnauthorized) {
    client.setConfig({
      fetch: createAuthFetch({
        fetch: baseFetch,
        refresh: async () => (await authRefresh({ client, fetch: baseFetch })).response?.ok ?? false,
        onSignedOut: options.onSignedOut,
      }),
    })
  } else {
    client.setConfig({ fetch: baseFetch })
  }
  client.interceptors.request.use((request) => {
    for (const [name, value] of Object.entries(options.headers?.() ?? {})) {
      if (value) request.headers.set(name, value)
    }
    return request
  })
  client.interceptors.error.use((error, response) =>
    error instanceof ApiError ? error : new ApiError(response?.status ?? 0, error),
  )
  return client
}
