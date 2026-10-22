<script setup lang="ts">
import { computed, ref, watch, onMounted, onBeforeUnmount, nextTick, useAttrs } from 'vue'
import AppField from './AppField.vue'
import Textarea from '~/shared/ui/shadcn/textarea/Textarea.vue'
export type AppTextareaProps = {
  id?: string
  label?: string
  placeholder?: string
  disabled?: boolean
  readonly?: boolean
  required?: boolean
  error?: string
  hint?: string
  rows?: number
  autoGrow?: boolean
  variant?: 'outline' | 'ghost'
}
defineOptions({ inheritAttrs: false })
const props = defineProps<AppTextareaProps>()
const attrs = useAttrs()
const textarea = ref<{ $el: HTMLTextAreaElement }>()
const inputAttrs = () => Object.fromEntries(Object.entries(attrs).filter(([key]) => !['class', 'style'].includes(key)))
let observer: ResizeObserver | undefined
const resize = () => {
  const el = textarea.value?.$el
  if (!props.autoGrow || !el) return
  el.style.height = 'auto'
  el.style.height = `${el.scrollHeight + 2}px`
}
onMounted(() => {
  resize()
  let width = 0
  observer = new ResizeObserver(([entry]) => {
    if (entry && entry.contentRect.width !== width) {
      width = entry.contentRect.width
      resize()
    }
  })
  if (textarea.value?.$el) observer.observe(textarea.value.$el)
})
onBeforeUnmount(() => observer?.disconnect())
const model = defineModel<string | null>({ default: '' })
const text = computed({ get: () => model.value ?? '', set: (value: string | number) => { model.value = String(value) } })
watch(model, () => void nextTick(resize))
</script>
<template>
  <AppField
    :id="id"
    :class="attrs.class"
    :style="attrs.style"
    :label="label"
    :error="error"
    :hint="hint"
  >
    <template #default="field">
      <Textarea
        v-bind="inputAttrs()"
        :id="field.id"
        ref="textarea"
        v-model="text"
        :aria-describedby="field.describedBy"
        :aria-invalid="Boolean(error) || undefined"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :required="required"
        :rows="rows || (autoGrow ? 1 : 3)"
        :class="[
          autoGrow && 'min-h-0 resize-none overflow-hidden',
          variant === 'ghost' &&
            'border-transparent bg-transparent shadow-none hover:border-border focus-visible:border-ring',
          error && 'border-destructive focus-visible:border-destructive focus-visible:ring-destructive/30'
        ]"
        @input="resize"
      />
    </template>
  </AppField>
</template>
