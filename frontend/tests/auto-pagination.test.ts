import { afterEach, describe, expect, it, vi } from 'vite-plus/test'
import { mount } from '@vue/test-utils'
import { defineComponent, h, nextTick, ref } from 'vue'
import { useAutoPagination } from '../app/shared/ui/app/infinite-scroll/useAutoPagination'

afterEach(() => vi.unstubAllGlobals())

describe('automatic pagination', () => {
  it('loads only a visible new page, pauses for loading and errors, and disconnects on unmount', async () => {
    const observers: { callback: IntersectionObserverCallback; disconnect: ReturnType<typeof vi.fn> }[] = []
    vi.stubGlobal(
      'IntersectionObserver',
      class {
        disconnect = vi.fn()
        observe = vi.fn()
        constructor(callback: IntersectionObserverCallback) {
          observers.push({ callback, disconnect: this.disconnect })
        }
      },
    )
    const loading = ref(false)
    const error = ref(false)
    const hasMore = ref(true)
    const disabled = ref(false)
    const page = ref(1)
    const load = vi.fn()
    const wrapper = mount(
      defineComponent({
        setup() {
          const target = ref<HTMLElement>()
          useAutoPagination(target, {
            hasMore: () => hasMore.value,
            loading: () => loading.value,
            error: () => error.value,
            disabled: () => disabled.value,
            requestKey: () => page.value,
            load,
          })
          return () => h('div', { ref: target })
        },
      }),
    )
    await nextTick()
    const intersect = (visible = true, index = observers.length - 1) => {
      observers[index]!.callback(
        [{ isIntersecting: visible, intersectionRatio: visible ? 1 : 0 } as IntersectionObserverEntry],
        {} as IntersectionObserver,
      )
    }
    intersect(false)
    expect(load).not.toHaveBeenCalled()
    intersect()
    intersect()
    expect(load).toHaveBeenCalledTimes(1)
    loading.value = true
    page.value = 2
    await nextTick()
    intersect()
    expect(load).toHaveBeenCalledTimes(1)
    loading.value = false
    error.value = true
    await nextTick()
    intersect()
    expect(load).toHaveBeenCalledTimes(1)
    error.value = false
    await nextTick()
    intersect(false)
    expect(load).toHaveBeenCalledTimes(1)
    intersect()
    expect(load).toHaveBeenCalledTimes(2)
    hasMore.value = false
    page.value = 3
    await nextTick()
    intersect()
    expect(load).toHaveBeenCalledTimes(2)
    wrapper.unmount()
    intersect()
    expect(load).toHaveBeenCalledTimes(2)
    expect(observers.every((observer) => observer.disconnect.mock.calls.length > 0)).toBe(true)
  })
})
