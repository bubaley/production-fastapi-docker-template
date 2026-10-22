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
  /** Loads a stored organization the user is not a member of (superusers see every organization). */
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

  const persist = () => {
    if (!import.meta.client || !state.value.restored) return
    const payload: StoredSetup = { userId: userId.value, organization: state.value.organization?.id ?? null }
    localStorage.setItem(setupStorageKey, JSON.stringify(payload))
  }
  watch(() => state.value.organization?.id, persist)

  /**
   * Picks the organization stored for this user, else the only membership. A stored id from another account is
   * ignored, so signing in as someone else starts the organization choice again.
   */
  const restore = async ({ userId: currentUserId, organizations, retrieve }: SetupRestoreContext) => {
    if (!import.meta.client) return
    const request = ++generation
    const stored = readStored()
    const storedId = stored.userId === currentUserId ? stored.organization : null
    let organization = organizations.find((item) => item.id === storedId) ?? null
    if (!organization && storedId && retrieve) organization = await retrieve(storedId).catch(() => null)
    if (!organization && !storedId && organizations.length === 1) organization = organizations[0] ?? null
    if (request !== generation) return
    userId.value = currentUserId
    state.value.organization = organization
    state.value.restored = true
    persist()
  }

  /** Sign-out: forget the selection, including the stored one. */
  const reset = () => {
    generation++
    state.value.organization = null
    state.value.restored = false
    userId.value = null
    if (import.meta.client) localStorage.removeItem(setupStorageKey)
  }

  return { state, restore, reset }
})
