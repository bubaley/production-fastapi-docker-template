import { afterEach, beforeEach, describe, expect, it, vi } from 'vite-plus/test'
import { flushPromises, mount } from '@vue/test-utils'
import { computed, nextTick, reactive } from 'vue'
import { useTemplateDetail } from '../app/shared/ui/template/composables/useTemplateDetail'
import AppDetailTemplate from '../app/shared/ui/template/AppDetailTemplate.vue'

const deferred = () => {
  let resolve!: (value: { id: string; name: string }) => void
  let reject!: (reason: Error) => void
  const promise = new Promise<{ id: string; name: string }>((yes, no) => { resolve = yes; reject = no })
  return { promise, resolve, reject }
}
let route: ReturnType<typeof reactive<{ params: { id: string } }>>
beforeEach(() => {
  route = reactive({ params: { id: 'A' } })
  vi.stubGlobal('useRoute', () => route)
  vi.stubGlobal('useRouter', () => ({ back: vi.fn() }))
  vi.stubGlobal('useSectionBind', () => computed(() => ({})))
  vi.stubGlobal('useTemplateDetail', useTemplateDetail)
  vi.stubGlobal('computed', computed)
})
afterEach(() => vi.unstubAllGlobals())
const render = (repo: unknown) => mount(AppDetailTemplate, {
  props: { repo: repo as never },
  slots: { default: '<div>{{ params.item.name }}</div>' },
  global: { stubs: {
    AppPageView: { template: '<main><slot /></main>' },
    AppSection: { template: '<section><slot /></section>' },
    AppDetailActions: true,
    AppLoadingIndicator: { props: ['label'], template: '<span role="status">{{ label }}</span>' },
    AppButton: { template: '<button><slot /></button>' },
  } },
})
describe('detail request ownership', () => {
  it('keeps B visible when A returns late without publishing either result to the shared repo', async () => {
    const a = deferred(), b = deferred()
    const repo = { item: null, retrieve: vi.fn().mockReturnValueOnce(a.promise).mockReturnValueOnce(b.promise) }
    const wrapper = render(repo)
    await nextTick()
    await flushPromises()
    expect(wrapper.get('[role="status"]').text()).toContain('Загрузка')
    route.params.id = 'B'
    b.resolve({ id: 'B', name: 'Current B' })
    await flushPromises()
    expect(wrapper.text()).toBe('Current B')
    a.resolve({ id: 'A', name: 'Old A' })
    await flushPromises()
    expect(wrapper.text()).toBe('Current B')
    expect(repo.item).toBeNull()
    expect(repo.retrieve.mock.calls[0]?.[3]).toEqual({ storeInRepo: false })
    wrapper.unmount()
  })
  it('shows a failed load and retries the same record', async () => {
    const repo = { retrieve: vi.fn().mockRejectedValueOnce(new Error('404')).mockResolvedValueOnce({ id: 'A', name: 'Recovered' }) }
    const wrapper = render(repo)
    await flushPromises()
    expect(wrapper.get('[role="alert"]').text()).toContain('Не удалось загрузить запись')
    await wrapper.get('button').trigger('click')
    await flushPromises()
    expect(wrapper.text()).toBe('Recovered')
    expect(repo.retrieve).toHaveBeenCalledTimes(2)
    wrapper.unmount()
  })
  it('clears the visible record immediately when the repository context is reset', async () => {
    const repo = reactive({ revision: 0, retrieve: vi.fn().mockResolvedValue({ id: 'A', name: 'Private A' }) })
    const wrapper = render(repo)
    await flushPromises()
    expect(wrapper.text()).toBe('Private A')
    repo.revision++
    await flushPromises()
    expect(wrapper.text()).not.toContain('Private A')
    wrapper.unmount()
  })
})
