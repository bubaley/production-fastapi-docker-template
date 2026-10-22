import { onBeforeUnmount, watch, type Ref } from 'vue'

/** One request per confirmed page. Observe actual visibility through every scroll/clipping ancestor. */
export function useAutoPagination(
  target: Ref<HTMLElement | undefined>,
  options: {
    hasMore: () => boolean
    loading: () => boolean
    disabled: () => boolean
    error: () => boolean
    requestKey: () => unknown
    load: () => void
  }
) {
  let observer: IntersectionObserver | undefined
  let lastRequested: unknown = Symbol('initial')
  let disposed = false
  function observe() {
    observer?.disconnect()
    const element = target.value
    if (disposed || !element) return
    // Re-observe after DOM updates: the old intersection may describe the previous page's height.
    const activeObserver = new IntersectionObserver((entries) => {
      if (
        disposed ||
        observer !== activeObserver ||
        !entries.some((entry) => entry.isIntersecting && entry.intersectionRatio > 0)
      )
        return
      if (!options.hasMore() || options.loading() || options.disabled() || options.error()) return
      const key = options.requestKey()
      if (Object.is(lastRequested, key)) return
      lastRequested = key
      options.load()
    })
    observer = activeObserver
    observer.observe(element)
  }
  const stop = watch(
    () => [
      target.value,
      options.requestKey(),
      options.hasMore(),
      options.loading(),
      options.disabled(),
      options.error()
    ],
    observe,
    { immediate: true, flush: 'post' }
  )
  onBeforeUnmount(() => {
    disposed = true
    stop()
    observer?.disconnect()
  })
}
