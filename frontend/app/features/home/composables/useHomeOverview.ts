import { computed, type ComputedRef } from 'vue'
import { useResourceList } from '~/shared/api/useResource'
import { organizationUserResource, type OrganizationUser } from '~/features/organization/resources/organizationUser'
import { userResource } from '~/features/user/resources/user'
import { userTokenResource, type UserToken } from '~/features/user/resources/userToken'

/** Enough rows for a dashboard count; beyond it the count reads «100+» (the API does not return totals). */
const OVERVIEW_PAGE_SIZE = 100

export type HomeCount = { value: number; more: boolean; loading: boolean }

type CountSource = {
  items: ComputedRef<unknown[]>
  data: { value: { pages: { hasNext: boolean }[] } | undefined }
  isLoading: { value: boolean }
}

const countOf = (list: CountSource): ComputedRef<HomeCount> =>
  computed<HomeCount>(() => ({
    value: list.items.value.length,
    more: Boolean(list.data.value?.pages.at(-1)?.hasNext),
    loading: list.isLoading.value,
  }))

/** The home page's live numbers: the selected organization, its members, the user's API tokens and (superusers) users. */
export const useHomeOverview = () => {
  const { user, organizations } = useSession()
  const setupStore = useSetupStore()
  const organization = computed(() => setupStore.state.organization)
  const isSuperuser = computed<boolean>(() => Boolean(user.value?.is_superuser))

  const members = useResourceList(organizationUserResource, {
    params: () => ({ organization_id: organization.value?.id ?? '' }),
    pageSize: OVERVIEW_PAGE_SIZE,
    enabled: () => Boolean(organization.value),
  })
  const tokens = useResourceList(userTokenResource, {
    params: () => ({ user_id: user.value?.id ?? '' }),
    pageSize: OVERVIEW_PAGE_SIZE,
    enabled: () => Boolean(user.value),
  })
  const users = useResourceList(userResource, { pageSize: OVERVIEW_PAGE_SIZE, enabled: isSuperuser })

  return {
    user,
    organization,
    isSuperuser,
    organizationCount: computed<HomeCount>(() => ({ value: organizations.value.length, more: false, loading: false })),
    members: members.items as ComputedRef<OrganizationUser[]>,
    membersLoading: computed<boolean>(() => members.isLoading.value),
    membersError: computed<boolean>(() => Boolean(members.error.value)),
    memberCount: countOf(members),
    tokens: tokens.items as ComputedRef<UserToken[]>,
    tokensLoading: computed<boolean>(() => tokens.isLoading.value),
    tokenCount: countOf(tokens),
    userCount: countOf(users),
  }
}
