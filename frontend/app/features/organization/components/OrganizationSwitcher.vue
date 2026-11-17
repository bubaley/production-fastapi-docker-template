<template>
  <AppMenu
    :actions="actions"
    align="start"
    title="Организации"
    content-class="w-72 max-w-[calc(100vw-2rem)]"
  >
    <template #trigger>
      <button
        type="button"
        class="flex h-[44px] w-full min-w-0 items-center gap-2 rounded-md px-1.5 text-left transition-colors outline-none hover:bg-sidebar-accent/70 focus-visible:ring-2 focus-visible:ring-ring data-[state=open]:bg-sidebar-accent md:h-9"
        aria-label="Сменить организацию"
      >
        <span
          class="flex size-6 shrink-0 items-center justify-center rounded-md bg-primary text-xs font-semibold text-primary-foreground"
          aria-hidden="true"
          >{{ initial }}</span
        >
        <span class="min-w-0 flex-1 truncate text-sm font-medium text-sidebar-foreground">{{
          current?.name || 'Нет организации'
        }}</span>
        <AppIcon
          :icon="ChevronsUpDown"
          size="xs"
          tone="muted"
        />
      </button>
    </template>
    <template #action="{ action }">
      <AppIcon
        v-if="action.icon"
        :icon="action.icon"
      />
      <span
        class="min-w-0 flex-1 truncate"
        :title="action.label"
        >{{ action.label }}</span
      >
    </template>
  </AppMenu>
  <OrganizationCreateModal v-model="createOpen" />
</template>

<script setup lang="ts">
import { Building2, ChevronsUpDown, Plus, Settings2 } from '@lucide/vue'
import OrganizationCreateModal from './OrganizationCreateModal.vue'
import type { AppMenuAction } from '~/shared/ui/app/AppMenu.vue'
import type { SetupOrganization } from '~/shared/stores/useSetupStore'

const setupStore = useSetupStore()
const createOpen = ref<boolean>(false)
const { organizations } = useSession()

// The session has the fresh name after a rename; the store keeps the one chosen at selection time.
const current = computed<SetupOrganization | null>(() => {
  const selected = setupStore.state.organization
  return organizations.value.find((item) => item.id === selected?.id) ?? selected
})
const initial = computed<string>(() => (current.value?.name || '?').trim().slice(0, 1).toUpperCase())

// The session lists memberships only. The current organization can be outside them (a stored choice restored with
// `organizationsRetrieve`, see useSetupStore.restore), so it is kept in the list.
const choices = computed<SetupOrganization[]>(() => {
  const list: SetupOrganization[] = [...organizations.value]
  if (current.value && !list.some((item) => item.id === current.value?.id)) list.unshift(current.value)
  return list
})

const select = async (organization: SetupOrganization): Promise<void> => {
  if (organization.id === current.value?.id) return
  setupStore.state.organization = { id: organization.id, name: organization.name, key: organization.key }
  await navigateTo({ name: 'home' })
}

const actions = computed<AppMenuAction[]>(() => [
  ...choices.value.map((organization) => ({
    key: organization.id,
    label: organization.name,
    icon: Building2,
    checked: organization.id === current.value?.id,
    action: () => select(organization),
  })),
  {
    key: 'create',
    label: 'Создать организацию',
    icon: Plus,
    separatorBefore: true,
    action: () => {
      createOpen.value = true
    },
  },
  {
    key: 'manage',
    label: 'Управление организациями',
    icon: Settings2,
    hidden: choices.value.length === 0,
    action: async () => {
      await navigateTo({ name: 'settings-organizations' })
    },
  },
])
</script>
