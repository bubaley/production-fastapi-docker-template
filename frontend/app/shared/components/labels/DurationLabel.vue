<template>
  <div v-if="formattedDuration">{{ formattedDuration }}</div>
</template>

<script setup lang="ts">
export type DurationFormat = 'clock' | 'parts' | 'value'
export type DurationUnit = 'hours' | 'minutes' | 'seconds'

const UNIT_ORDER: DurationUnit[] = ['hours', 'minutes', 'seconds']

const UNIT_LABEL: Record<DurationUnit, string> = {
  hours: 'ч',
  minutes: 'м',
  seconds: 'с',
}

const UNIT_SECONDS: Record<DurationUnit, number> = {
  hours: 3600,
  minutes: 60,
  seconds: 1,
}

const props = withDefaults(
  defineProps<{
    date?: string | null
    format?: DurationFormat
    /** One unit: `value` mode, or a shorthand for `units: [unit]`. */
    unit?: DurationUnit
    /** Which segments to show, largest first. Clock: `['hours', 'minutes']` → `00:23`, `['minutes', 'seconds']` → `23:45`. */
    units?: DurationUnit[]
    hideZero?: boolean
  }>(),
  {
    format: 'parts',
    hideZero: true,
  },
)

const { parseDate, now } = useDate()

const pad = (value: number) => String(value).padStart(2, '0')

const resolvedUnits = computed<DurationUnit[]>(() => {
  if (props.format === 'value') {
    const unit = props.unit ?? props.units?.[0] ?? 'seconds'
    return [unit]
  }
  if (props.units?.length) {
    const unique = new Set(props.units)
    return UNIT_ORDER.filter((unit) => unique.has(unit))
  }
  if (props.unit) return [props.unit]
  return [...UNIT_ORDER]
})

const splitDuration = (totalSeconds: number, units: DurationUnit[]) => {
  let remaining = totalSeconds
  return units.map((unit, index) => {
    const size = UNIT_SECONDS[unit]
    if (index === units.length - 1) return Math.floor(remaining / size)
    const value = Math.floor(remaining / size)
    remaining %= size
    return value
  })
}

const formattedDuration = computed(() => {
  if (!props.date) return ''

  const date = parseDate(props.date)
  if (!date) return ''

  const totalSeconds = Math.abs(date.diff(now(), 'seconds'))
  const units = resolvedUnits.value
  if (!units.length) return ''

  const values = splitDuration(totalSeconds, units)
  if (props.hideZero && values.every((value) => value === 0)) return ''

  if (props.format === 'clock') {
    return values.map((value) => pad(value)).join(':')
  }

  return units
    .flatMap((unit, index) => {
      const value = values[index]
      if (props.hideZero && value === 0) return []
      return [`${value}${UNIT_LABEL[unit]}`]
    })
    .join(' ')
})
</script>
