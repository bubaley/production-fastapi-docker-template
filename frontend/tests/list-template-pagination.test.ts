import { afterEach, describe, expect, it, vi } from 'vite-plus/test'
import { flushPromises, mount } from '@vue/test-utils'
import AppListToolbar from '../app/shared/ui/app/AppListToolbar.vue'
import AppPage from '../app/shared/ui/app/AppPage.vue'
import AppListTemplate from '../app/shared/ui/template/AppListTemplate.vue'
import { defineResource } from '../app/shared/api/resource'
import { installColada } from './colada'

type Row = { id: string }
const page = (query: Record<string, unknown>) => {
  const number = Number(query.page)
  return {
    data: {
      data: Array.from({ length: 50 }, (_, index) => ({ id: String((number - 1) * 50 + index + 1) })),
      meta: { page: number, page_size: 50, has_next: number < 10 },
    },
  }
}
const createResource = (list: (options: { query?: Record<string, unknown> }) => Promise<unknown>) =>
  defineResource({
    key: 'rows',
    sdk: { list: list as never },
    toForm: (item?: Partial<Row>) => ({ id: item?.id ?? null }),
  })

afterEach(() => vi.unstubAllGlobals())
const createList = (resource: unknown, props = {}, slots = {}) => {
  const plugins = installColada()
  vi.stubGlobal('useRouter', () => ({ push: vi.fn() }))
  return mount(AppListTemplate, {
    props: { resource: resource as never, ...props },
    slots,
    global: {
      plugins: plugins as never,
      components: { AppPage },
      stubs: {
        AppInput: {
          props: ['modelValue'],
          emits: ['update:modelValue'],
          template: '<input :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />',
        },
        AppTitle: true,
        AppBackButton: true,
        AppList: {
          name: 'AppList',
          props: ['items', 'infiniteScroll', 'hasNextPage'],
          emits: ['loadMore'],
          template:
            '<div><span v-for="item in items" :key="item.id">{{ item.id }}</span><button @click="$emit(\'loadMore\')">Ещё</button></div>',
        },
        AppButton: true,
        AppModal: true,
        AppDetailTemplate: true,
      },
    },
  })
}
const lastQuery = (list: ReturnType<typeof vi.fn>) => (list.mock.calls.at(-1)![0] as { query: object }).query

describe('list template on a resource', () => {
  it('keeps search outside the scrolling body and queries the search param from page 1', async () => {
    const list = vi.fn(async ({ query = {} }: { query?: Record<string, unknown> }) =>
      query.name ? { data: { data: [{ id: '500' }], meta: { page: 1, has_next: false } } } : page(query),
    )
    const wrapper = createList(
      createResource(list),
      { searchParam: 'name', debounce: 0 },
      { filters: '<div data-test="filters">Фильтры</div>' },
    )
    await flushPromises()
    expect(wrapper.get('main').find('input').exists()).toBe(false)
    expect(wrapper.find('[data-test="filters"]').exists()).toBe(true)
    expect(wrapper.findComponent({ name: 'AppList' }).classes()).toContain('-mx-3')
    await wrapper.get('input').setValue('500')
    await flushPromises()
    expect(lastQuery(list)).toEqual({ name: '500', page: 1, page_size: 50 })
    expect(wrapper.findComponent({ name: 'AppList' }).props('items')).toEqual([{ id: '500' }])
    wrapper.unmount()
  })

  it('merges filters with extra params and starts again from page 1 when they change', async () => {
    const list = vi.fn(async ({ query = {} }: { query?: Record<string, unknown> }) => page(query))
    const wrapper = createList(createResource(list), { debounce: 0, extraParams: { organization_id: 'scope' } })
    await flushPromises()
    await wrapper.get('button').trigger('click')
    await flushPromises()
    expect(wrapper.findAll('span')).toHaveLength(100)
    wrapper.findComponent(AppListToolbar).vm.$emit('update:filters', { key: 'sample', active: false })
    await flushPromises()
    expect(lastQuery(list)).toEqual({ key: 'sample', active: false, organization_id: 'scope', page: 1, page_size: 50 })
    expect(wrapper.findAll('span')).toHaveLength(50)
    wrapper.unmount()
  })

  it('appends 500 rows across ten pages and stops at the last page', async () => {
    const list = vi.fn(async ({ query = {} }: { query?: Record<string, unknown> }) => page(query))
    const wrapper = createList(createResource(list))
    await flushPromises()
    expect(wrapper.findComponent({ name: 'AppList' }).props('infiniteScroll')).toBe(true)
    for (let number = 2; number <= 10; number++) {
      await wrapper.get('button').trigger('click')
      await flushPromises()
      expect(wrapper.findAll('span')).toHaveLength(number * 50)
    }
    expect(wrapper.findComponent({ name: 'AppList' }).props('hasNextPage')).toBe(false)
    await wrapper.get('button').trigger('click')
    await flushPromises()
    expect(list).toHaveBeenCalledTimes(10)
    expect(new Set(wrapper.findAll('span').map((node) => node.text())).size).toBe(500)
    wrapper.unmount()
  })

  it('ignores repeated load-more events while a page is pending', async () => {
    let resolve!: (value: unknown) => void
    const pending = new Promise((yes) => {
      resolve = yes
    })
    const list = vi
      .fn()
      .mockResolvedValueOnce(page({ page: 1 }))
      .mockReturnValueOnce(pending)
    const wrapper = createList(createResource(list))
    await flushPromises()
    await wrapper.get('button').trigger('click')
    await wrapper.get('button').trigger('click')
    expect(list).toHaveBeenCalledTimes(2)
    resolve(page({ page: 2 }))
    await flushPromises()
    expect(wrapper.findAll('span')).toHaveLength(100)
    wrapper.unmount()
  })

  it('filters local items without a resource', async () => {
    const wrapper = createList(undefined, {
      items: [
        { id: '1', name: 'Alpha' },
        { id: '2', name: 'Beta' },
      ],
      itemLabel: 'name',
    })
    await flushPromises()
    expect(wrapper.findComponent({ name: 'AppList' }).props('infiniteScroll')).toBe(false)
    await wrapper.get('input').setValue('bet')
    await flushPromises()
    expect(wrapper.findAll('span').map((node) => node.text())).toEqual(['2'])
    wrapper.unmount()
  })
})
