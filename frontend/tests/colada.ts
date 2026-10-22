import { PiniaColada } from '@pinia/colada'
import { createPinia } from 'pinia'
import { vi } from 'vite-plus/test'
import { computed, ref, shallowRef, watch } from 'vue'

/** Pinia + Pinia Colada for mounting templates, and the Nuxt auto-imports they use. */
export const installColada = () => {
  vi.stubGlobal('ref', ref)
  vi.stubGlobal('shallowRef', shallowRef)
  vi.stubGlobal('computed', computed)
  vi.stubGlobal('watch', watch)
  vi.stubGlobal('useNuxtApp', () => ({ $api: {} }))
  vi.stubGlobal('useToast', () => ({ default: vi.fn(), error: vi.fn() }))
  vi.stubGlobal('useSectionBind', () => computed(() => ({})))
  return [createPinia(), [PiniaColada, { queryOptions: { staleTime: 60_000, refetchOnWindowFocus: false } }]] as const
}
