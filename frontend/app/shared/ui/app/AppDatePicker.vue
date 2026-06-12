<template>
  <AppLabel :label="label">
    <DatePicker
      :class="props.class"
      :date-format="dateFormat"
      :model-value="_modelValue"
      :selection-mode="selectionMode"
      v-bind="$attrs"
      :fluid="fluid"
      :show-icon="showIcon"
      :icon-display="iconDisplay"
      @hide="handleHide"
      @update:model-value="handleDateChange"
    />
  </AppLabel>
</template>

<script setup lang="ts">
import { max, min } from 'lodash-es'
import moment from 'moment'
import type { CalendarProps } from 'primevue/calendar'
import { computed } from 'vue'
import AppLabel from './AppLabel.vue'

export interface CDatePickerProps extends /* @vue-ignore */ Omit<CalendarProps, 'modelValue'> {
  data?: CDatePickerChangeData | null
  startDate?: string | null
  endDate?: string | null
  dateFormat?: string
  fluid?: boolean
  showIcon?: boolean
  label?: string
  iconDisplay?: 'input' | 'button'
  class?: string
  selectionMode?: 'single' | 'range'
}

export type CDatePickerChangeData = {
  startDate: string | null
  endDate: string | null
  dates: string[]
}

const model = defineModel<string | (string | null)[] | null>()
const emit = defineEmits<{
  'update:modelValue': [event: string | string[] | null]
  'update:data': [event: CDatePickerChangeData | null]
  'update:startDate': [event: string | null]
  'update:endDate': [event: string | null]
}>()

const props = withDefaults(defineProps<CDatePickerProps>(), {
  dateFormat: 'dd.mm.yy',
  fluid: true,
  showIcon: true,
  iconDisplay: 'input',
  selectionMode: 'single',
})

const handleHide = () => {
  if (props.selectionMode === 'range' && Array.isArray(model.value) && model.value.length === 1) {
    const value = model.value[0] || null
    model.value = [value, value]
    emitValue()
  }
}

const _modelValue = computed(() => {
  let values: (string | null)[] = []
  if (props.data) {
    values = props.data.dates
  } else if (model.value) {
    values = Array.isArray(model.value) ? model.value : [model.value]
  } else if (props.startDate) {
    values = [props.startDate, props.endDate || null]
  }
  if (props.selectionMode === 'single') {
    return _parseDate(values[0])
  }
  const result = values.map((d) => _parseDate(d)).filter((d) => !!d)
  return result.length ? result : null
})

const handleDateChange = (val: Date | Date[] | (Date | null)[] | null | undefined) => {
  if (Array.isArray(val)) {
    model.value = val.map((d) => _formatDate(d)).filter((d) => d !== null)
  } else {
    model.value = _formatDate(val) || null
  }
  emitValue()
}

const emitValue = () => {
  if (props.selectionMode === 'range' && Array.isArray(model.value) && model.value.length !== 2) return
  const changedData = buildChangeData(model.value)
  emit('update:startDate', changedData.startDate)
  emit('update:endDate', changedData.endDate)
  emit('update:data', buildChangeData(model.value))
}

const _formatDate = (val?: Date | null) => {
  if (!val) return null
  return moment(val).format('YYYY-MM-DD')
}

const _parseDate = (val: string | null | undefined) => {
  if (!val) return null
  return moment.utc(val).toDate()
}

const buildChangeData = (value?: string | (string | null)[] | null): CDatePickerChangeData => {
  if (Array.isArray(value)) {
    return {
      startDate: min(value) || null,
      endDate: max(value) || null,
      dates: value.filter((v) => v !== null),
    }
  }
  return {
    startDate: value || null,
    endDate: value || null,
    dates: value ? [value] : [],
  }
}
</script>
