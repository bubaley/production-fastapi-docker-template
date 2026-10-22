import { afterEach, describe, expect, it, vi } from 'vite-plus/test'
import { flushPromises, mount } from '@vue/test-utils'
import { useQueryCache } from '@pinia/colada'
import { defineComponent, h } from 'vue'
import { defineResource, fetchPage, resourceKeys, saveItem } from '../app/shared/api/resource'
import { useResourceMutations } from '../app/shared/api/useResource'
import { organizationUserResource } from '../app/features/organization/resources/organizationUser'
import { installColada } from './colada'

type Item = { id: string; name: string; key: string }
const createResource = (sdk: Record<string, ReturnType<typeof vi.fn>>) =>
  defineResource({
    key: 'things',
    sdk: sdk as never,
    toForm: (item?: Partial<Item>) => ({ id: item?.id ?? null, name: item?.name ?? '', key: item?.key ?? '' }),
    toCreate: (form) => ({ name: form.name, key: form.key }) as never,
    toUpdate: (form) => ({ name: form.name }) as never,
    invalidates: ['session'],
  })

afterEach(() => vi.unstubAllGlobals())

describe('resource descriptor', () => {
  it('keys lists and details under the resource root', () => {
    const keys = resourceKeys({ key: 'organizations' })
    expect(keys.all).toEqual(['organizations'])
    expect(keys.list({ name: 'a' })).toEqual(['organizations', 'list', { name: 'a' }])
    expect(keys.detail('id-1')).toEqual(['organizations', 'id-1'])
  })

  it('sends page and page_size and ends on an empty page', async () => {
    const list = vi.fn().mockResolvedValue({ data: { data: [], meta: { page: 3, has_next: true } } })
    const result = await fetchPage(createResource({ list }), {} as never, { name: 'a' }, 3, 20)
    expect(list.mock.calls[0]![0].query).toEqual({ name: 'a', page: 3, page_size: 20 })
    expect(result).toEqual({ items: [], hasNext: false })
  })

  it('creates without an id and updates with one, mapping the form to each body', async () => {
    const create = vi.fn().mockResolvedValue({ data: { id: 'new', name: 'A', key: 'a' } })
    const update = vi.fn().mockResolvedValue({ data: { id: 'x', name: 'B', key: 'a' } })
    const resource = createResource({ create, update })
    expect(await saveItem(resource, {} as never, { id: null, name: 'A', key: 'a' })).toMatchObject({ created: true })
    expect(create.mock.calls[0]![0].body).toEqual({ name: 'A', key: 'a' })
    expect(await saveItem(resource, {} as never, { id: 'x', name: 'B', key: 'a' })).toMatchObject({ created: false })
    expect(update.mock.calls[0]![0]).toMatchObject({ path: { item_id: 'x' }, body: { name: 'B' } })
  })

  it('adds members to the organization in the form, not the selected one', () => {
    const form = organizationUserResource.toForm({ organization_id: 'viewed-org' })
    expect(() => organizationUserResource.toCreate!(form)).toThrow()
    form.user = { id: 'user-1' } as never
    expect(organizationUserResource.toCreate!(form)).toEqual({ organization_id: 'viewed-org', user_id: 'user-1' })
  })
})

describe('resource mutations', () => {
  const run = async (sdk: Record<string, ReturnType<typeof vi.fn>>) => {
    let api!: ReturnType<typeof useResourceMutations> & { cache: ReturnType<typeof useQueryCache> }
    const resource = createResource(sdk)
    const wrapper = mount(
      defineComponent({
        setup() {
          api = { ...useResourceMutations(resource), cache: useQueryCache() }
          return () => h('div')
        },
      }),
      { global: { plugins: installColada() as never } },
    )
    const seed = (key: readonly unknown[]) => {
      const entry = api.cache.ensure({ key: [...key], query: async () => 'fresh' })
      api.cache.setQueryData([...key], 'cached')
      return entry
    }
    return { api, seed, wrapper }
  }

  it('stores the saved record and invalidates lists and related roots, not that record', async () => {
    const update = vi.fn().mockResolvedValue({ data: { id: 'x', name: 'B', key: 'k' } })
    const { api, seed, wrapper } = await run({ update })
    const list = seed(['things', 'list', {}])
    const other = seed(['things', 'y'])
    const saved = seed(['things', 'x'])
    const session = seed(['session'])
    const unrelated = seed(['users', 'list', {}])
    await api.save.mutateAsync({ id: 'x', name: 'B', key: 'k' })
    await flushPromises()
    expect(api.cache.getQueryData(['things', 'x'])).toEqual({ id: 'x', name: 'B', key: 'k' })
    expect([list, other, session].map((entry) => entry.stale)).toEqual([true, true, true])
    expect(saved.stale).toBe(false)
    expect(unrelated.stale).toBe(false)
    wrapper.unmount()
  })

  it('does not refetch the detail of a deleted record', async () => {
    const destroy = vi.fn().mockResolvedValue({ data: undefined })
    const { api, seed, wrapper } = await run({ destroy })
    const list = seed(['things', 'list', {}])
    const removed = seed(['things', 'x'])
    await api.remove.mutateAsync('x')
    await flushPromises()
    expect(destroy.mock.calls[0]![0].path).toEqual({ item_id: 'x' })
    expect(list.stale).toBe(true)
    expect(removed.stale).toBe(false)
    wrapper.unmount()
  })
})
