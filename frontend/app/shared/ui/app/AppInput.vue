<template>
  <AppLabel :label="label">
    <IconField>
      <InputText
        ref="inputRef"
        v-bind="{ ...props, ...$attrs }"
        v-model="localValue"
        :fluid="fluid"
        :class="props.class"
        @blur="emit('blur')"
      />
      <InputIcon
        v-if="clearable && localValue"
        class="flex items-center justify-center cursor-pointer"
        @click="handleClear"
      >
        <Icon name="lucide:x" />
      </InputIcon>
      <InputIcon
        v-else-if="_icon"
        :class="{ [_icon]: true }"
        class="flex items-center justify-center"
      >
        <Icon :name="_icon" />
      </InputIcon>
    </IconField>
  </AppLabel>
</template>

<script setup lang="ts">
import type { InputTextProps } from 'primevue/inputtext'
import AppLabel from './AppLabel.vue'
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useDebounceFn } from '@vueuse/core'

export interface AppInputProps extends /* @vue-ignore */ InputTextProps {
  label?: string
  loading?: boolean
  isSearch?: boolean
  fluid?: boolean
  icon?: string
  debounce?: number
  clearable?: boolean
  modelValue?: string | null
}

const props = withDefaults(defineProps<AppInputProps>(), {
  fluid: true,
  isSearch: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: string | null]
  blur: []
}>()

const inputRef = ref()
const localValue = ref<string | null>(props.modelValue ?? null)
const skipDebounce = ref(false)

const _icon = computed(() => {
  if (props.loading) return 'svg-spinners:180-ring'
  if (props.icon) return props.icon
  if (props.isSearch) return 'lucide:search'
  return null
})

watch(
  () => props.modelValue,
  (newValue) => {
    localValue.value = newValue ?? null
  },
)

const emitValue = (value: string | null) => {
  emit('update:modelValue', value)
}

const debouncedEmit = props.debounce && props.debounce > 0 ? useDebounceFn(emitValue, props.debounce) : emitValue

watch(localValue, (newValue) => {
  if (skipDebounce.value) {
    skipDebounce.value = false
    return
  }
  debouncedEmit(newValue ?? null)
})

const handleClear = () => {
  skipDebounce.value = true
  localValue.value = null
  emitValue(null)
  emit('blur')
}

onMounted(() => {
  if (props.autofocus) {
    nextTick(() => {
      inputRef.value?.$el.focus()
    })
  }
})
</script>
