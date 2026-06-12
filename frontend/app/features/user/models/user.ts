export type UserRaw = DeepPartial<User>

export interface User {
  id: string | null
  email: string
  first_name: string | null
  last_name: string | null
  is_superuser: boolean
  password?: string | null
  /** optional: session / legacy pickers */
  organization_id?: string | null
}

export const userCodec = createCodec<User>({
  decode: (raw: UserRaw) => {
    return {
      id: raw.id ?? null,
      email: raw.email ?? '',
      first_name: raw.first_name ?? null,
      last_name: raw.last_name ?? null,
      is_superuser: Boolean(raw.is_superuser),
      password: null,
    }
  },
  encode: (data) => {
    if (!data.id) {
      return {
        email: data.email || null,
        first_name: data.first_name || null,
        last_name: data.last_name || null,
        password: data.password || null,
        is_superuser: data.is_superuser,
      }
    }
    const payload: Record<string, unknown> = {
      email: data.email || null,
      first_name: data.first_name || null,
      last_name: data.last_name || null,
      is_superuser: data.is_superuser,
    }
    if (data.password) {
      payload.password = data.password
    }
    return payload
  },
})
