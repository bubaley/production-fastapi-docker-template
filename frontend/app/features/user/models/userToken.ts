export type UserTokenRaw = DeepPartial<UserToken>

export interface UserToken {
  id: string | null
  user_id: string | null
  created_at: string | null
  updated_at: string | null
  name: string
  value_preview: string
  last_used_at: string | null
  /** Present only in the response right after creation */
  value: string | null
}

export const userTokenCodec = createCodec<UserToken>({
  decode: (raw: UserTokenRaw) => ({
    id: raw.id ?? null,
    user_id: raw.user_id ?? null,
    created_at: raw.created_at ?? null,
    updated_at: raw.updated_at ?? null,
    name: raw.name ?? '',
    value_preview: raw.value_preview ?? '',
    last_used_at: raw.last_used_at ?? null,
    value: raw.value ?? null,
  }),
  encode: (data) => ({
    user_id: data.user_id || null,
    name: data.name || '',
  }),
})
