export type OrganizationUserRaw = DeepPartial<OrganizationUser>

export interface OrganizationUser {
  id: string | null
  organization_id: string | null
  user_id: string | null
  user?: {
    id: string
    email: string
    first_name: string | null
    last_name: string | null
    is_superuser: boolean
  }
}

export const organizationUserCodec = createCodec<OrganizationUser>({
  decode: (raw: OrganizationUserRaw) => ({
    id: raw.id ?? null,
    organization_id: raw.organization_id ?? null,
    user_id: raw.user_id ?? null,
    user: raw.user
      ? {
          id: raw.user.id!,
          email: raw.user.email ?? '',
          first_name: raw.user.first_name ?? null,
          last_name: raw.user.last_name ?? null,
          is_superuser: Boolean(raw.user.is_superuser),
        }
      : undefined,
  }),
  encode: (data) => ({
    organization_id: data.organization_id ?? null,
    user_id: data.user?.id ?? null,
  }),
})
