import {
  userTokensCreate,
  userTokensDestroy,
  userTokensList,
  userTokensRetrieve,
  userTokensUpdate,
  type UserTokenCreatedReadSchema,
  type UserTokenReadSchema,
} from '~/shared/api/generated'
import { defineResource } from '~/shared/api/resource'

/** `value` (the full secret) is present only in the create response. */
export type UserToken = UserTokenReadSchema & Partial<Pick<UserTokenCreatedReadSchema, 'value'>>
export type UserTokenForm = {
  id: string | null
  user_id: string | null
  name: string
  value_preview: string
  value: string | null
}

export const userTokenResource = defineResource({
  key: 'user-tokens',
  sdk: {
    list: userTokensList,
    retrieve: userTokensRetrieve,
    create: userTokensCreate,
    update: userTokensUpdate,
    destroy: userTokensDestroy,
  },
  toForm: (item?: Partial<UserToken>): UserTokenForm => ({
    id: item?.id ?? null,
    user_id: item?.user_id ?? null,
    name: item?.name ?? '',
    value_preview: item?.value_preview ?? '',
    value: item?.value ?? null,
  }),
  // The owner is fixed after creation; the update schema rejects it.
  toCreate: (form) => ({ user_id: form.user_id, name: form.name }),
  toUpdate: (form) => ({ name: form.name }),
})
