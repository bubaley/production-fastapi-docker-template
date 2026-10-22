<script setup lang="ts">
import { computed } from 'vue'
import { X } from '@lucide/vue'
import AppButton from '../AppButton.vue'
import AppInput from '../AppInput.vue'
import AppSelect from '../AppSelect.vue'
import AppIcon from '../AppIcon.vue'
import AppDataLabel from '../AppDataLabel.vue'
import type { AppControlSize } from '../types/control'
import { appControlStyles, appSelectIconSize } from '~/shared/ui/app/types/control'
import type { AppLabelConfig } from '~/shared/ui/app/types/label-types'
import type { ViewFilterField, FilterValue } from './types'
import { filterIcon, filterLookupLabel } from './filterPresentation'
import ViewFilterDateValue from './ViewFilterDateValue.vue'
const props = withDefaults(
  defineProps<{
    field: ViewFilterField
    modelValue: FilterValue
    lookup: string
    lookups: string[]
    selectedItems?: object[]
    clearable?: boolean
    removable?: boolean
    inline?: boolean
    disabled?: boolean
    locale?: 'ru' | 'en'
    size?: AppControlSize
  }>(),
  { locale: 'ru', size: 'default', removable: true, clearable: true },
)
const emit = defineEmits<{ 'update:modelValue': [value: unknown]; lookup: [value: string]; remove: [] }>()
const hasValue = computed(() =>
  Array.isArray(props.modelValue)
    ? props.modelValue.some((value) => value !== '')
    : props.modelValue !== '' && props.modelValue != null,
)
const english = computed(() => props.locale === 'en')
const iconButtonSize = computed(() => (props.size === 'xs' ? 'icon-xs' : props.size === 'sm' ? 'icon-sm' : 'icon'))
const booleans = computed(() => [
  { id: 'true', name: english.value ? 'Yes' : 'Да' },
  { id: 'false', name: english.value ? 'No' : 'Нет' },
])
function appearance(item: unknown): AppLabelConfig | undefined {
  return (item as { appearance?: AppLabelConfig } | undefined)?.appearance
}
</script>
<template>
  <div
    :style="inline ? { '--filter-height': appControlStyles.input[size].height } : undefined"
    :class="
      inline
        ? 'compound-filter flex max-w-full shrink-0 items-center overflow-hidden rounded-md border border-input bg-background [&_[data-app-select-trigger]]:rounded-none [&_button]:rounded-none [&_button]:focus-visible:ring-inset [&_input]:rounded-none [&_input]:focus-visible:ring-inset'
        : 'grid gap-2 rounded-md border border-border p-3 sm:grid-cols-[1fr_1fr_2fr_auto] sm:items-end'
    "
  >
    <span
      :class="
        inline
          ? 'flex shrink-0 items-center gap-1 px-2 whitespace-nowrap text-foreground'
          : 'flex items-center gap-1 pb-2 text-sm'
      "
      :style="inline ? appControlStyles.selectValue[size] : undefined"
    >
      <AppIcon
        :icon="filterIcon(field)"
        :size="appSelectIconSize[size]"
        class="text-muted-foreground"
      />{{ field.label }}
    </span>
    <span
      v-if="inline"
      class="w-px shrink-0 self-stretch bg-border"
      aria-hidden="true"
    />
    <AppSelect
      :disabled="disabled"
      :variant="inline ? 'ghost' : 'outline'"
      :size="size"
      :class="inline && 'text-muted-foreground'"
      :model-value="lookup"
      :items="lookups.map((id) => ({ id, name: filterLookupLabel(id, locale) }))"
      emit-value
      :clearable="false"
      :locale="locale"
      :aria-label="english ? 'Condition' : 'Условие'"
      @update:model-value="emit('lookup', String($event))"
    />
    <span
      v-if="inline"
      class="w-px shrink-0 self-stretch bg-border"
      aria-hidden="true"
    />
    <AppSelect
      v-if="lookup === 'isnull' || field.kind === 'boolean'"
      :disabled="disabled"
      :clearable="false"
      :variant="inline ? 'ghost' : 'outline'"
      :size="size"
      :class="inline && (hasValue ? 'text-foreground' : 'text-muted-foreground')"
      :model-value="String(modelValue)"
      :items="booleans"
      emit-value
      :locale="locale"
      :aria-label="field.label"
      @update:model-value="emit('update:modelValue', $event === 'true')"
    />
    <AppSelect
      v-else-if="field.kind === 'choice'"
      :disabled="disabled"
      :clearable="false"
      :variant="inline ? 'ghost' : 'outline'"
      :size="size"
      :class="inline && (hasValue ? 'text-foreground' : 'text-muted-foreground')"
      :model-value="(modelValue === '' ? (['in', 'not_in'].includes(lookup) ? [] : null) : modelValue) as never"
      :repo="field.repo"
      :query="field.query"
      :selected-items="selectedItems"
      :items="field.items"
      :item-label="field.itemLabel || 'name'"
      :multiple="['in', 'not_in'].includes(lookup)"
      emit-value
      :locale="locale"
      :aria-label="field.label"
      @update:model-value="emit('update:modelValue', $event)"
    >
      <template #item="{ item, label }">
        <AppDataLabel
          v-if="appearance(item)"
          :config="appearance(item)!"
        /><span v-else>{{ label }}</span>
      </template>
      <template
        v-if="inline"
        #selection="{ selected }"
      >
        <span class="max-w-56 truncate">{{ selected.map((entry) => entry.label).join(', ') }}</span>
      </template>
      <template #selected="{ item, label }">
        <AppDataLabel
          v-if="!inline && appearance(item)"
          :config="appearance(item)!"
        /><span v-else>{{ label }}</span>
      </template>
    </AppSelect>
    <ViewFilterDateValue
      v-else-if="field.kind === 'date' || field.kind === 'datetime'"
      :field="field"
      :lookup="lookup"
      :model-value="modelValue"
      :inline="inline"
      :size="size"
      :locale="locale"
      :disabled="disabled"
      @update:model-value="emit('update:modelValue', $event)"
    />
    <AppInput
      v-else
      :disabled="disabled"
      :size="size"
      :variant="inline ? 'ghost' : 'outline'"
      :model-value="String(modelValue)"
      :type="field.kind === 'number' && !['in', 'not_in'].includes(lookup) ? 'number' : 'text'"
      :aria-label="field.label"
      @update:model-value="
        emit(
          'update:modelValue',
          ['in', 'not_in'].includes(lookup)
            ? String($event)
                .split(',')
                .map((value) => value.trim())
                .filter(Boolean)
            : $event,
        )
      "
    />
    <span
      v-if="inline && removable"
      class="w-px shrink-0 self-stretch bg-border"
      aria-hidden="true"
    />
    <AppButton
      v-if="removable"
      :disabled="disabled"
      variant="ghost"
      :size="inline ? iconButtonSize : size"
      :class="inline && (hasValue ? 'text-foreground' : 'text-muted-foreground')"
      :aria-label="`${english ? 'Remove' : 'Убрать'}: ${field.label}`"
      @click="emit('remove')"
    >
      <AppIcon
        v-if="inline"
        :icon="X"
        :size="appSelectIconSize[size]"
      />
      <template v-else>{{ english ? 'Remove' : 'Убрать' }}</template>
    </AppButton>
  </div>
</template>

<style scoped>
/* The outer frame owns the border; sections fit inside its two border pixels. */
.compound-filter {
  height: var(--filter-height);
}
.compound-filter :deep([data-app-select-trigger]),
.compound-filter :deep(input),
.compound-filter :deep(button) {
  min-height: calc(var(--filter-height) - 2px) !important;
  height: calc(var(--filter-height) - 2px) !important;
}
</style>
