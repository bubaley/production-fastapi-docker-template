<template>
  <AppButton
    severity="secondary"
    icon="lucide:user"
    class="rounded-xl!"
    @click="toggle"
  />
  <Popover
    ref="op"
    class="w-[240px] overflow-hidden"
    :pt="{ content: { class: '!p-0' } }"
    :show-close-icon="false"
  >
    <div class="p-2">
      <div class="font-bold ml-2 my-2">МЕНЮ</div>
      <div
        v-for="action in actions"
        :key="action.label"
        class="flex flex-col"
      >
        <AppButton
          severity="secondary"
          text
          class="justify-start!"
          fluid
          @click="action.action"
        >
          {{ action.label }}
        </AppButton>
      </div>
    </div>
    <Divider class="mb-0! mt-1!" />
    <div class="p-2 dark:bg-secondary">
      <SelectButton
        fluid
        :model-value="$colorMode.value"
        :options="themes"
        @update:model-value="$colorMode.preference = $event"
      >
        <template #option="{ option }">
          <Icon
            class="h-5!"
            :name="option === 'dark' ? 'lucide:moon' : 'lucide:sun'"
          />
        </template>
      </SelectButton>
    </div>
  </Popover>
</template>

<script setup lang="ts">
import type { PopoverMethods } from 'primevue/popover'

const op = ref<PopoverMethods | null>(null)
const themes = ['light', 'dark']

const router = useRouter()
const { logout } = useAuth()

const logoutHandler = async () => {
  await logout()
  router.replace({ name: 'auth' })
}

const toggle = (event: Event) => {
  op.value?.toggle(event)
}

const actions = ref([
  {
    label: 'Профиль',
    action: () => navigateTo({ name: 'settings-profile' }),
  },
  {
    label: 'Выйти',
    action: logoutHandler,
  },
])
</script>
