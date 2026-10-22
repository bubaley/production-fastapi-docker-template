<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import AppButton from '../AppButton.vue'
import DateTimeField from './DateTimeField.vue'
import PickerCalendar from './PickerCalendar.vue'
import { localDateValue, validatePickerValues } from './dateMath'
import { DEFAULT_DATE_MASK } from './format'
import { finishCalendarRange, replaceCalendarDay } from './selection'
import type { DatePickerEndpoint, DatePickerProps, DatePickerRange } from './types'
const props = withDefaults(defineProps<DatePickerProps>(), {
  mode: 'single',
  locale: 'ru',
  mask: DEFAULT_DATE_MASK,
  applyMode: 'auto',
  navigation: 'scroll',
  months: 1,
})
const model = defineModel<string | null>({ default: null })
const range = defineModel<DatePickerRange>('range', { default: () => ({ start: null, end: null }) })
const emit = defineEmits<{ apply: [] }>()
const start = ref<string | null>(null)
const end = ref<string | null>(null)
const active = ref<DatePickerEndpoint>('start')
const validationError = ref('')
const startField = ref<InstanceType<typeof DateTimeField>>()
const endField = ref<InstanceType<typeof DateTimeField>>()
const calendar = ref<InstanceType<typeof PickerCalendar>>()
const en = computed(() => props.locale === 'en')
const locked = computed(() => props.disabled || props.readonly)
const draftRange = computed(() => ({ start: start.value, end: end.value }))
let previousEnd: string | null = null
function sync() {
  start.value = props.mode === 'range' ? range.value.start : model.value
  end.value = range.value.end
  previousEnd = end.value
  validationError.value = ''
}
watch(() => [model.value, range.value.start, range.value.end, props.mode], sync, { immediate: true })
function validation() {
  if (!start.value && (props.mode === 'single' || !end.value)) return null
  return validatePickerValues(props.mode === 'range' ? [start.value, end.value] : [start.value], props)
}
function commit(showError = true) {
  if (locked.value) return false
  const invalid = validation()
  if (invalid) {
    if (showError && invalid !== 'invalid')
      validationError.value =
        invalid === 'order'
          ? en.value
            ? 'End must be on or after start.'
            : 'Окончание должно быть не раньше начала.'
          : invalid === 'bounds'
            ? en.value
              ? 'Date is outside the allowed interval.'
              : 'Дата за пределами допустимого интервала.'
            : en.value
              ? 'Enter both dates in the specified format.'
              : 'Введите даты в указанном формате.'
    return false
  }
  validationError.value = ''
  if (props.mode === 'range') {
    if (range.value.start !== start.value || range.value.end !== end.value)
      range.value = { start: start.value, end: end.value }
  } else if (model.value !== start.value) model.value = start.value
  return true
}
function autoCommit(showError = true) {
  validationError.value = ''
  if (props.applyMode === 'auto') commit(showError && !(props.mode === 'range' && (!start.value || !end.value)))
}
function apply() {
  const firstValid = startField.value?.commit() ?? true
  const lastValid = endField.value?.commit() ?? true
  if (firstValid && lastValid && commit()) emit('apply')
}
function commitOnClose() {
  if (locked.value) return
  const firstValid = startField.value?.commit() ?? true
  const lastValid = endField.value?.commit() ?? true
  if (firstValid && lastValid && commit(false)) return
  if (props.mode === 'range') range.value = { start: null, end: null }
  else model.value = null
}
defineExpose({ commitOnClose })
function clear() {
  if (locked.value) return
  start.value = null
  end.value = null
  previousEnd = null
  active.value = 'start'
  startField.value?.reset(start.value)
  endField.value?.reset(end.value)
  autoCommit()
}
function navigate(endpoint: DatePickerEndpoint) {
  calendar.value?.reveal(endpoint === 'start' ? start.value : end.value)
}
function selectDate(day: string) {
  if (locked.value) return
  if (props.mode === 'single') {
    start.value = replaceCalendarDay(day, start.value, props.time)
    startField.value?.reset(start.value)
    autoCommit()
    return
  }
  if (active.value === 'start' || !start.value) {
    previousEnd = end.value || previousEnd
    start.value = replaceCalendarDay(day, start.value, props.time)
    active.value = 'end'
    startField.value?.reset(start.value)
    validationError.value = ''
    if (props.allowPartial) autoCommit()
  } else {
    const previousStart = start.value
    const next = finishCalendarRange(start.value, replaceCalendarDay(day, end.value || previousEnd, props.time))
    start.value = next.start
    end.value = next.end
    if (start.value !== previousStart) startField.value?.reset(start.value)
    endField.value?.reset(end.value)
    autoCommit()
  }
}
const presets = computed(() =>
  props.smart && props.mode === 'range'
    ? [
        ['5m', en.value ? 'Last 5 minutes' : 'Последние 5 минут'],
        ['30m', en.value ? 'Last 30 minutes' : 'Последние 30 минут'],
        ['1h', en.value ? 'Last hour' : 'Последний час'],
        ['2h', en.value ? 'Last 2 hours' : 'Последние 2 часа'],
        ['6h', en.value ? 'Last 6 hours' : 'Последние 6 часов'],
        ['24h', en.value ? 'Last 24 hours' : 'Последние 24 часа'],
        ['7d', en.value ? 'Last 7 days' : 'Последние 7 дней'],
        ['30d', en.value ? 'Last 30 days' : 'Последние 30 дней'],
      ]
    : [
        ['0', en.value ? 'Today' : 'Сегодня'],
        ['1', en.value ? 'Tomorrow' : 'Завтра'],
        ['7', en.value ? 'In a week' : 'Через неделю'],
        ['14', en.value ? 'In two weeks' : 'Через две недели'],
      ],
)
function preset(key: string) {
  if (locked.value) return
  if (props.smart && props.mode === 'range') {
    start.value = `now-${key}`
    end.value = 'now'
  } else {
    const date = new Date()
    date.setDate(date.getDate() + Number(key))
    start.value = replaceCalendarDay(localDateValue(date), start.value, props.time)
    if (props.mode === 'range') end.value = replaceCalendarDay(localDateValue(date), end.value, props.time)
  }
  startField.value?.reset(start.value)
  if (props.mode === 'range') endField.value?.reset(end.value)
  autoCommit()
}
</script>
<template>
  <section
    class="flex w-full flex-col overflow-hidden rounded-xl border border-overlay-border bg-background text-foreground"
    :class="!inline && 'max-h-[min(90dvh,var(--reka-popover-content-available-height,90dvh))]'"
    :aria-label="en ? 'Date picker' : 'Выбор даты'"
  >
    <div
      class="grid shrink-0 gap-2 border-b border-border p-3"
      :class="mode === 'range' && 'sm:grid-cols-2'"
    >
      <DateTimeField
        ref="startField"
        v-bind="props"
        v-model="start"
        :label="mode === 'single' ? (en ? 'Date' : 'Дата') : en ? 'Start date' : 'Дата начала'"
        :active="active === 'start'"
        @activate="active = 'start'"
        @navigate="navigate('start')"
        @commit="autoCommit"
      />
      <DateTimeField
        v-if="mode === 'range'"
        v-bind="props"
        :id="id ? `${id}-end` : undefined"
        ref="endField"
        v-model="end"
        :label="en ? 'End date' : 'Дата конца'"
        :active="active === 'end'"
        @activate="active = 'end'"
        @navigate="navigate('end')"
        @commit="autoCommit"
      />
    </div>
    <div class="flex min-h-0 flex-1 flex-col sm:flex-row">
      <aside
        v-if="smart"
        class="flex shrink-0 gap-1 overflow-x-auto border-b border-border p-3 sm:w-44 sm:flex-col sm:border-r sm:border-b-0"
        :aria-label="en ? 'Quick selection' : 'Быстрый выбор'"
      >
        <AppButton
          v-for="[key, label] in presets"
          :key="key"
          variant="ghost"
          size="sm"
          class="justify-start text-left"
          :class="start === `now-${key}` && 'bg-primary/10 text-primary'"
          :disabled="locked"
          @click="preset(key!)"
        >
          {{ label }}
        </AppButton>
      </aside>
      <div class="flex min-h-0 min-w-0 flex-1 flex-col">
        <PickerCalendar
          ref="calendar"
          v-bind="props"
          :model-value="start"
          :range="draftRange"
          :active-endpoint="active"
          @select="selectDate"
        />
      </div>
    </div>
    <p
      v-if="validationError"
      role="alert"
      class="m-0 shrink-0 px-3 py-2.5 text-xs text-destructive"
    >
      {{ validationError }}
    </p>
    <footer
      v-if="applyMode === 'manual'"
      class="flex shrink-0 items-center justify-between gap-3 border-t border-border px-3 py-2.5"
    >
      <AppButton
        variant="ghost"
        size="sm"
        :disabled="locked"
        @click="clear"
      >
        {{ en ? 'Clear' : 'Очистить' }}
      </AppButton>
      <AppButton
        :disabled="locked"
        size="sm"
        @click="apply"
      >
        {{ en ? 'Apply' : 'Применить' }}
      </AppButton>
    </footer>
  </section>
</template>
