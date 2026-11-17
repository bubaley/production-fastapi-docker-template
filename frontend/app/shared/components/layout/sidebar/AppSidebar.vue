<template>
  <div class="flex min-h-0 flex-col">
    <!-- Top row: the layout's context control (organization switcher, «Назад») and the hide/close button. -->
    <div class="flex h-12 shrink-0 items-center gap-1 px-2">
      <div class="min-w-0 flex-1">
        <slot name="header" />
      </div>
      <!-- In the phone sheet the panel closes rather than hides, so it gets a plain close button. -->
      <AppButton
        variant="ghost"
        size="icon-sm"
        text-variant="muted"
        class="size-[44px] shrink-0 md:size-control-sm"
        :icon="sheet ? X : PanelLeftClose"
        :aria-label="sheet ? 'Закрыть навигацию' : 'Скрыть боковую панель'"
        :title="sheet ? 'Закрыть' : 'Скрыть боковую панель'"
        @click="emit('hide')"
      />
    </div>
    <div class="min-h-0 flex-1 overflow-y-auto px-2 py-2">
      <slot />
    </div>
    <!-- The brand strip and the account row below are the same height: one row with the same padding. -->
    <div
      v-if="$slots.brand"
      class="shrink-0 px-2 py-2"
    >
      <slot name="brand" />
    </div>
    <div
      v-if="$slots.footer"
      class="flex shrink-0 flex-col gap-px border-t border-sidebar-border px-2 py-2"
    >
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { PanelLeftClose, X } from '@lucide/vue'

defineProps<{
  /** Rendered in the phone sheet: the header button closes the sheet instead of hiding the sidebar. */
  sheet?: boolean
}>()
const emit = defineEmits<{ hide: [] }>()
</script>
