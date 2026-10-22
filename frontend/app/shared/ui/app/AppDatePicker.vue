<script setup lang="ts">
import { useOverlayStack } from './useOverlayStack'
import { computed, ref, watch } from 'vue'
import { CalendarDays } from '@lucide/vue'
import { Popover, PopoverContent, PopoverTrigger } from '~/shared/ui/shadcn/popover'
import AppButton from './AppButton.vue'
import AppField from './AppField.vue'
import PickerPanel from './date-picker/PickerPanel.vue'
import { DEFAULT_DATE_MASK, formatPickerValue } from './date-picker/format'
import type { DatePickerProps, DatePickerRange, DatePickerTriggerBindings } from './date-picker/types'
export type CDatePickerChangeData = { startDate: string | null; endDate: string | null; dates: string[] }
export type AppDatePickerProps = DatePickerProps & {
  selectionMode?: 'single' | 'range'
  data?: CDatePickerChangeData | null
  startDate?: string | null
  endDate?: string | null
}
const emit = defineEmits<{
  'update:data': [value: CDatePickerChangeData]
  'update:startDate': [value: string | null]
  'update:endDate': [value: string | null]
}>()
const props = withDefaults(defineProps<AppDatePickerProps>(), {
  mode: 'single',
  navigation: 'scroll',
  months: 1,
  locale: 'ru',
  mask: DEFAULT_DATE_MASK,
  applyMode: 'auto',
})
const legacyModel = defineModel<string | (string | null)[] | null>({ default: null })
const effectiveMode = computed(() => props.selectionMode ?? props.mode)
const notify = (start: string | null, end: string | null) => {
  emit('update:startDate', start)
  emit('update:endDate', end)
  emit('update:data', {
    startDate: start,
    endDate: end,
    dates: [start, end].filter((value, index, all): value is string => value !== null && all.indexOf(value) === index),
  })
}
const model = computed({
  get: () =>
    props.data?.dates[0] ?? (typeof legacyModel.value === 'string' ? legacyModel.value : (props.startDate ?? null)),
  set: (value: string | null) => {
    legacyModel.value = value
    notify(value, value)
  },
})
const rangeModel = defineModel<DatePickerRange>('range', { default: () => ({ start: null, end: null }) })
const range = computed({
  get: () =>
    props.selectionMode === 'range'
      ? {
          start:
            props.data?.startDate ??
            (Array.isArray(legacyModel.value) ? legacyModel.value[0] : props.startDate) ??
            null,
          end: props.data?.endDate ?? (Array.isArray(legacyModel.value) ? legacyModel.value[1] : props.endDate) ?? null,
        }
      : rangeModel.value,
  set: (value: DatePickerRange) => {
    rangeModel.value = value
    if (props.selectionMode === 'range') legacyModel.value = [value.start, value.end]
    notify(value.start, value.end)
  },
})
const panel = ref<InstanceType<typeof PickerPanel>>()
const open = defineModel<boolean>('open', { default: false })
watch(
  open,
  (value, previous) => {
    if (!value && previous && props.applyMode === 'close') panel.value?.commitOnClose()
  },
  { flush: 'sync' },
)
const { contentStyle: overlayStyle } = useOverlayStack(open)
defineSlots<{ trigger(props: DatePickerTriggerBindings): unknown }>()
const valueLabel = computed(() =>
  (effectiveMode.value === 'range' ? [range.value.start, range.value.end] : [model.value])
    .filter(Boolean)
    .map((value) => formatPickerValue(value, props.mask, props.time, props.locale))
    .join(' - '),
)
const triggerBindings = computed<DatePickerTriggerBindings>(() => ({
  mode: effectiveMode.value,
  modelValue: model.value,
  range: range.value,
  value: effectiveMode.value === 'range' ? range.value : model.value,
  formattedValue: valueLabel.value,
  open: open.value,
  disabled: Boolean(props.disabled),
  readonly: Boolean(props.readonly),
}))
const width = computed(
  () =>
    (props.navigation === 'paged' && props.months === 2
      ? 616
      : props.time && effectiveMode.value === 'range'
        ? 288
        : effectiveMode.value === 'single'
          ? 340
          : 360) + (props.smart ? 168 : 0),
)
</script>
<template>
  <AppField
    :id="id"
    :label="label"
    :hint="hint"
    :error="error"
  >
    <template #default="field">
      <template v-if="name">
        <input
          v-if="effectiveMode === 'single'"
          type="hidden"
          :name="name"
          :value="model || ''"
          :disabled="disabled"
        />
        <template v-else>
          <input
            type="hidden"
            :name="`${name}-start`"
            :value="range.start || ''"
            :disabled="disabled"
          />
          <input
            type="hidden"
            :name="`${name}-end`"
            :value="range.end || ''"
            :disabled="disabled"
          />
        </template>
      </template>
      <PickerPanel
        v-if="inline"
        v-bind="props"
        :id="field.id"
        v-model="model"
        v-model:range="range"
        :mode="effectiveMode"
        :described-by="field.describedBy"
        :style="{ maxWidth: `${width}px` }"
      />
      <Popover
        v-else
        v-model:open="open"
      >
        <PopoverTrigger as-child>
          <slot
            name="trigger"
            v-bind="{
              ...triggerBindings,
              id: field.id,
              'aria-describedby': field.describedBy,
              'aria-invalid': !!error || undefined,
            }"
          >
            <AppButton
              :id="field.id"
              variant="outline"
              :icon="CalendarDays"
              :disabled="disabled"
              :aria-readonly="readonly || undefined"
              :aria-required="required || undefined"
              :aria-invalid="!!error || undefined"
              :aria-describedby="field.describedBy"
              class="w-full justify-start font-normal"
              :aria-label="label || (locale === 'en' ? 'Choose date' : 'Выбрать дату')"
            >
              <span
                class="truncate"
                :class="!valueLabel && 'text-muted-foreground'"
                >{{ valueLabel || placeholder || (locale === 'en' ? 'Choose date' : 'Выбрать дату') }}</span
              >
            </AppButton>
          </slot>
        </PopoverTrigger>
        <PopoverContent
          align="start"
          :aria-label="label || (locale === 'en' ? 'Choose date' : 'Выбор даты')"
          :side-offset="6"
          :collision-padding="12"
          class="max-h-[min(90dvh,var(--reka-popover-content-available-height))] w-auto max-w-[calc(100vw-24px)] overflow-y-auto rounded-xl border-0 bg-transparent p-0 shadow-xl"
          :style="{ width: `${width}px`, ...overlayStyle }"
        >
          <PickerPanel
            v-bind="props"
            :id="`${field.id}-input`"
            ref="panel"
            v-model="model"
            v-model:range="range"
            :mode="effectiveMode"
            :described-by="field.describedBy"
            @apply="open = false"
          />
        </PopoverContent>
      </Popover>
    </template>
  </AppField>
</template>
