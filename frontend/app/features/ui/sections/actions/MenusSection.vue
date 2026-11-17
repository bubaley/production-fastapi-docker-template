<script setup lang="ts">
import { Ellipsis, Pencil, Share2, Trash2 } from '@lucide/vue'
import type { AppMenuAction } from '~/shared/ui/app/AppMenu.vue'
import UiDemo from '../../components/UiDemo.vue'

const toast = useToast()
const confirm = ref(false)
const actions: AppMenuAction[] = [
  { label: 'Rename', icon: Pencil, action: () => void toast.default('Rename requested') },
  { label: 'Share', icon: Share2, action: () => void toast.default('Link copied') },
  {
    label: 'Delete',
    icon: Trash2,
    destructive: true,
    separatorBefore: true,
    action: () => {
      confirm.value = true
    },
  },
]
</script>

<template>
  <UiDemo
    title="Action menu"
    code='mode="menu" :actions label'
    description="Overflow actions of a row or a page behind a ⋯ button. The trigger goes into the trigger slot."
  >
    <div class="flex flex-wrap items-center gap-3">
      <AppMenu
        :actions="actions"
        label="Project actions"
      >
        <template #trigger>
          <AppButton
            variant="outline"
            label="Actions"
            :icon="Ellipsis"
          />
        </template>
      </AppMenu>
      <AppMenu :actions="actions">
        <template #trigger>
          <AppButton
            variant="ghost"
            :icon="Ellipsis"
            aria-label="More actions"
          />
        </template>
      </AppMenu>
    </div>
  </UiDemo>
  <UiDemo
    title="Context menu"
    code='mode="cursor"'
    description="The same list on right click, for rows and canvas items. Always offer the same actions through a visible button too."
  >
    <AppMenu
      mode="cursor"
      :actions="actions"
    >
      <template #trigger>
        <div
          class="flex h-control-lg items-center justify-center rounded-md border border-dashed border-border px-3 text-sm text-muted-foreground select-none"
        >
          Right-click here
        </div>
      </template>
    </AppMenu>
  </UiDemo>
  <AppConfirmModal
    v-model="confirm"
    decline-text="Cancel"
    close-label="Close"
    title="Delete project?"
    subtitle="This is a demo. Your data will not change."
    confirm-text="Delete"
    :confirm-props="{ variant: 'destructive' }"
    :confirm="() => void toast.default('Action confirmed')"
  />
</template>
