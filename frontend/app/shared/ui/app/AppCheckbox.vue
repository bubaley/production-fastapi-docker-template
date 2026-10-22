<script setup lang="ts">
import { Check, Minus } from '@lucide/vue'
import { computed, useAttrs, useId } from 'vue'
import { Checkbox } from '~/shared/ui/shadcn/checkbox'
import { Label } from '~/shared/ui/shadcn/label'

defineOptions({ inheritAttrs: false })
const props = defineProps<{
  label?: string
  /** Value added to / removed from an array model. */
  val?: unknown
  trueValue?: unknown
  falseValue?: unknown
  disabled?: boolean
  indeterminate?: boolean
}>()
const model = defineModel<any>()
const attrs = useAttrs()
const generatedId = useId()
const id = computed(() => (typeof attrs.id === 'string' ? attrs.id : generatedId))
const checked = computed(() => {
  if (Array.isArray(model.value)) return model.value.includes(props.val)
  return model.value === (props.trueValue ?? true)
})
const state = computed(() => (props.indeterminate ? 'indeterminate' : checked.value))
const toggle = () => {
  if (props.disabled) return
  if (Array.isArray(model.value)) {
    model.value = checked.value
      ? model.value.filter((item: unknown) => item !== props.val)
      : [...model.value, props.val]
  } else {
    model.value = checked.value ? (props.falseValue ?? false) : (props.trueValue ?? true)
  }
}
</script>

<template>
  <span
    class="inline-flex items-center gap-2"
    :class="attrs.class"
  >
    <Checkbox
      v-bind="{ ...attrs, class: undefined }"
      :id="id"
      :model-value="state"
      :disabled="disabled"
      class="size-[18px] rounded-sm border-border bg-card"
      @update:model-value="toggle"
    >
      <Minus
        v-if="indeterminate"
        class="size-3.5"
        :stroke-width="3"
      />
      <Check
        v-else
        class="size-3.5"
        :stroke-width="3"
      />
    </Checkbox>
    <Label
      v-if="label || $slots.default"
      :for="id"
      class="cursor-pointer leading-[inherit] font-normal"
    >
      <slot>{{ label }}</slot>
    </Label>
  </span>
</template>
