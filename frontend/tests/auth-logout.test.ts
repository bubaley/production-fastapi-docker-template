import { afterEach, describe, expect, it, vi } from 'vitest'
import { computed, ref } from 'vue'
import { useAuth } from '../modules/base-auth/runtime/composables/useAuth'
vi.mock('../modules/base-auth/runtime/utils/config-utils', () => ({
  getBaseAuthConfig: () => ({ nuxtApiPrefix: '/api/auth', sessionRefresh: { interval: 0, beforeExpiry: 0 }, fetchSessionAfterLogin: true }),
}))
afterEach(() => vi.unstubAllGlobals())
describe('logout authentication state', () => {
  it('does not restore tokens or session from responses started before logout', async () => {
    const tokens = { access: { isValid: true, expiresIn: 3600 }, refresh: { isValid: true, expiresIn: 7200 } }
    const authState = ref({ session: { id: 'account-A' }, tokens, _tokensInitialized: true, isLoading: false, error: null })
    const states = new Map<string, unknown>([['baseAuthState', authState]])
    vi.stubGlobal('useState', (key: string, initial: () => unknown) => {
      if (!states.has(key)) states.set(key, ref(initial()))
      return states.get(key)
    })
    vi.stubGlobal('computed', computed)
    vi.stubGlobal('useRequestHeader', () => undefined)
    vi.stubGlobal('useResponseHeader', () => ref())
    vi.stubGlobal('useAsyncData', (_key: string, handler: () => Promise<unknown>) => {
      const data = ref()
      const execute = async () => { data.value = await handler() }
      return { data, execute, refresh: execute }
    })
    let resolveSession!: (value: unknown) => void
    let resolveRefresh!: (value: unknown) => void
    const raw = vi.fn((url: string) => {
      if (url.endsWith('/session')) return new Promise(yes => { resolveSession = yes })
      if (url.endsWith('/refresh')) return new Promise(yes => { resolveRefresh = yes })
      return Promise.resolve({ _data: { data: null, error: null, tokens: {} } })
    })
    vi.stubGlobal('$fetch', { raw })
    const auth = useAuth()
    const sessionRequest = auth.getSession()
    await Promise.resolve()
    const refreshRequest = auth.refresh()
    await auth.logout()
    expect(auth.session.value).toBeNull()
    expect(auth._state.value._tokensInitialized).toBe(false)
    resolveSession({ _data: { data: { id: 'account-A' }, error: null, tokens } })
    resolveRefresh({ _data: { data: null, error: null, tokens } })
    await Promise.all([sessionRequest, refreshRequest])
    expect(auth.session.value).toBeNull()
    expect(auth._state.value.tokens).toEqual({})
  })
})
