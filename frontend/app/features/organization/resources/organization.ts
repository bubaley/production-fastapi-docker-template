import {
  organizationsCreate,
  organizationsDestroy,
  organizationsList,
  organizationsRetrieve,
  organizationsUpdate,
  type OrganizationReadSchema,
} from '~/shared/api/generated'
import { defineResource } from '~/shared/api/resource'

export type Organization = OrganizationReadSchema
export type OrganizationForm = { id: string | null; name: string; key: string }

export const organizationResource = defineResource({
  key: 'organizations',
  sdk: {
    list: organizationsList,
    retrieve: organizationsRetrieve,
    create: organizationsCreate,
    update: organizationsUpdate,
    destroy: organizationsDestroy,
  },
  toForm: (item?: Partial<Organization>): OrganizationForm => ({
    id: item?.id ?? null,
    name: item?.name ?? '',
    key: item?.key ?? '',
  }),
  toCreate: (form) => ({ name: form.name, key: form.key }),
  // The key is the tenancy id: fixed after creation.
  toUpdate: (form) => ({ name: form.name }),
  // The session lists the user's organizations.
  invalidates: ['session'],
})
