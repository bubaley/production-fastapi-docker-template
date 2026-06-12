type OrganizationRaw = DeepPartial<Organization>

export interface Organization {
  id: string | null
  created_at: string | null
  updated_at: string | null
  name: string
  key: string
}

export const organizationCodec = createCodec<Organization>({
  decode: (raw: OrganizationRaw) => {
    return {
      id: raw.id || null,
      created_at: raw.created_at || null,
      updated_at: raw.updated_at || null,
      key: raw.key ?? '',
      name: raw.name ?? '',
    }
  },
  encode: (data) => {
    return {
      name: data.name || null,
      key: data.key || '',
    }
  },
})
