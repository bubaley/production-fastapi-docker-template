<template>
  <!-- `sticky="controls"`: the greeting and the numbers scroll away, the member search stays on top. -->
  <AppPageView
    :title="greeting"
    :description="description"
    max-width="lg"
    sticky="controls"
  >
    <template #actions>
      <AppTemplateActions
        class="flex-wrap"
        :actions="actions"
      />
    </template>

    <template #subheader>
      <div class="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <HomeStatCard
          label="Организации"
          hint="Все организации"
          :icon="Building"
          :count="organizationCount"
          :to="{ name: 'settings-organizations' }"
        />
        <HomeStatCard
          label="Участники"
          hint="Пригласить"
          :icon="Users"
          :count="memberCount"
          :to="organizationRoute"
        />
        <HomeStatCard
          label="Токены API"
          hint="В профиле"
          :icon="KeyRound"
          :count="tokenCount"
          :to="{ name: 'settings-profile' }"
        />
        <HomeStatCard
          v-if="isSuperuser"
          label="Пользователи"
          hint="Все учётные записи"
          :icon="UserRound"
          :count="userCount"
          :to="{ name: 'settings-users' }"
        />
        <HomeStatCard
          v-else
          label="Компоненты"
          hint="Каталог интерфейса"
          :icon="Palette"
          :count="{ value: catalogueSize, more: false, loading: false }"
          :to="{ name: 'ui' }"
        />
      </div>
    </template>

    <template #controls>
      <div class="flex items-center gap-2">
        <AppInput
          v-model="search"
          :icon="Search"
          placeholder="Найти участника"
          aria-label="Найти участника"
          clearable
          class="min-w-0 flex-1 sm:max-w-72"
        />
        <AppSelect
          v-model="access"
          :items="accessOptions"
          emit-value
          :clearable="false"
          :variant="access === 'all' ? 'outline' : 'active-outline'"
          aria-label="Доступ"
          class="w-40 shrink-0 sm:w-48"
        />
      </div>
    </template>

    <div class="flex flex-col gap-10">
      <AppSection
        title="Участники организации"
        :description="organization ? `Люди с доступом к «${organization.name}»` : undefined"
        title-size="md"
      >
        <AppTable
          :items="visibleMembers"
          :loading="membersLoading"
          :error="membersError ? 'Не удалось загрузить участников' : undefined"
          :empty-text="search || access !== 'all' ? 'Никого не нашли' : 'Участников пока нет'"
          clickable
          @row-click="openOrganization"
        >
          <AppColumn header="Участник">
            <template #body="{ data }">
              <span class="flex min-w-0 items-center gap-2.5">
                <AppAvatar
                  :name="userDisplayName(data.user)"
                  size="small"
                  variant="soft"
                />
                <span class="truncate">{{ userDisplayName(data.user) || '—' }}</span>
              </span>
            </template>
          </AppColumn>
          <AppColumn
            header="Электронная почта"
            header-class="max-sm:hidden"
            body-class="text-muted-foreground max-sm:hidden"
            :format="(row) => row.user?.email || '—'"
          />
          <AppColumn header="Доступ">
            <template #body="{ data }">
              <AppBadge
                :label="data.user?.is_superuser ? 'Суперпользователь' : 'Пользователь'"
                :tone="data.user?.is_superuser ? 'info' : 'neutral'"
              />
            </template>
          </AppColumn>
        </AppTable>
      </AppSection>

      <div class="grid gap-10 lg:grid-cols-2">
        <HomeTokens
          :tokens="tokens"
          :loading="tokensLoading"
        />
        <HomeLinks :is-superuser="isSuperuser" />
      </div>
    </div>

    <OrganizationCreateModal v-model="creating" />
  </AppPageView>
</template>

<script setup lang="ts">
import { Building, KeyRound, Palette, Plus, Search, UserPlus, UserRound, Users } from '@lucide/vue'
import type { RouteLocationRaw } from 'vue-router'
import OrganizationCreateModal from '~/features/organization/components/OrganizationCreateModal.vue'
import type { OrganizationUser } from '~/features/organization/resources/organizationUser'
import { uiCatalog } from '~/features/ui/catalog'
import HomeLinks from '../components/HomeLinks.vue'
import HomeStatCard from '../components/HomeStatCard.vue'
import HomeTokens from '../components/HomeTokens.vue'
import { useHomeOverview } from '../composables/useHomeOverview'

type Access = 'all' | 'superuser' | 'regular'

const {
  user,
  organization,
  isSuperuser,
  organizationCount,
  members,
  membersLoading,
  membersError,
  memberCount,
  tokens,
  tokensLoading,
  tokenCount,
  userCount,
} = useHomeOverview()

const greeting = computed<string>(() => {
  const name = user.value?.first_name || userDisplayName(user.value)
  return name ? `Здравствуйте, ${name}` : 'Главная'
})
const description = computed<string>(() =>
  organization.value ? `Организация «${organization.value.name}»` : 'Выберите организацию, чтобы начать работу',
)
const organizationRoute = computed<RouteLocationRaw>(() =>
  organization.value
    ? { name: 'settings-organizations-id', params: { id: organization.value.id } }
    : { name: 'settings-organizations' },
)
const catalogueSize = uiCatalog.reduce((total, group) => total + group.sections.length, 0)

const search = ref<string>('')
const access = ref<Access>('all')
const accessOptions: { id: Access; name: string }[] = [
  { id: 'all', name: 'Любой доступ' },
  { id: 'superuser', name: 'Суперпользователи' },
  { id: 'regular', name: 'Пользователи' },
]
const visibleMembers = computed<OrganizationUser[]>(() => {
  const term = search.value.trim().toLocaleLowerCase('ru')
  return members.value.filter((member) => {
    if (access.value !== 'all' && Boolean(member.user?.is_superuser) !== (access.value === 'superuser')) return false
    const text = `${userDisplayName(member.user)} ${member.user?.email ?? ''}`.toLocaleLowerCase('ru')
    return !term || text.includes(term)
  })
})
const openOrganization = async (): Promise<void> => {
  await navigateTo(organizationRoute.value)
}

const creating = ref<boolean>(false)
const actions = computed<AppTemplateAction[]>(() => [
  {
    label: 'Пригласить участника',
    icon: UserPlus,
    hidden: !organization.value,
    action: openOrganization,
  },
  {
    label: 'Новая организация',
    icon: Plus,
    variant: 'outline',
    action: () => {
      creating.value = true
    },
  },
])
</script>
