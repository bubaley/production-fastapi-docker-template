<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, shallowRef, watch } from 'vue'
import { getLocalTimeZone, today, type DateValue } from '@internationalized/date'
import { ChevronLeft, ChevronRight, ChevronUp, ChevronDown } from '@lucide/vue'
import * as Calendar from '~/shared/ui/shadcn/calendar'
import AppButton from '../AppButton.vue'
import { calendarValue } from './dateMath'
import { monthAt, monthIndex, monthWindow, monthWeeks, visibleMonthIndex, type CalendarMonth } from './calendarWindow'
import type { DatePickerEndpoint, DatePickerProps, DatePickerRange } from './types'
const props = withDefaults(
  defineProps<
    DatePickerProps & { modelValue?: string | null; range?: DatePickerRange; activeEndpoint?: DatePickerEndpoint }
  >(),
  { mode: 'single', navigation: 'scroll', months: 1, locale: 'ru', activeEndpoint: 'start' },
)
const emit = defineEmits<{ select: [value: string] }>()
const timezone = getLocalTimeZone()
const minDate = computed(() => calendarValue(props.min))
const maxDate = computed(() => calendarValue(props.max))
const singleDate = computed(() => calendarValue(props.modelValue))
const startDate = computed(() => calendarValue(props.range?.start))
const endDate = computed(() => calendarValue(props.range?.end))
function initial() {
  const value = (props.mode === 'range' ? startDate.value : singleDate.value) || today(timezone)
  return minDate.value && value.compare(minDate.value) < 0
    ? minDate.value
    : maxDate.value && value.compare(maxDate.value) > 0
      ? maxDate.value
      : value
}
const focusDate = shallowRef<DateValue>(initial())
const cursor = ref(monthIndex(initial()))
const window = shallowRef(monthWindow(cursor.value))
const viewport = ref<HTMLElement>()
const top = ref(window.value.months[cursor.value - window.value.first]!.top)
const viewportHeight = ref(320)
const localeCode = computed(() => (props.locale === 'en' ? 'en-GB' : 'ru-RU'))
const formatter = computed(() => new Intl.DateTimeFormat(localeCode.value, { month: 'long', year: 'numeric' }))
const weekdays = computed(() => {
  const format = new Intl.DateTimeFormat(localeCode.value, { weekday: 'short' })
  return Array.from({ length: 7 }, (_, i) => format.format(new Date(2026, 0, 5 + i)))
})
const title = (value: DateValue) => formatter.value.format(value.toDate(timezone))
const rangeSelection = computed(() => {
  const start = startDate.value
  const end = endDate.value
  if (props.mode !== 'range' || !start || !end) return null
  return start.compare(end) <= 0 ? { start, end } : { start: end, end: start }
})
const selected = computed(() =>
  props.mode === 'single'
    ? singleDate.value
      ? [singleDate.value]
      : []
    : [startDate.value, endDate.value].filter((v): v is NonNullable<typeof v> => Boolean(v)),
)
const visible = computed(() => {
  if (props.navigation === 'paged') {
    const current = monthWindow(cursor.value)
    return current.months.slice(cursor.value - current.first, cursor.value - current.first + props.months)
  }
  const first = Math.max(0, visibleMonthIndex(window.value.months, top.value) - 1)
  const last = Math.min(
    window.value.months.length,
    visibleMonthIndex(window.value.months, top.value + viewportHeight.value) + 2,
  )
  return window.value.months.slice(first, last)
})
// Cache calendar geometry by month. Selection changes never regenerate dates or Intl formatters.
const weekCache = new Map<string, ReturnType<typeof monthWeeks>>()
function weeks(month: CalendarMonth) {
  let result = weekCache.get(month.key)
  if (!result) {
    result = monthWeeks(month)
    weekCache.set(month.key, result)
    if (weekCache.size > 24) weekCache.delete(weekCache.keys().next().value!)
  }
  return result
}
const inRange = (day: DateValue) => {
  const range = rangeSelection.value
  return Boolean(range && day.compare(range.start) >= 0 && day.compare(range.end) <= 0)
}
const isEndpoint = (day: DateValue) => selected.value.some((value) => value.compare(day) === 0)
const rangeBandClasses = (day: DateValue) => {
  const range = rangeSelection.value
  if (!range || !inRange(day)) return []
  const weekday = day.calendar.toJulianDay(day) % 7
  const startsRange = day.compare(range.start) === 0
  const endsRange = day.compare(range.end) === 0
  const startsWeek = weekday === 0
  const endsWeek = weekday === 6
  return [
    'before:absolute before:inset-y-0 before:bg-secondary',
    startsRange || (endsRange && startsWeek) ? 'before:left-1/2' : 'before:left-0',
    endsRange || (startsRange && endsWeek) ? 'before:right-1/2' : 'before:right-0',
    startsWeek && 'before:rounded-l-md',
    endsWeek && 'before:rounded-r-md',
  ]
}
const blocked = (day: DateValue) =>
  Boolean(
    props.disabled ||
    props.readonly ||
    (minDate.value && day.compare(minDate.value) < 0) ||
    (maxDate.value && day.compare(maxDate.value) > 0),
  )
function choose(day: DateValue) {
  if (!blocked(day)) {
    focusDate.value = day
    emit('select', day.toString())
  }
}
let frame = 0
let observer: ResizeObserver | undefined
let disposed = false
function onScroll() {
  if (frame || props.navigation !== 'scroll') return
  frame = requestAnimationFrame(() => {
    frame = 0
    const el = viewport.value
    if (!el) return
    top.value = el.scrollTop
    const index = visibleMonthIndex(window.value.months, top.value + viewportHeight.value * 0.4)
    const nextCursor = window.value.first + index
    if (cursor.value !== nextCursor && !el.contains(document.activeElement)) focusDate.value = monthAt(nextCursor)
    cursor.value = nextCursor
    // Rebase the spacer only once per ~10 years, never at each visible month boundary.
    if (
      (index < 6 && window.value.first > 0) ||
      (index > window.value.months.length - 7 && window.value.first + window.value.months.length < 9999 * 12)
    )
      void rebase(cursor.value)
  })
}
async function rebase(center: number) {
  const anchorIndex = visibleMonthIndex(window.value.months, top.value)
  const anchor = window.value.months[anchorIndex]!
  const offset = top.value - anchor.top
  window.value = monthWindow(center)
  weekCache.clear()
  const nextAnchor = window.value.months[monthIndex(anchor.value) - window.value.first]
  top.value = (nextAnchor?.top || 0) + offset
  await nextTick()
  if (!disposed && viewport.value) viewport.value.scrollTop = top.value
}
async function jump(day: DateValue, focus = false) {
  cursor.value = monthIndex(day)
  focusDate.value = day
  if (props.navigation === 'scroll') {
    if (cursor.value < window.value.first || cursor.value >= window.value.first + window.value.months.length) {
      window.value = monthWindow(cursor.value)
      weekCache.clear()
    }
    top.value = window.value.months[cursor.value - window.value.first]!.top
    await nextTick()
    if (!disposed && viewport.value) viewport.value.scrollTop = top.value
  }
  await nextTick()
  if (focus && !disposed)
    viewport.value
      ?.querySelector<HTMLElement>(`[data-value="${day.toString()}"]:not([data-outside-view])`)
      ?.focus({ preventScroll: false })
}
function reveal(value: string | null | undefined) {
  const date = calendarValue(value)
  if (date) void jump(date)
}
async function keyboard(event: KeyboardEvent, day: DateValue) {
  if (event.altKey || event.ctrlKey || event.metaKey || blocked(day)) return
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault()
    event.stopPropagation()
    choose(day)
    return
  }
  const weekday = day.calendar.toJulianDay(day) % 7
  const amount = { ArrowLeft: -1, ArrowRight: 1, ArrowUp: -7, ArrowDown: 7, Home: -weekday, End: 6 - weekday }[
    event.key
  ]
  let target: DateValue
  if (amount !== undefined) target = day.add({ days: amount })
  else if (event.key === 'PageUp' || event.key === 'PageDown')
    target = day.add({ months: (event.key === 'PageUp' ? -1 : 1) * (event.shiftKey ? 12 : 1) })
  else return
  event.preventDefault()
  event.stopPropagation()
  if (blocked(target)) return
  focusDate.value = target
  const targetElement = viewport.value?.querySelector<HTMLElement>(
    `[data-value="${target.toString()}"]:not([data-outside-view])`,
  )
  if (targetElement) targetElement.focus()
  else await jump(target, true)
}
watch(
  () => [props.navigation, props.months, props.min, props.max, props.mode],
  () => void jump(initial()),
)
watch(
  () => (props.mode === 'single' ? [props.modelValue] : [props.range?.start, props.range?.end]),
  (values, previous) => {
    const index = props.mode === 'range' && props.activeEndpoint === 'end' ? 1 : 0
    if (values[index] === previous?.[index]) return
    const value = values[index]
    const date = calendarValue(value)
    if (!date) return
    const target = monthIndex(date)
    if (!visible.value.some((month) => monthIndex(month.value) === target)) void jump(date)
  },
)
defineExpose({ reveal })
onMounted(() => {
  observer = new ResizeObserver((entries) => {
    viewportHeight.value = entries[0]?.contentRect.height || 320
  })
  if (viewport.value) observer.observe(viewport.value)
  void jump(initial())
})
onBeforeUnmount(() => {
  disposed = true
  cancelAnimationFrame(frame)
  observer?.disconnect()
})
</script>
<template>
  <div class="flex min-h-0 min-w-0 flex-1 flex-col p-3">
    <header class="mb-3 flex shrink-0 items-center gap-1">
      <span
        class="mr-auto text-sm font-semibold capitalize"
        aria-live="polite"
        >{{ title(monthAt(cursor)) }}</span
      >
      <AppButton
        size="sm"
        variant="ghost"
        :disabled="disabled"
        @click="jump(today(timezone))"
      >
        {{ locale === 'en' ? 'Today' : 'Сегодня' }}
      </AppButton>
      <AppButton
        size="icon-sm"
        variant="ghost"
        :icon="navigation === 'scroll' ? ChevronUp : ChevronLeft"
        :disabled="disabled || cursor <= 0"
        :aria-label="locale === 'en' ? 'Previous month' : 'Предыдущий месяц'"
        @click="jump(monthAt(cursor - 1))"
      />
      <AppButton
        size="icon-sm"
        variant="ghost"
        :icon="navigation === 'scroll' ? ChevronDown : ChevronRight"
        :disabled="disabled || cursor >= 9999 * 12 - 1"
        :aria-label="locale === 'en' ? 'Next month' : 'Следующий месяц'"
        @click="jump(monthAt(cursor + 1))"
      />
    </header>
    <div
      ref="viewport"
      class="relative min-h-0 [scrollbar-width:none] overflow-y-auto overscroll-contain [overflow-anchor:none] [&::-webkit-scrollbar]:hidden"
      :class="navigation === 'scroll' && 'h-[320px]'"
      @scroll.passive="onScroll"
    >
      <Calendar.CalendarRoot
        :model-value="selected"
        multiple
        :placeholder="focusDate"
        :locale="localeCode"
        :week-starts-on="1"
        :disabled="disabled"
        :readonly="readonly"
        :min-value="minDate"
        :max-value="maxDate"
        :calendar-label="locale === 'en' ? 'Choose date' : 'Выбор даты'"
      >
        <div
          class="relative"
          :class="navigation === 'paged' && 'flex flex-col gap-4 sm:flex-row'"
          :style="navigation === 'scroll' ? { height: `${window.height}px` } : undefined"
        >
          <section
            v-for="month in visible"
            :key="month.key"
            :data-picker-month="month.key"
            class="min-w-0"
            :class="navigation === 'scroll' ? 'absolute inset-x-0' : 'flex-1'"
            :style="{ height: `${month.height}px`, ...(navigation === 'scroll' ? { top: `${month.top}px` } : {}) }"
          >
            <h4 class="m-0 flex h-7 items-start text-xs font-medium text-muted-foreground capitalize">
              {{ title(month.value) }}
            </h4>
            <Calendar.CalendarGrid
              class="w-full border-collapse"
              :aria-label="title(month.value)"
            >
              <Calendar.CalendarGridHead>
                <Calendar.CalendarGridRow class="flex h-6 w-full">
                  <Calendar.CalendarHeadCell
                    v-for="(day, index) in weekdays"
                    :key="index"
                    class="flex-1 text-center text-xs text-muted-foreground"
                  >
                    {{ day }}
                  </Calendar.CalendarHeadCell>
                </Calendar.CalendarGridRow>
              </Calendar.CalendarGridHead>
              <Calendar.CalendarGridBody>
                <Calendar.CalendarGridRow
                  v-for="(week, index) in weeks(month)"
                  :key="index"
                  class="flex h-10 w-full items-center"
                >
                  <Calendar.CalendarCell
                    v-for="day in week"
                    :key="day.toString()"
                    :date="day"
                    class="relative flex h-9 min-w-0 flex-1 items-center justify-center [&:has([data-selected])]:bg-transparent [&:has([data-selected][data-outside-view])]:bg-transparent"
                    :class="[day.month !== month.value.month && 'pointer-events-none invisible', rangeBandClasses(day)]"
                    :aria-selected="inRange(day) || isEndpoint(day)"
                    :data-in-range="inRange(day) || undefined"
                  >
                    <Calendar.CalendarCellTrigger
                      :day="day"
                      :month="month.value"
                      class="relative z-10 h-9 w-9 shrink-0 rounded-md text-sm transition-none data-[selected]:bg-white data-[selected]:text-neutral-950 data-[selected]:hover:bg-white data-[selected]:hover:text-neutral-950 data-[selected]:focus:bg-white data-[selected]:focus:text-neutral-950"
                      :class="[
                        isEndpoint(day) && 'bg-white text-neutral-950 hover:bg-white hover:text-neutral-950',
                        inRange(day) && '[&[data-today]:not([data-selected])]:bg-transparent',
                      ]"
                      :aria-pressed="inRange(day) || isEndpoint(day)"
                      @click="choose(day)"
                      @keydown.capture="keyboard($event, day)"
                    />
                  </Calendar.CalendarCell>
                </Calendar.CalendarGridRow>
              </Calendar.CalendarGridBody>
            </Calendar.CalendarGrid>
          </section>
        </div>
      </Calendar.CalendarRoot>
    </div>
  </div>
</template>
