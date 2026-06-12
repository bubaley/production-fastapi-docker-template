<template>
  <span :class="dateView.class">
    <!-- <q-tooltip v-if="showTooltip">
      <span>{{ tooltipTitle }}</span>
      {{ formatDate(dateView.value, { type, includeSeconds: true, disableRelative: true }) }}
    </q-tooltip> -->
    {{ dateView.formattedValue }}</span>
</template>

<script setup lang="ts">
import type { Dayjs } from 'dayjs'
import { computed } from 'vue'

export type DateLabelProps = {
  date?: string | null
  colored?: boolean
  isUtc?: boolean
  format?: DateFormat
  type?: DateType
  includeSeconds?: boolean
  showTooltip?: boolean
  tooltipTitle?: string
}

const props = withDefaults(defineProps<DateLabelProps>(), {
  isUtc: true,
  format: 'shortcut',
  type: 'datetime',
})

const { parseDate, formatDate, now } = useDate()

type DateViewData = {
  value: Dayjs | null
  class?: string
  formattedValue: string | null
  isToday?: boolean
  isOverdue?: boolean
}

const dateView = computed<DateViewData>(() => {
  const value = parseDate(props.date, { isUtc: props.isUtc, type: props.type })
  const formattedValue = formatDate(value, {
    format: props.format,
    type: props.type,
    includeSeconds: props.includeSeconds,
  })
  const _now = now(props.type)
  //   const isToday = value?.isSame(_now, 'date')
  //   const isOverdue = value?.isBefore(_now)

  return {
    value,
    formattedValue,
    // isToday,
    // isOverdue,
  }
})
</script>
