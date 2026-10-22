<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import { Popover, PopoverContent, PopoverTrigger } from '~/shared/ui/shadcn/popover'
import AppButton from '../AppButton.vue'
import AppInput from '../AppInput.vue'
import { maskClockInput } from './format'
import { useOverlayStack } from '../useOverlayStack'
const props = withDefaults(
  defineProps<{ modelValue: string | null; label: string; disabled?: boolean; locale?: 'ru' | 'en'; step?: number }>(),
  { locale: 'ru', step: 15 },
)
const emit = defineEmits<{ 'update:modelValue': [value: string | null]; activate: [] }>()
const open = ref(false)
const draft = ref('')
const dirty = ref(false)
const invalid = ref(false)
const input = ref<InstanceType<typeof AppInput>>()
const { contentStyle } = useOverlayStack(open)
const format = (value: string) => (value.length === 5 ? `${value}:00` : value)
const times = computed(() => {
  const step = Number.isFinite(props.step) ? Math.max(1, Math.min(720, Math.round(props.step))) : 15
  return Array.from({ length: Math.ceil(1440 / step) }, (_, index) => {
    const minutes = index * step
    return `${String(Math.floor(minutes / 60)).padStart(2, '0')}:${String(minutes % 60).padStart(2, '0')}:00`
  })
})
function commit() {
  if (props.disabled || !dirty.value) return !invalid.value
  const value = draft.value.trim()
  invalid.value = !!value && !/^([01]\d|2[0-3]):[0-5]\d(?::[0-5]\d)?$/.test(value)
  if (invalid.value) return false
  dirty.value = false
  emit('update:modelValue', value ? format(value) : null)
  return true
}
watch(
  open,
  (value) => {
    if (value) {
      draft.value = props.modelValue ? format(props.modelValue) : ''
      dirty.value = false
      invalid.value = false
      emit('activate')
    } else commit()
  },
  { flush: 'sync' },
)
function select(value: string | null) {
  dirty.value = false
  invalid.value = false
  emit('update:modelValue', value)
  open.value = false
}
async function focusTime(event: Event) {
  event.preventDefault()
  await nextTick()
  input.value?.focus()
}
function edit(value: string | null) {
  draft.value = maskClockInput(value ?? '', true)
  dirty.value = true
  invalid.value = false
}
defineExpose({ commit })
</script>
<template>
  <Popover v-model:open="open">
    <PopoverTrigger as-child>
      <AppButton
        variant="ghost"
        size="sm"
        :disabled="disabled"
        :aria-label="label"
        class="shrink-0 border-0 px-1.5 font-normal tabular-nums shadow-none hover:bg-field-hover focus-visible:ring-0 focus-visible:ring-offset-0"
        :class="!modelValue && 'text-muted-foreground'"
      >
        {{ modelValue ? format(modelValue) : '00:00:00' }}
      </AppButton>
    </PopoverTrigger>
    <PopoverContent
      align="end"
      :side-offset="6"
      :style="contentStyle"
      class="w-44 overflow-hidden rounded-lg border-border-strong bg-background p-1.5 text-foreground shadow-overlay"
      :aria-label="label"
      @open-auto-focus="focusTime"
    >
      <AppInput
        ref="input"
        :model-value="draft"
        size="sm"
        placeholder="00:00:00"
        :aria-label="label"
        :aria-invalid="invalid"
        inputmode="numeric"
        autocomplete="off"
        :disabled="disabled"
        class="mb-1.5 [&_input]:focus-visible:border-input [&_input]:focus-visible:ring-0"
        maxlength="8"
        @update:model-value="edit"
        @keydown.enter.prevent="commit() && (open = false)"
      />
      <div class="max-h-48 overflow-y-auto overscroll-contain">
        <AppButton
          variant="ghost"
          size="sm"
          class="w-full justify-start font-normal text-muted-foreground"
          @click="select(null)"
        >
          {{ locale === 'en' ? 'No time' : 'Без времени' }}
        </AppButton>
        <AppButton
          v-for="value in times"
          :key="value"
          variant="ghost"
          size="sm"
          class="w-full justify-start font-normal tabular-nums"
          :class="modelValue && format(modelValue) === value && 'bg-accent'"
          @click="select(value)"
        >
          {{ value }}
        </AppButton>
      </div>
    </PopoverContent>
  </Popover>
</template>
