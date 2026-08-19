<template>
  <div class="smart-date-picker w-full">
    <div
      class="input-row"
      :class="{ 'input-row--labeled': Boolean(label) }"
    >
      <AppInput
        v-if="label"
        v-model="text"
        class="flex-1"
        :label="label"
        :placeholder="placeholder"
        :invalid="Boolean(error)"
        @keydown.enter.prevent="validate"
        @blur="validate"
      />
      <InputText
        v-else
        v-model="text"
        class="flex-1"
        :placeholder="placeholder"
        :invalid="Boolean(error)"
        @keydown.enter.prevent="validate"
        @blur="validate"
      />
      <AppButton
        severity="secondary"
        variant="outlined"
        icon="lucide:calendar"
        :icon-size="16"
        aria-label="Выбрать дату"
        @click="toggleMenu"
      />
    </div>

    <p
      v-if="error"
      class="mt-1 text-sm text-[var(--p-danger-500)]"
    >
      {{ error }}
    </p>

    <Popover
      ref="menuRef"
      append-to="body"
      class="smart-date-picker-menu"
    >
      <div class="picker-menu">
        <DatePicker
          v-model="calendarValue"
          inline
          show-time
          hour-format="24"
          @update:model-value="handleCalendarSelect"
        />
        <CSmartDateQuickList
          v-if="showQuickDates"
          class="quick-column"
          :items="SMART_QUICK_DATES"
          :active-id="activeQuickId"
          search-placeholder="Поиск быстрых дат"
          @select="selectQuickDate"
        />
      </div>
    </Popover>
  </div>
</template>

<script setup lang="ts">
import DatePicker from 'primevue/datepicker'
import InputText from 'primevue/inputtext'
import Popover from 'primevue/popover'
import type { PopoverMethods } from 'primevue/popover'
import {
  SMART_DATE_ERROR,
  SMART_QUICK_DATES,
  useSmartDate,
  type SmartQuickDate,
} from '~/shared/ui/app/smartDatePicker/composables/useSmartDate'
import CSmartDateQuickList from './AppSmartDateQuickList.vue'

withDefaults(
  defineProps<{
    label?: string
    placeholder?: string
    showQuickDates?: boolean
  }>(),
  {
    placeholder: 'now-1h',
    showQuickDates: true,
  },
)

const model = defineModel<string | null>({ default: null })
const { parseExpression, formatAbsolute, findQuickDate } = useSmartDate()
const dayjs = useDayjs()

const menuRef = ref<PopoverMethods | null>(null)
const calendarValue = ref<Date | null>(null)
const error = ref<string | null>(null)
const text = ref(model.value ?? '')

const activeQuickId = computed(() => findQuickDate(model.value)?.id ?? null)

watch(
  () => model.value,
  (value) => {
    const next = value ?? ''
    if (text.value !== next) text.value = next
    if (!value || parseExpression(value)) error.value = null
  },
)

watch(text, (value) => {
  if ((model.value ?? '') !== value) model.value = value
  error.value = null
})

const validate = () => {
  const trimmed = text.value.trim()
  if (!trimmed) {
    text.value = ''
    model.value = null
    error.value = null
    return true
  }
  if (!parseExpression(trimmed)) {
    error.value = SMART_DATE_ERROR
    return false
  }
  text.value = trimmed
  model.value = trimmed
  error.value = null
  return true
}

const applyExpression = (value: string) => {
  text.value = value
  model.value = value
  if (!parseExpression(value)) {
    error.value = SMART_DATE_ERROR
    return false
  }
  error.value = null
  menuRef.value?.hide()
  return true
}

const toggleMenu = (event: Event) => {
  const parsed = parseExpression(text.value.trim() || 'now')
  calendarValue.value = (parsed ?? dayjs()).toDate()
  menuRef.value?.toggle(event)
}

const handleCalendarSelect = (value: Date | Date[] | (Date | null)[] | null | undefined) => {
  const selected = Array.isArray(value) ? value[0] : value
  if (!selected) return
  applyExpression(formatAbsolute(dayjs(selected)))
}

const selectQuickDate = (item: SmartQuickDate) => {
  applyExpression(item.value)
}
</script>

<style scoped lang="scss">
.input-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;

  &--labeled {
    align-items: flex-end;
  }
}

.picker-menu {
  display: grid;
  grid-template-columns: auto minmax(220px, 0.9fr);
  padding: 0.25rem;
}

.quick-column {
  padding: 1rem;
  border-left: 1px solid var(--border-base);
}

@media (max-width: 640px) {
  .picker-menu {
    grid-template-columns: 1fr;
  }

  .quick-column {
    border-left: 0;
    border-top: 1px solid var(--border-base);
  }
}
</style>
