import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import type { Organization } from '~/features/organization/models/organization'

const setupStorageKey = 'setup:state'

export type SetupState = {
  organization: Organization | null
  theme: string | null
  restored: boolean
}

type SetupKey = keyof SetupState

export const useSetupStore = defineStore('setup', () => {
  const state = ref<SetupState>({
    organization: null,
    theme: null,
    restored: false,
  })

  const isRestoring = ref(false)

  const repoMap = {
    organization: useRepo('organization'),
  } as const

  type RepoKey = keyof typeof repoMap

  const isRepoKey = (key: SetupKey): key is RepoKey => {
    return key in repoMap
  }

  const parseStoredJson = (value: string): Partial<Record<SetupKey, unknown>> => {
    try {
      const parsed = JSON.parse(value)
      return parsed && typeof parsed === 'object' ? (parsed as Partial<Record<SetupKey, unknown>>) : {}
    } catch {
      return {}
    }
  }

  const serializeState = (): string => {
    const payload: Partial<Record<SetupKey, unknown>> = {}

    for (const key of Object.keys(state.value) as SetupKey[]) {
      const value = state.value[key]

      if (isRepoKey(key)) {
        payload[key] = (value as AppModel | null)?.id ?? null
        continue
      }

      payload[key] = value ?? null
    }

    return JSON.stringify(payload)
  }

  const persistState = () => {
    if (!import.meta.client || isRestoring.value) return
    localStorage.setItem(setupStorageKey, serializeState())
  }

  watch(state, persistState, { deep: true })

  const restore = async () => {
    if (!import.meta.client) return

    isRestoring.value = true
    try {
      const raw = localStorage.getItem(setupStorageKey)
      const payload = raw ? parseStoredJson(raw) : {}

      const repoTasks: Promise<void>[] = []

      for (const key of Object.keys(state.value) as SetupKey[]) {
        const storedValue = payload[key]
        if (isRepoKey(key)) {
          if (storedValue === null || storedValue === undefined || storedValue === '') {
            ;(state.value as any)[key] = null
            continue
          }

          repoTasks.push(
            (async () => {
              const item = await repoMap[key].retrieve(String(storedValue))
              ;(state.value as any)[key] = item || null
            })(),
          )
          continue
        }

        ;(state.value as any)[key] = storedValue ?? null
      }

      await Promise.all(repoTasks)
      state.value.restored = true
    } finally {
      isRestoring.value = false
      persistState()
    }
  }

  return {
    state,
    restore,
  }
})
