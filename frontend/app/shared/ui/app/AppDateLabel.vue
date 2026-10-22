<script setup lang="ts">
import { computed } from 'vue'
import { useDate, type DateFormat, type DateLocale, type DateType } from '~/shared/composables/useDate'

export type DateLabelProps = {
  date?: string | null
  colored?: boolean
  isUtc?: boolean
  format?: DateFormat
  type?: DateType
  locale?: DateLocale
  includeSeconds?: boolean
  showTooltip?: boolean
  tooltipTitle?: string
}
const props = withDefaults(defineProps<DateLabelProps>(), {
  isUtc: true,
  format: 'shortcut',
  type: 'datetime',
  locale: 'ru',
})
const { parseDate, formatDate } = useDate(() => props.locale)
const value = computed(() => parseDate(props.date, { isUtc: props.isUtc, type: props.type }))
const formatted = computed(() =>
  formatDate(value.value, {
    format: props.format,
    type: props.type,
    includeSeconds: props.includeSeconds,
  }),
)
const tooltip = computed(() =>
  props.showTooltip
    ? [props.tooltipTitle, formatDate(value.value, { type: props.type, includeSeconds: true, disableRelative: true })]
        .filter(Boolean)
        .join(' ')
    : undefined,
)
</script>
<template>
  <span :title="tooltip">{{ formatted }}</span>
</template>
