import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { computed, ref, shallowRef } from 'vue'
import AppListToolbar from '../app/shared/ui/app/AppListToolbar.vue'
import AppPage from '../app/shared/ui/app/AppPage.vue'
import AppListTemplate from '../app/shared/ui/template/AppListTemplate.vue'
import { useRepoData } from '../app/shared/toolkits/repo/composables/useRepoData'

const pagination = (page = 1) => ({ page, size: 50, total: 500, pages: 10, has_next: page < 10 })
const response = (page: number) => ({ pagination: pagination(page), items: Array.from({ length: 50 }, (_, index) => ({ id: String((page - 1) * 50 + index + 1) })) })
beforeEach(() => {
  vi.stubGlobal('ref', ref)
  vi.stubGlobal('shallowRef', shallowRef)
  vi.stubGlobal('computed', computed)
  vi.stubGlobal('useRouter', () => ({ push: vi.fn() }))
  vi.stubGlobal('useSectionBind', () => computed(() => ({})))
  vi.stubGlobal('useRepoData', useRepoData)
  vi.stubGlobal('useListEvents', () => ({ updateListItem: vi.fn(), deleteListItem: vi.fn() }))
  vi.stubGlobal('paginationFromServer', (raw = {}) => ({ ...pagination(), has_next: false, ...raw }))
})
afterEach(() => vi.unstubAllGlobals())
const createList = (repo: unknown, props = {}, slots = {}) => mount(AppListTemplate, {
  props: { repo: repo as never, ...props },
  slots,
  global: { components: { AppPage }, stubs: {
    AppInput: { props: ['modelValue'], emits: ['update:modelValue'], template: '<input :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />' },
    AppTitle: true,
    AppBackButton: true,
    AppList: { name: 'AppList', props: ['items', 'infiniteScroll'], emits: ['loadMore'], template: '<div><span v-for="item in items" :key="item.id">{{ item.id }}</span><button @click="$emit(\'loadMore\')">Ещё</button></div>' },
    AppButton: true,
    AppModal: true,
    AppDetailTemplate: true,
  } },
})

describe('list template pagination', () => {
  it('keeps search and filters outside the scrolling body while wiring search back to the query', async () => {
    const repo = { list: vi.fn((query, config) => Promise.resolve(query.name
      ? { items: [{ id: '500' }], pagination: { ...pagination(), has_next: false } }
      : response(config.pagination.page))) }
    const wrapper = createList(repo, { searchParam: 'name', debounce: 0 }, { filters: '<div data-test="filters">Фильтры</div>' })
    await flushPromises()
    expect(wrapper.get('main').find('input').exists()).toBe(false)
    expect(wrapper.get('main').find('[data-test="filters"]').exists()).toBe(false)
    expect(wrapper.find('[data-test="filters"]').exists()).toBe(true)
    expect(wrapper.findComponent({ name: 'AppList' }).classes()).toContain('-mx-3')
    await wrapper.get('input').setValue('500')
    await flushPromises()
    expect(repo.list.mock.calls.at(-1)?.[0]).toEqual({ name: '500' })
    expect(repo.list.mock.calls.at(-1)?.[1].pagination.page).toBe(1)
    expect(wrapper.findComponent({ name: 'AppList' }).props('items')).toEqual([{ id: '500' }])
    wrapper.unmount()
  })

  it('merges declarative filter values with page scope and resets appended pages on change and clear', async () => {
    const repo = { list: vi.fn((_query, config) => Promise.resolve(response(config.pagination.page))) }
    const wrapper = createList(repo, { debounce: 0, extraParams: { organization_id: 'scope' } })
    await flushPromises()
    await wrapper.get('button').trigger('click')
    await flushPromises()
    expect(wrapper.findAll('span')).toHaveLength(100)
    wrapper.findComponent(AppListToolbar).vm.$emit('update:filters', { key: 'sample', active: false, count: 0 })
    await flushPromises()
    expect(repo.list.mock.calls.at(-1)?.[0]).toEqual({ key: 'sample', active: false, count: 0, organization_id: 'scope' })
    expect(repo.list.mock.calls.at(-1)?.[1].pagination.page).toBe(1)
    expect(wrapper.findAll('span')).toHaveLength(50)
    wrapper.findComponent(AppListToolbar).vm.$emit('update:filters', {})
    await flushPromises()
    expect(repo.list.mock.calls.at(-1)?.[0]).toEqual({ organization_id: 'scope' })
    wrapper.unmount()
  })

  it('appends 500 rows across ten pages and stops at the last page', async () => {
    const repo = { list: vi.fn((_query, config) => Promise.resolve(response(config.pagination.page))) }
    const wrapper = createList(repo)
    await flushPromises()
    expect(wrapper.findComponent({ name: 'AppList' }).props('infiniteScroll')).toBe(true)
    for (let page = 2; page <= 10; page++) {
      await wrapper.get('button').trigger('click')
      await flushPromises()
      expect(wrapper.findAll('span')).toHaveLength(page * 50)
    }
    await wrapper.get('button').trigger('click')
    expect(repo.list).toHaveBeenCalledTimes(10)
    expect(new Set(wrapper.findAll('span').map(node => node.text())).size).toBe(500)
    wrapper.unmount()
  })

  it('ignores repeated load-more events while a page is pending', async () => {
    let resolve!: (value: ReturnType<typeof response>) => void
    const pending = new Promise<ReturnType<typeof response>>(yes => { resolve = yes })
    const repo = { list: vi.fn().mockResolvedValueOnce(response(1)).mockReturnValueOnce(pending) }
    const wrapper = createList(repo)
    await flushPromises()
    await wrapper.get('button').trigger('click')
    await wrapper.get('button').trigger('click')
    expect(repo.list).toHaveBeenCalledTimes(2)
    resolve(response(2))
    await flushPromises()
    expect(wrapper.findAll('span')).toHaveLength(100)
    wrapper.unmount()
  })
})
