<script setup lang="ts">
import { computed, ref, watch, onBeforeUnmount, useAttrs, type Component } from 'vue'
import { Input } from '~/shared/ui/shadcn/input'
import AppField from './AppField.vue'
import AppIcon from './AppIcon.vue'
import AppClearButton from './AppClearButton.vue'
import {
  activeOutlineClasses,
  appControlRadiusClasses,
  appControlStyles,
  appControlIconSize,
  type AppFieldVariant,
  type AppControlSize
} from './types/control'

defineOptions({ inheritAttrs: false })

export type AppInputProps = {
  variant?: AppFieldVariant
  clearable?: boolean
  /** Reserve trailing space for an always-visible clear button. Default: overlay on hover/focus. */
  clearInline?: boolean
  icon?: Component | string
  isSearch?: boolean
  loading?: boolean
  fluid?: boolean
  debounce?: number
  id?: string
  label?: string
  type?: 'number' | 'datetime-local' | 'date' | 'time' | 'email' | 'password' | 'search' | 'tel' | 'text' | 'url'
  placeholder?: string
  autocomplete?: string
  autofocus?: boolean
  disabled?: boolean
  readonly?: boolean
  required?: boolean
  error?: string
  hint?: string
  size?: AppControlSize
}

const props = withDefaults(defineProps<AppInputProps>(), { type: 'text', size: 'default', variant: 'outline' })
const model = defineModel<string | null>({ default: '' })
const localValue = ref(model.value ?? '')
let debounceTimer: ReturnType<typeof setTimeout> | undefined
watch(model, value => { clearTimeout(debounceTimer); localValue.value = value ?? '' })
onBeforeUnmount(() => clearTimeout(debounceTimer))
const inputModel = computed({
  get: () => localValue.value,
  set: (value: string | number) => {
    localValue.value = String(value)
    clearTimeout(debounceTimer)
    if (props.debounce) debounceTimer = setTimeout(() => { model.value = localValue.value }, props.debounce)
    else model.value = localValue.value
  },
})
const effectiveIcon = computed(() => props.loading ? 'svg-spinners:180-ring' : props.icon || (props.isSearch ? 'lucide:search' : undefined))
const attrs = useAttrs()
const inputRef = ref<{ $el: HTMLInputElement }>()
const emit = defineEmits<{ clear: [] }>()
const clear = () => {
  clearTimeout(debounceTimer)
  localValue.value = ''
  model.value = ''
  emit('clear')
  inputRef.value?.$el.focus()
}
defineExpose({ focus: () => inputRef.value?.$el.focus(), blur: () => inputRef.value?.$el.blur() })
// Layout classes belong to the field; native attributes and listeners belong to its input.
const inputAttrs = () =>
  Object.fromEntries(Object.entries(attrs).filter(([key]) => !['class', 'style', 'aria-describedby'].includes(key)))
const describedBy = (message?: string) => [attrs['aria-describedby'], message].filter(Boolean).join(' ') || undefined
</script>

<template>
  <AppField
    :id="id"
    :label="label"
    :error="error"
    :hint="hint"
    :class="attrs.class"
    :style="attrs.style"
  >
    <template #default="field">
      <span class="group/input relative flex items-center">
        <Input
          v-bind="inputAttrs()"
          :id="field.id"
          ref="inputRef"
          v-model="inputModel"
          :type="type"
          :placeholder="placeholder"
          :autocomplete="autocomplete"
          :autofocus="autofocus"
          :disabled="disabled"
          :readonly="readonly"
          :required="required"
          :aria-invalid="Boolean(error) || attrs['aria-invalid'] || undefined"
          :aria-describedby="describedBy(field.describedBy)"
          :style="{
            ...appControlStyles.input[props.size],
            ...($slots.prepend || effectiveIcon ? { paddingLeft: '2.5rem' } : {}),
            ...($slots.append || (clearable && clearInline) ? { paddingRight: '2.5rem' } : {})
          }"
          :class="[
            appControlRadiusClasses[props.size],
            ($slots.prepend || effectiveIcon) && 'pl-10',
            ($slots.append || (clearable && clearInline)) && 'pr-10',
            variant === 'active-outline' && [activeOutlineClasses, 'enabled:hover:bg-primary/20'],
            variant === 'secondary' &&
              'border-transparent bg-secondary text-secondary-foreground shadow-none enabled:hover:bg-accent',
            variant === 'ghost' && 'border-transparent bg-transparent shadow-none',
            error && 'border-destructive focus-visible:border-destructive focus-visible:ring-destructive/30'
          ]"
        />
        <span
          v-if="$slots.prepend || effectiveIcon"
          class="absolute left-3 flex"
          :class="!model ? 'text-muted-foreground' : variant === 'active-outline' ? 'text-primary' : 'text-foreground'"
        ><slot name="prepend"><AppIcon
          :icon="effectiveIcon"
          :size="appControlIconSize[size]"
        /></slot></span>
        <AppClearButton
          v-if="clearable && model && !disabled && !readonly"
          :size="size"
          :active="variant === 'active-outline'"
          type="button"
          class="absolute right-2 transition-opacity"
          :class="
            !clearInline &&
              'opacity-0 pointer-events-none group-hover/input:opacity-100 group-hover/input:pointer-events-auto group-focus-within/input:opacity-100 group-focus-within/input:pointer-events-auto'
          "
          :label="attrs['lang'] === 'en' ? 'Clear' : 'Очистить'"
          @click="clear"
        />
        <span
          v-else-if="$slots.append"
          class="absolute right-1 flex text-muted-foreground"
        ><slot name="append" /></span>
      </span>
    </template>
  </AppField>
</template>
