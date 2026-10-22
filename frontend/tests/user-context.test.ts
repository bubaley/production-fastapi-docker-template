import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { computed, effectScope, proxyRefs, ref } from 'vue'
import { createAppRepo } from '../app/shared/toolkits/repo/appRepo'
import { AppApi } from '../app/shared/toolkits/repo/appApi'
import { createCodec } from '../app/shared/toolkits/repo/appModel'

beforeEach(() => {
  vi.stubGlobal('ref', ref)
  vi.stubGlobal('computed', computed)
  vi.stubGlobal('AppApi', AppApi)
  vi.stubGlobal('createCodec', createCodec)
})
afterEach(() => { vi.unstubAllGlobals(); vi.resetModules() })
const createRepo = (client = vi.fn().mockResolvedValue({ id: 'private' })) => {
  const { state, actions } = createAppRepo({
    resource: 'users', apiClient: client as never,
    codec: { decode: (v: unknown) => v, encode: (v: unknown) => v },
    paginationCodec: { decode: () => ({ page: 1, size: 50, total: 0, pages: 0, has_next: false }), encode: (v: unknown) => v },
  } as never)()
  return proxyRefs({ ...state, ...actions, organization: ref<unknown>(null) })
}
describe('user context reset', () => {
  it('resets all business repositories and setup on logout, and discards a previous account response', async () => {
    let resolve!: (value: { id: string }) => void
    const client = vi.fn().mockReturnValue(new Promise<{ id: string }>(yes => { resolve = yes }))
    const repos = { organization: createRepo(), organizationUser: createRepo(), user: createRepo(client), userToken: createRepo() }
    repos.organization.organization = { id: 'org-A' }
    for (const repo of Object.values(repos)) repo.items = [{ id: 'private' }] as never
    const setup = { organization: { id: 'org-A' } as unknown, restored: true }
    const reset = vi.fn(() => { setup.organization = null; setup.restored = false })
    const session = ref<{ id: string } | null>({ id: 'account-A' })
    vi.stubGlobal('useAuthRepo', () => ({}))
    vi.stubGlobal('useOrganizationRepo', () => repos.organization)
    vi.stubGlobal('useOrganizationUserRepo', () => repos.organizationUser)
    vi.stubGlobal('useUserRepo', () => repos.user)
    vi.stubGlobal('useUserTokenRepo', () => repos.userToken)
    const { useUserRepoReset } = await import('../app/shared/composables/useRepo')
    vi.stubGlobal('useUserRepoReset', useUserRepoReset)
    vi.stubGlobal('useSetupStore', () => ({ reset }))
    vi.stubGlobal('useAuth', () => ({ session }))
    const dismiss = vi.fn()
    vi.stubGlobal('useToast', () => ({ dismiss }))
    vi.stubGlobal('watch', (await import('vue')).watch)
    vi.stubGlobal('defineNuxtPlugin', (fn: unknown) => fn)
    const { default: plugin } = await import('../app/plugins/user-context')
    const scope = effectScope()
    scope.run(() => (plugin as () => void)())
    const pending = repos.user.retrieve('private')
    session.value = null
    expect(reset).toHaveBeenCalledOnce()
    expect(dismiss).toHaveBeenCalledOnce()
    expect(setup).toEqual({ organization: null, restored: false })
    for (const repo of Object.values(repos)) expect(repo.items).toEqual([])
    expect(repos.organization.organization).toBeNull()
    session.value = { id: 'account-B' }
    resolve({ id: 'private' })
    expect(await pending).toBeUndefined()
    expect(repos.user.item).toBeNull()
    scope.stop()
  })
  it('encodes token ownership only on creation, never on editing', async () => {
    const { userTokenCodec } = await import('../app/features/user/models/userToken')
    const token = userTokenCodec.decode({ user_id: 'user-A', name: 'Integration' })
    expect(userTokenCodec.encode(token)).toEqual({ user_id: 'user-A', name: 'Integration' })
    token.id = 'token-ID'
    expect(userTokenCodec.encode(token)).toEqual({ name: 'Integration' })
  })
})
