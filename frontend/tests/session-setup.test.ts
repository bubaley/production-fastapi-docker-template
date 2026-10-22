import { afterEach, beforeEach, describe, expect, it, vi } from 'vite-plus/test'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { defineComponent, h } from 'vue'
import { useSetupStore } from '../app/shared/stores/useSetupStore'
import { SESSION_KEY, ensureSession } from '../app/shared/composables/useSession'
import { ApiError } from '../app/shared/api/client'
import { safeRedirect } from '../app/shared/utils/redirect'
import { installColada } from './colada'
import { useQueryCache } from '@pinia/colada'

const orgA = { id: 'a', name: 'A', key: 'a' }
const orgB = { id: 'b', name: 'B', key: 'b' }

beforeEach(() => {
  localStorage.clear()
  setActivePinia(createPinia())
})
afterEach(() => vi.unstubAllGlobals())

describe('organization selection', () => {
  it('restores the stored organization of the same user from the session', async () => {
    localStorage.setItem('setup:state', JSON.stringify({ userId: 'u1', organization: 'b' }))
    const store = useSetupStore()
    await store.restore({ userId: 'u1', organizations: [orgA, orgB] })
    expect(store.state.organization).toEqual(orgB)
    expect(store.state.restored).toBe(true)
  })

  it('ignores a selection stored by another account', async () => {
    localStorage.setItem('setup:state', JSON.stringify({ userId: 'u1', organization: 'b' }))
    const retrieve = vi.fn()
    const store = useSetupStore()
    await store.restore({ userId: 'u2', organizations: [orgA, orgB], retrieve })
    expect(store.state.organization).toBeNull()
    expect(retrieve).not.toHaveBeenCalled()
  })

  it('selects the only membership and loads a stored non-member organization (superuser)', async () => {
    const store = useSetupStore()
    await store.restore({ userId: 'u1', organizations: [orgA] })
    expect(store.state.organization).toEqual(orgA)
    store.state.organization = orgB
    await flushPromises()
    expect(JSON.parse(localStorage.getItem('setup:state')!)).toEqual({ userId: 'u1', organization: 'b' })
    const next = (setActivePinia(createPinia()), useSetupStore())
    const retrieve = vi.fn().mockResolvedValue(orgB)
    await next.restore({ userId: 'u1', organizations: [orgA], retrieve })
    expect(retrieve).toHaveBeenCalledWith('b')
    expect(next.state.organization).toEqual(orgB)
  })

  it('forgets the selection on sign-out', async () => {
    const store = useSetupStore()
    await store.restore({ userId: 'u1', organizations: [orgA] })
    store.reset()
    expect(store.state.organization).toBeNull()
    expect(localStorage.getItem('setup:state')).toBeNull()
  })
})

describe('session for route guards', () => {
  const withCache = async (authMe: (request: Request) => Response) => {
    const plugins = installColada()
    let cache!: ReturnType<typeof useQueryCache>
    let result: unknown
    const client = (await import('../app/shared/api/client')).createApiClient({
      baseUrl: 'http://app.test',
      fetch: (async (request: Request) => authMe(request)) as typeof fetch,
    })
    vi.stubGlobal('useNuxtApp', () => ({ $api: client }))
    const wrapper = mount(
      defineComponent({
        setup() {
          cache = useQueryCache()
          return () => h('div')
        },
      }),
      { global: { plugins: plugins as never } },
    )
    return {
      cache,
      wrapper,
      ensure: async () => {
        result = await wrapper.vm.$.appContext.app.runWithContext(() => ensureSession())
        return result
      },
    }
  }

  it('treats 401 as signed out and re-checks a cached sign-out', async () => {
    const authMe = vi.fn(() => new Response('{}', { status: 401 }))
    const { ensure, wrapper } = await withCache(authMe)
    expect(await ensure()).toBeNull()
    expect(await ensure()).toBeNull()
    expect(authMe).toHaveBeenCalledTimes(2)
    wrapper.unmount()
  })

  it('caches a signed-in session', async () => {
    const session = { user: { id: 'u1' }, organizations: [] }
    const authMe = vi.fn(
      () => new Response(JSON.stringify(session), { status: 200, headers: { 'Content-Type': 'application/json' } }),
    )
    const { ensure, cache, wrapper } = await withCache(authMe)
    expect(await ensure()).toEqual(session)
    expect(await ensure()).toEqual(session)
    expect(authMe).toHaveBeenCalledTimes(1)
    expect(cache.getQueryData([...SESSION_KEY])).toEqual(session)
    wrapper.unmount()
  })

  it('keeps redirects on this site', () => {
    expect(safeRedirect('/settings/users')).toBe('/settings/users')
    expect(safeRedirect('//evil.example')).toBeNull()
    expect(safeRedirect('https://evil.example')).toBeNull()
    expect(safeRedirect(['/a'])).toBeNull()
    expect(new ApiError(401, {}).status).toBe(401)
  })
})
