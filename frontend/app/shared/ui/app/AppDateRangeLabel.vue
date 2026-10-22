<template>
  <div class="inline-flex items-center whitespace-nowrap">
    <DateLabel
      v-bind="props"
      :date="startDate"
      :colored="coloredStartDate || (coloredEndDate && startDate === endDate)"
      @click="emit('clickStart')"
    />
    <AppIcon
      v-if="showEndDate && startDate && endDate"
      size="xs"
      :icon="ChevronRight"
      class="mx-1 text-muted-foreground"
    />
    <DateLabel
      v-if="showEndDate"
      v-bind="props"
      :date="endDate"
      :colored="coloredEndDate"
      @click="emit('clickEnd')"
    />
  </div>
</template>

<script setup lang="ts">
import DateLabel, { type DateLabelProps } from '~/shared/ui/app/AppDateLabel.vue'
import AppIcon from '~/shared/ui/app/AppIcon.vue'
import { ChevronRight } from '@lucide/vue'
import { computed } from 'vue'

export type DateRangeLabelProps = Omit<DateLabelProps, 'date' | 'colored'> & {
  startDate?: string | null
  endDate?: string | null
  combineEqualDates?: boolean
  coloredStartDate?: boolean
  coloredEndDate?: boolean
}
const props = withDefaults(defineProps<DateRangeLabelProps>(), {
  isUtc: true,
  combineEqualDates: true,
  format: 'shortcut',
  type: 'datetime'
})

const emit = defineEmits<{
  (evt: 'clickStart' | 'clickEnd'): void
}>()

const showEndDate = computed(() => {
  return props.endDate && !(props.combineEqualDates && props.startDate === props.endDate)
})

export type { DateLabelProps as DateViewProps }
</script>
