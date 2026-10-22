<script setup lang="ts">
import { Check, Minus } from '@lucide/vue'
import { computed, useAttrs, useId } from 'vue'

defineOptions({ inheritAttrs: false })
const props = defineProps<{
  label?: string
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
  <label
    :for="id"
    class="inline-flex cursor-pointer items-center gap-2 text-sm"
  >
    <input
      :id="id"
      v-bind="attrs"
      type="checkbox"
      :checked="checked"
      :indeterminate.prop="indeterminate"
      :aria-checked="indeterminate ? 'mixed' : checked"
      :disabled="disabled"
      class="peer sr-only"
      @change="toggle"
    />
    <span
      aria-hidden="true"
      class="relative box-border block size-[18px] min-h-[18px] min-w-[18px] shrink-0 overflow-hidden rounded border border-border transition-colors peer-focus-visible:ring-2 peer-focus-visible:ring-ring peer-focus-visible:ring-offset-2 peer-disabled:cursor-not-allowed peer-disabled:opacity-50"
      :class="checked || indeterminate ? 'bg-white text-black' : 'bg-card text-transparent'"
    >
      <Minus
        v-if="indeterminate"
        class="absolute inset-0 m-auto size-3.5"
        :stroke-width="3"
      />
      <Check
        v-else-if="checked"
        class="absolute inset-0 m-auto size-3.5"
        :stroke-width="3"
      />
    </span>
    <slot>{{ label }}</slot>
  </label>
</template>
