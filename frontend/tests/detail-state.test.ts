import { afterEach, beforeEach, describe, expect, it, vi } from 'vite-plus/test'
import { flushPromises, mount } from '@vue/test-utils'
import { nextTick, reactive } from 'vue'
import { useTemplateDetail } from '../app/shared/ui/template/composables/useTemplateDetail'
import AppDetailTemplate from '../app/shared/ui/template/AppDetailTemplate.vue'
import { defineResource } from '../app/shared/api/resource'
import { installColada } from './colada'

type Record = { id: string; name: string }
const deferred = () => {
  let resolve!: (value: { data: Record }) => void
  let reject!: (reason: Error) => void
  const promise = new Promise<{ data: Record }>((yes, no) => {
    resolve = yes
    reject = no
  })
  return { promise, resolve, reject }
}
const createResource = (retrieve: ReturnType<typeof vi.fn>) =>
  defineResource({
    key: 'records',
    sdk: { retrieve: retrieve as never },
    toForm: (item?: Partial<Record>) => ({ id: item?.id ?? null, name: item?.name ?? '' }),
  })

let route: { params: { id: string } }
beforeEach(() => {
  route = reactive({ params: { id: 'A' } })
  vi.stubGlobal('useRoute', () => route)
  vi.stubGlobal('useRouter', () => ({ back: vi.fn() }))
  vi.stubGlobal('useTemplateDetail', useTemplateDetail)
})
afterEach(() => vi.unstubAllGlobals())
const render = (resource: unknown) => {
  const plugins = installColada()
  return mount(AppDetailTemplate, {
    props: { resource: resource as never },
    slots: { default: '<div>{{ params.item.name }}</div>' },
    global: {
      plugins: plugins as never,
      stubs: {
        AppPageView: { template: '<main><slot /></main>' },
        AppSection: { template: '<section><slot /></section>' },
        AppDetailActions: true,
        AppLoadingIndicator: { props: ['label'], template: '<span role="status">{{ label }}</span>' },
        AppButton: { template: '<button><slot /></button>' },
      },
    },
  })
}

describe('detail record from the [key, id] query', () => {
  it('keeps B visible when A returns late', async () => {
    const a = deferred()
    const b = deferred()
    const retrieve = vi.fn().mockReturnValueOnce(a.promise).mockReturnValueOnce(b.promise)
    const wrapper = render(createResource(retrieve))
    await nextTick()
    expect(wrapper.get('[role="status"]').text()).toContain('Загрузка')
    route.params.id = 'B'
    await flushPromises()
    b.resolve({ data: { id: 'B', name: 'Current B' } })
    await flushPromises()
    expect(wrapper.text()).toBe('Current B')
    a.resolve({ data: { id: 'A', name: 'Old A' } })
    await flushPromises()
    expect(wrapper.text()).toBe('Current B')
    expect(retrieve.mock.calls.map(([options]) => options.path.item_id)).toEqual(['A', 'B'])
    wrapper.unmount()
  })

  it('shows a failed load and retries the same record', async () => {
    const retrieve = vi
      .fn()
      .mockRejectedValueOnce(new Error('404'))
      .mockResolvedValueOnce({ data: { id: 'A', name: 'Recovered' } })
    const wrapper = render(createResource(retrieve))
    await flushPromises()
    expect(wrapper.get('[role="alert"]').text()).toContain('Не удалось загрузить запись')
    await wrapper.get('button').trigger('click')
    await flushPromises()
    expect(wrapper.text()).toBe('Recovered')
    expect(retrieve).toHaveBeenCalledTimes(2)
    wrapper.unmount()
  })

  it('builds a new record for the `new` route without a request', async () => {
    route.params.id = 'new'
    const retrieve = vi.fn()
    const resource = createResource(retrieve)
    const wrapper = render({ ...resource, toForm: () => ({ id: null, name: 'Draft' }) })
    await flushPromises()
    expect(wrapper.text()).toBe('Draft')
    expect(retrieve).not.toHaveBeenCalled()
    wrapper.unmount()
  })
})
