<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import dayjs from 'dayjs'
import { ChevronLeft, ChevronRight } from '@lucide/vue'
import AppButton from './AppButton.vue'
const model = defineModel<string | null>()
const props = withDefaults(defineProps<{ eventDates?: string[]; locale?: 'ru' | 'en'; disabled?: boolean }>(), {
  locale: 'ru'
})
const emit = defineEmits<{ navigation: [value: { year: number; month: number }] }>()
const month = ref(dayjs(model.value || undefined).startOf('month'))
const weekdays = computed(() =>
  props.locale === 'en' ? ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'] : ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
)
const title = computed(() => month.value.toDate().toLocaleDateString(props.locale, { month: 'long', year: 'numeric' }))
const days = computed(() => {
  const first = month.value.subtract((month.value.day() + 6) % 7, 'day')
  return Array.from({ length: 42 }, (_, i) => first.add(i, 'day'))
})
const events = computed(() => new Set(props.eventDates?.map((date) => date.replaceAll('/', '-'))))
watch(model, (value) => {
  if (value && dayjs(value).isValid()) month.value = dayjs(value).startOf('month')
})
watch(month, (value) => emit('navigation', { year: value.year(), month: value.month() + 1 }))
</script>
<template>
  <section
    class="w-[300px] rounded-lg border border-border bg-card p-3"
    :aria-label="locale === 'en' ? 'Calendar' : 'Календарь'"
  >
    <header class="mb-3 flex items-center justify-between gap-2">
      <AppButton
        :icon="ChevronLeft"
        variant="ghost"
        size="icon-sm"
        :aria-label="locale === 'en' ? 'Previous month' : 'Предыдущий месяц'"
        @click="month = month.subtract(1, 'month')"
      /><span
        class="text-sm font-medium"
        aria-live="polite"
      >{{ title }}</span><AppButton
        :icon="ChevronRight"
        variant="ghost"
        size="icon-sm"
        :aria-label="locale === 'en' ? 'Next month' : 'Следующий месяц'"
        @click="month = month.add(1, 'month')"
      />
    </header>
    <div class="grid grid-cols-7 gap-1">
      <span
        v-for="day in weekdays"
        :key="day"
        class="pb-2 text-center text-xs text-muted-foreground"
      >{{ day }}</span><button
        v-for="day in days"
        :key="day.format('YYYY-MM-DD')"
        type="button"
        :disabled="disabled"
        class="relative flex aspect-square items-center justify-center rounded text-xs hover:bg-accent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:opacity-50"
        :class="[
          day.format('YYYY-MM-DD') === model
            ? 'bg-primary text-primary-foreground'
            : day.month() !== month.month()
              ? 'text-muted-foreground/50'
              : 'text-foreground',
          day.isSame(dayjs(), 'day') && 'ring-1 ring-inset ring-primary'
        ]"
        :aria-pressed="day.format('YYYY-MM-DD') === model"
        :aria-label="day.toDate().toLocaleDateString(locale, { dateStyle: 'full' })"
        @click="model = day.format('YYYY-MM-DD')"
      >
        {{ day.date()
        }}<span
          v-if="events.has(day.format('YYYY-MM-DD'))"
          class="absolute bottom-1 size-1 rounded-full bg-current"
          :aria-label="locale === 'en' ? 'Has reminders' : 'Есть напоминания'"
        />
      </button>
    </div>
  </section>
</template>
