<template>
  <div class="flex flex-col gap-2">
    <div class="relative inline-flex">
      <div
        ref="targetRef"
        class="color-preview"
        :style="{ backgroundColor: displayColor }"
        @click="togglePopover"
      />
      <Popover
        ref="popoverRef"
        :target="targetRef"
        class="color-picker-popover"
      >
        <div class="color-palette p-2">
          <div
            v-for="color in colorPalette"
            :key="color.hex"
            class="color-item"
            :class="{ active: modelValue === color.hex }"
            :style="{ backgroundColor: color.hex }"
            :title="color.name"
            @click="selectColor(color.hex)"
          />
        </div>
      </Popover>
    </div>
  </div>
</template>

<script setup lang="ts">
import Popover from 'primevue/popover'
import type { PopoverMethods } from 'primevue/popover'

export interface CColorPickerProps {
  modelValue?: string | null
  label?: string
}

const props = withDefaults(defineProps<CColorPickerProps>(), {
  modelValue: null,
})

const emit = defineEmits<{
  'update:modelValue': [value: string | null]
}>()

const targetRef = ref<HTMLElement | null>(null)
const popoverRef = ref<PopoverMethods | null>(null)

const colorPalette = [
  { name: 'Red', hex: '#ef4444' },
  { name: 'Orange', hex: '#f97316' },
  { name: 'Amber', hex: '#f59e0b' },
  { name: 'Yellow', hex: '#eab308' },
  { name: 'Lime', hex: '#84cc16' },
  { name: 'Green', hex: '#22c55e' },
  { name: 'Emerald', hex: '#10b981' },
  { name: 'Teal', hex: '#14b8a6' },
  { name: 'Cyan', hex: '#06b6d4' },
  { name: 'Sky', hex: '#0ea5e9' },
  { name: 'Blue', hex: '#3b82f6' },
  { name: 'Indigo', hex: '#6366f1' },
  { name: 'Violet', hex: '#8b5cf6' },
  { name: 'Purple', hex: '#a855f7' },
  { name: 'Fuchsia', hex: '#d946ef' },
  { name: 'Pink', hex: '#ec4899' },
  { name: 'Rose', hex: '#f43f5e' },
  { name: 'Slate', hex: '#64748b' },
  { name: 'Gray', hex: '#6b7280' },
  { name: 'Zinc', hex: '#71717a' },
  { name: 'Neutral', hex: '#737373' },
  { name: 'Stone', hex: '#78716c' },
]

const normalizeHex = (value: string | null | undefined): string => {
  try {
    return value?.startsWith('#') ? value : `#${value}`
  } catch {
    return '#cccccc'
  }
}

const displayColor = computed(() => {
  return normalizeHex(props.modelValue)
})

const togglePopover = (event: Event) => {
  popoverRef.value?.toggle(event)
}

const selectColor = (hex: string) => {
  emit('update:modelValue', hex)
  popoverRef.value?.hide()
}
</script>

<style scoped lang="scss">
.color-preview {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.375rem;
  border: 2px solid var(--p-content-border-color);
  cursor: pointer;
  transition: all 0.2s;
}

.color-palette {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 0.5rem;
}

.color-item {
  width: 2rem;
  height: 2rem;
  border-radius: 0.375rem;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    transform: scale(1.1);
    border-color: var(--p-content-border-color);
  }

  &.active {
    border-color: var(--p-primary-color);
    border-width: 3px;
    box-shadow: 0 0 0 2px var(--p-primary-50);
  }
}
</style>
