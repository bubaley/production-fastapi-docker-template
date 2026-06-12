<template>
  <AppLabel :label="label">
    <IconField>
      <Textarea
        ref="inputRef"
        v-model="model"
        fluid
        :class="props.class"
        v-bind="$attrs"
      />
      <InputIcon
        v-if="_icon"
        :class="{ [_icon]: true }"
      >
        <Icon :name="_icon" />
      </InputIcon>
    </IconField>
  </AppLabel>
</template>

<script setup lang="ts">
import type { TextareaProps } from 'primevue/textarea'
import AppLabel from './AppLabel.vue'
import { computed, nextTick, onMounted, ref } from 'vue'

export interface CTextareaProps extends /* @vue-ignore */ TextareaProps {
  label?: string
  icon?: string
  autofocus?: boolean
  loading?: boolean
}

const props = defineProps<CTextareaProps>()
const model = defineModel<string | null>()

const inputRef = ref()

const _icon = computed(() => {
  return props.loading ? 'svg-spinners:180-ring' : props.icon
})

onMounted(() => {
  if (props.autofocus) {
    nextTick(() => {
      inputRef.value?.$el.focus()
    })
  }
})
</script>
