import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

const setupStorageKey = 'setup:state'

/** The slice of an organization the shell needs (`OrganizationReadSchema` fits). */
export type SetupOrganization = { id: string; name: string; key: string }

export type SetupState = {
  organization: SetupOrganization | null
  restored: boolean
}

type StoredSetup = { userId?: string | null; organization?: string | null }

export type SetupRestoreContext = {
  userId: string
  /** The session's organizations (`GET /auth/me`). */
  organizations: SetupOrganization[]
  /** Loads a stored organization that is no longer among the memberships; a failed request falls back to the first one. */
  retrieve?: (id: string) => Promise<SetupOrganization | null>
}

const readStored = (): StoredSetup => {
  try {
    const parsed = JSON.parse(localStorage.getItem(setupStorageKey) ?? '{}')
    return parsed && typeof parsed === 'object' ? (parsed as StoredSetup) : {}
  } catch {
    return {}
  }
}

/** Current organization (`Organization-Key` on every request), remembered per user in localStorage. */
export const useSetupStore = defineStore('setup', () => {
  const state = ref<SetupState>({ organization: null, restored: false })
  const userId = ref<string | null>(null)
  let generation = 0

  const persist = (): void => {
    if (!import.meta.client || !state.value.restored) return
    const payload: StoredSetup = { userId: userId.value, organization: state.value.organization?.id ?? null }
    localStorage.setItem(setupStorageKey, JSON.stringify(payload))
  }
  watch(() => state.value.organization?.id, persist)

  /**
   * Selects an organization without asking: the one stored for this user while it is still reachable, else the first
   * membership. A stored id from another account is ignored. `null` means the user has no organization at all; the
   * shell then asks to create one.
   */
  const restore = async ({ userId: currentUserId, organizations, retrieve }: SetupRestoreContext): Promise<void> => {
    if (!import.meta.client) return
    const request = ++generation
    const stored = readStored()
    const storedId = stored.userId === currentUserId ? stored.organization : null
    let organization: SetupOrganization | null = organizations.find((item) => item.id === storedId) ?? null
    if (!organization && storedId && retrieve) organization = await retrieve(storedId).catch(() => null)
    organization ??= organizations[0] ?? null
    if (request !== generation) return
    userId.value = currentUserId
    state.value.organization = organization
    state.value.restored = true
    persist()
  }

  /** Sign-out: forget the selection, including the stored one. */
  const reset = (): void => {
    generation++
    state.value.organization = null
    state.value.restored = false
    userId.value = null
    if (import.meta.client) localStorage.removeItem(setupStorageKey)
  }

  return { state, restore, reset }
})
