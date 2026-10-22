import {
  usersCreate,
  usersDestroy,
  usersList,
  usersRetrieve,
  usersUpdate,
  type UserReadSchema,
} from '~/shared/api/generated'
import { defineResource } from '~/shared/api/resource'

export type User = UserReadSchema
export type UserForm = {
  id: string | null
  email: string
  first_name: string
  last_name: string
  is_superuser: boolean
  /** Only sent on create. */
  password: string
}

export const userResource = defineResource({
  key: 'users',
  sdk: { list: usersList, retrieve: usersRetrieve, create: usersCreate, update: usersUpdate, destroy: usersDestroy },
  toForm: (item?: Partial<User>): UserForm => ({
    id: item?.id ?? null,
    email: item?.email ?? '',
    first_name: item?.first_name ?? '',
    last_name: item?.last_name ?? '',
    is_superuser: item?.is_superuser ?? false,
    password: '',
  }),
  toCreate: ({ email, first_name, last_name, password, is_superuser }) => ({
    email,
    first_name,
    last_name,
    password,
    is_superuser,
  }),
  toUpdate: ({ email, first_name, last_name, is_superuser }) => ({ email, first_name, last_name, is_superuser }),
  // Names show up in the session (profile) and in member lists.
  invalidates: ['session', 'organization-users'],
})
