<script setup lang="ts" generic="V extends string | number">
import { useId } from 'vue'
import { RadioGroup, RadioGroupItem } from '~/shared/ui/shadcn/radio-group'
import { Label } from '~/shared/ui/shadcn/label'

export type AppRadioOption<V> = { label: string; value: V; disabled?: boolean }

withDefaults(
  defineProps<{
    items: AppRadioOption<V>[]
    /** Accessible name of the group. */
    ariaLabel?: string
    orientation?: 'horizontal' | 'vertical'
    disabled?: boolean
  }>(),
  { orientation: 'vertical' },
)
const model = defineModel<V | null>()
const id = useId()
</script>

<template>
  <RadioGroup
    v-model="model as V"
    :aria-label="ariaLabel"
    :orientation="orientation"
    :disabled="disabled"
    :class="orientation === 'horizontal' ? 'flex flex-wrap gap-4' : 'grid gap-2'"
  >
    <span
      v-for="(item, index) in items"
      :key="String(item.value)"
      class="inline-flex items-center gap-2"
    >
      <RadioGroupItem
        :id="`${id}-${index}`"
        :value="item.value"
        :disabled="item.disabled"
        class="focus-visible:ring-2"
      />
      <Label
        :for="`${id}-${index}`"
        class="cursor-pointer leading-[inherit] font-normal"
        >{{ item.label }}</Label
      >
    </span>
  </RadioGroup>
</template>
