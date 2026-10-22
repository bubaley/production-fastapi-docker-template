import { computed, onScopeDispose, shallowReactive, shallowRef, watch, type Ref } from 'vue'

// Every portalled surface shares opening order, independent of its Vue parent.
// Keep assigned layers on close so exit animations cannot jump behind older surfaces.
const stack = shallowReactive<{ id: symbol; layer: number }[]>([])

export function useOverlayStack(open: Ref<boolean>) {
  const id = Symbol('app-overlay')
  const layer = shallowRef(1000)
  const unregister = () => {
    const index = stack.findIndex((entry) => entry.id === id)
    if (index !== -1) stack.splice(index, 1)
  }

  watch(
    open,
    (value) => {
      unregister()
      if (value) {
        layer.value = Math.max(998, ...stack.map((entry) => entry.layer)) + 2
        stack.push({ id, layer: layer.value })
      }
    },
    { immediate: true, flush: 'sync' }
  )
  onScopeDispose(unregister)

  return {
    backdropStyle: computed(() => ({ '--app-overlay-z': layer.value })),
    contentStyle: computed(() => ({ '--app-overlay-z': layer.value + 1 })),
    isTop: computed(() => stack.at(-1)?.id === id)
  }
}
