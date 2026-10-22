<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { CalendarDays } from '@lucide/vue'
import { Input } from '~/shared/ui/shadcn/input'
import AppField from '../AppField.vue'
import AppClearButton from '../AppClearButton.vue'
import AppIcon from '../AppIcon.vue'
import PickerTimeSelect from './PickerTimeSelect.vue'
import { appInputSizeClasses } from '../types/control'
import { DEFAULT_DATE_MASK, formatPickerValue, parsePickerText } from './format'
import type { DatePickerProps } from './types'
const props = withDefaults(defineProps<DatePickerProps & { active?: boolean; label: string }>(), {
  locale: 'ru',
  mask: DEFAULT_DATE_MASK,
  timeStep: 15,
})
const model = defineModel<string | null>({ default: null })
const emit = defineEmits<{ activate: []; commit: []; navigate: [] }>()
const text = ref('')
const timePicker = ref<InstanceType<typeof PickerTimeSelect>>()
const timeLocked = computed(() => locked.value || !model.value || model.value.startsWith('now'))
const inputRef = ref<{ $el: HTMLInputElement }>()
const locked = computed(() => props.disabled || props.readonly)
const display = () => formatPickerValue(model.value, props.mask, false, props.locale)
watch(
  () => [model.value, props.mask, props.time, props.locale],
  () => {
    text.value = display()
  },
  { immediate: true },
)
const selectedTime = computed(() => (model.value?.includes('T') ? model.value.split('T')[1]! : null))
function commitDate() {
  if (locked.value) return true
  let parsed = parsePickerText(text.value, props.mask, props.time, props.locale, props.smart)
  if (parsed === undefined) {
    emit('commit')
    return false
  }
  if (parsed && !parsed.includes('T') && !parsed.startsWith('now') && props.time && selectedTime.value)
    parsed = `${parsed}T${selectedTime.value}`
  if (parsed !== model.value) model.value = parsed
  emit('commit')
  text.value = formatPickerValue(parsed, props.mask, false, props.locale)
  return true
}
function commit() {
  const validDate = commitDate()
  const validTime = timePicker.value?.commit() ?? true
  return validDate && validTime
}
function selectTime(value: string | number | null | undefined) {
  if (locked.value || !commitDate() || !model.value || model.value.startsWith('now')) return
  const date = model.value.split('T')[0]!
  model.value = value && value !== 'none' ? `${date}T${value}` : date
  emit('commit')
}
function reset(value = model.value) {
  text.value = formatPickerValue(value, props.mask, false, props.locale)
}
function prepareNavigation(event: PointerEvent) {
  if (document.activeElement === event.currentTarget) emit('navigate')
}
function blurDate() {
  commit()
}
function clear() {
  if (locked.value) return
  model.value = null
  text.value = ''
  emit('commit')
  inputRef.value?.$el.focus()
}
defineExpose({ commit, reset })
</script>
<template>
  <AppField :id="id">
    <template #default="field">
      <div
        class="flex min-w-0 items-center gap-2 rounded-md border bg-secondary text-secondary-foreground shadow-none transition-colors hover:bg-accent"
        :class="[
          appInputSizeClasses.md,
          mode === 'range' && active ? 'border-foreground/80' : 'border-transparent',
          disabled && 'opacity-50',
        ]"
        :data-active="active || undefined"
        @focusin="emit('activate')"
      >
        <AppIcon
          :icon="CalendarDays"
          size="sm"
          class="shrink-0 text-muted-foreground"
        />
        <span class="group/input relative flex min-w-0 flex-1 items-center">
          <Input
            :id="field.id"
            ref="inputRef"
            v-model="text"
            type="text"
            :placeholder="label"
            :disabled="disabled"
            :readonly="readonly"
            :aria-label="label"
            :aria-describedby="[describedBy, field.describedBy].filter(Boolean).join(' ') || undefined"
            :aria-invalid="!!error || undefined"
            :aria-required="required || undefined"
            autocomplete="off"
            class="h-full min-w-0 flex-1 rounded-none border-0 bg-transparent p-0 text-inherit shadow-none focus-visible:border-transparent focus-visible:ring-0 enabled:hover:bg-transparent"
            @pointerdown="prepareNavigation"
            @blur="blurDate"
            @keydown.enter.prevent="commit"
          />
          <AppClearButton
            v-if="clearable && model && !locked"
            :active="mode === 'range' && active"
            :label="locale === 'en' ? 'Clear' : 'Очистить'"
            class="pointer-events-none absolute right-0 opacity-0 transition-opacity group-focus-within/input:pointer-events-auto group-focus-within/input:opacity-100 group-hover/input:pointer-events-auto group-hover/input:opacity-100"
            @click="clear"
          />
        </span>
        <PickerTimeSelect
          v-if="time"
          ref="timePicker"
          :model-value="selectedTime"
          :step="timeStep"
          :locale="locale"
          :label="`${label}: ${locale === 'en' ? 'time' : 'время'}`"
          :disabled="timeLocked"
          @update:model-value="selectTime"
          @activate="emit('activate')"
        />
      </div>
    </template>
  </AppField>
</template>
