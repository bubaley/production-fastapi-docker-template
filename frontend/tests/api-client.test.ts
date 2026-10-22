import { describe, expect, it, vi } from 'vite-plus/test'
import { ApiError, createApiClient, createAuthFetch, isApiError } from '../app/shared/api/client'
import { organizationsCreate, organizationsList } from '../app/shared/api/generated'

const json = (status: number, body: unknown = {}) =>
  new Response(status === 204 ? null : JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
const deferred = <T>() => {
  let resolve!: (value: T) => void
  const promise = new Promise<T>((done) => {
    resolve = done
  })
  return { promise, resolve }
}
const url = (path: string) => `http://app.test${path}`

describe('401 refresh and retry', () => {
  it('refreshes once for concurrent 401s and replays every request', async () => {
    const refreshed = deferred<boolean>()
    let session = 'old'
    const base = vi.fn(async (request: Request) => (session === 'new' ? json(200, { path: request.url }) : json(401)))
    const refresh = vi.fn(async () => {
      const ok = await refreshed.promise
      session = 'new'
      return ok
    })
    const authFetch = createAuthFetch({ fetch: base as typeof fetch, refresh })
    const first = authFetch(url('/api/v1/organizations'))
    const second = authFetch(url('/api/v1/users'), { method: 'POST', body: '{"a":1}' })
    await vi.waitFor(() => expect(refresh).toHaveBeenCalledTimes(1))
    refreshed.resolve(true)
    const responses = await Promise.all([first, second])
    expect(responses.map((response) => response.status)).toEqual([200, 200])
    expect(refresh).toHaveBeenCalledTimes(1)
    // The replayed POST still has its body.
    const replayedPost = base.mock.calls.map(([request]) => request).filter((request) => request.method === 'POST')
    expect(await replayedPost.at(-1)!.text()).toBe('{"a":1}')
  })

  it('replays a request that failed after another request already refreshed', async () => {
    const late = deferred<Response>()
    let calls = 0
    const base = vi.fn(async (request: Request) => {
      calls++
      if (request.url.endsWith('/slow') && calls <= 2) return late.promise
      return calls <= 2 ? json(401) : json(200)
    })
    const refresh = vi.fn(async () => true)
    const authFetch = createAuthFetch({ fetch: base as typeof fetch, refresh })
    const slow = authFetch(url('/api/v1/slow'))
    expect((await authFetch(url('/api/v1/fast'))).status).toBe(200)
    late.resolve(json(401))
    expect((await slow).status).toBe(200)
    expect(refresh).toHaveBeenCalledTimes(1)
  })

  it('signs out when the refresh fails and returns the original 401', async () => {
    const onSignedOut = vi.fn()
    const authFetch = createAuthFetch({
      fetch: (async () => json(401)) as typeof fetch,
      refresh: async () => false,
      onSignedOut,
    })
    expect((await authFetch(url('/api/v1/auth/me'))).status).toBe(401)
    expect(onSignedOut).toHaveBeenCalledTimes(1)
  })

  it('never refreshes for login, refresh or logout', async () => {
    const refresh = vi.fn(async () => true)
    const authFetch = createAuthFetch({ fetch: (async () => json(401)) as typeof fetch, refresh })
    for (const path of ['/api/v1/auth/login', '/api/v1/auth/refresh', '/api/v1/auth/logout']) {
      expect((await authFetch(url(path), { method: 'POST' })).status).toBe(401)
    }
    expect(refresh).not.toHaveBeenCalled()
  })
})

describe('generated client wiring', () => {
  it('adds per-request headers, uses the base URL and rejects with ApiError', async () => {
    const seen: Request[] = []
    let key: string | undefined = 'org-a'
    const client = createApiClient({
      baseUrl: 'http://api.internal:8000',
      headers: () => ({ 'Organization-Key': key, cookie: 'access_token=x' }),
      fetch: (async (request: Request) => {
        seen.push(request)
        return request.method === 'POST'
          ? json(422, { data: null, success: false, error: { code: 'VALIDATION_ERROR', message: 'Bad key' } })
          : json(200, { data: [], meta: { page: 1, page_size: 50, has_next: false } })
      }) as typeof fetch,
    })
    const { data } = await organizationsList({ client, throwOnError: true, query: { name: 'a' } })
    expect(data.data).toEqual([])
    expect(seen[0]!.url).toBe('http://api.internal:8000/api/v1/organizations?name=a')
    expect(seen[0]!.headers.get('Organization-Key')).toBe('org-a')
    expect(seen[0]!.headers.get('cookie')).toBe('access_token=x')
    key = undefined
    const error = await organizationsCreate({ client, throwOnError: true, body: { name: 'A', key: 'a' } }).catch(
      (reason) => reason,
    )
    expect(seen[1]!.headers.has('Organization-Key')).toBe(false)
    expect(error).toBeInstanceOf(ApiError)
    expect(isApiError(error, 422)).toBe(true)
    expect(error).toMatchObject({ status: 422, code: 'VALIDATION_ERROR', message: 'Bad key' })
  })

  it('refreshes through POST /api/v1/auth/refresh in the browser mode', async () => {
    const paths: string[] = []
    let renewed = false
    const client = createApiClient({
      baseUrl: 'http://app.test',
      refreshOnUnauthorized: true,
      fetch: (async (request: Request) => {
        const path = new URL(request.url).pathname
        paths.push(`${request.method} ${path}`)
        if (path === '/api/v1/auth/refresh') {
          renewed = true
          return json(200, { access_expires_at: '', refresh_expires_at: '' })
        }
        return renewed ? json(200, { data: [], meta: {} }) : json(401)
      }) as typeof fetch,
    })
    await organizationsList({ client, throwOnError: true })
    expect(paths).toEqual(['GET /api/v1/organizations', 'POST /api/v1/auth/refresh', 'GET /api/v1/organizations'])
  })
})
