<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { ChromePicker, tinycolor } from 'vue-color'
import { Pipette } from '@lucide/vue'
import 'vue-color/style.css'
import AppInput from './AppInput.vue'
import AppIcon from './AppIcon.vue'
import AppMenu from './AppMenu.vue'
import { appColorPalette } from './colorPalette'
const props = withDefaults(
  defineProps<{
    label?: string
    hint?: string
    disabled?: boolean
    mode?: 'palette' | 'hex'
    colors?: string[]
  }>(),
  { mode: 'palette', colors: () => [...appColorPalette] },
)
const model = defineModel<string | null>({ default: null })
const field = computed({
  get: () => model.value ?? '',
  set: (value) => {
    model.value = value
  },
})
const valid = computed(() => /^#[0-9a-f]{6}$/i.test(field.value))
const isPaletteColor = (value: string | null | undefined) =>
  !!value && props.colors.some((color) => color.toLowerCase() === value.toLowerCase())
const customColor = ref('#7779ed')
watch(
  model,
  (value) => {
    if (value && /^#[0-9a-f]{6}$/i.test(value) && !isPaletteColor(value)) customColor.value = value.toLowerCase()
  },
  { immediate: true },
)
const pickerColor = computed(() =>
  props.mode === 'palette' ? customColor.value : valid.value ? field.value : '#7779ed',
)
const customSelected = computed(
  () => !isPaletteColor(model.value) && model.value?.toLowerCase() === customColor.value.toLowerCase(),
)
function choose(value: unknown) {
  if (props.disabled) return
  const parsed = tinycolor(value as string)
  if (!parsed.isValid()) return
  const next = parsed.toHexString()
  if (props.mode === 'palette') customColor.value = next
  model.value = next
}
</script>
<template>
  <div class="min-w-0">
    <AppInput
      v-if="mode === 'hex'"
      v-model="field"
      :disabled="disabled"
      :label="label"
      :hint="hint"
      :error="valid ? undefined : 'HEX: #RRGGBB'"
      maxlength="7"
      spellcheck="false"
    >
      <template #append>
        <AppMenu
          :disabled="disabled"
          content-class="p-0"
        >
          <template #trigger>
            <button
              type="button"
              :disabled="disabled"
              :aria-label="`${label || 'Цвет'}: выбрать цвет`"
              class="mr-2 h-5 w-5 rounded-sm border-0 p-0 focus-visible:outline focus-visible:outline-2 focus-visible:outline-ring"
              :style="{ backgroundColor: pickerColor }"
            />
          </template>
          <ChromePicker
            :model-value="pickerColor"
            :formats="['hex']"
            disable-alpha
            class="app-color-picker !shadow-none"
            @update:model-value="choose"
          />
        </AppMenu>
      </template>
    </AppInput>
    <div
      v-else
      class="space-y-2"
    >
      <span
        v-if="label"
        class="block text-sm font-medium"
        >{{ label }}</span
      >
      <div
        class="flex max-w-64 flex-wrap gap-2"
        :aria-label="label || 'Цвет'"
        role="group"
      >
        <button
          v-for="color in colors"
          :key="color"
          type="button"
          :disabled="disabled"
          :aria-label="color"
          :aria-pressed="model?.toLowerCase() === color.toLowerCase()"
          class="h-6 w-6 rounded-sm border-0 p-0 focus-visible:outline focus-visible:outline-2 focus-visible:outline-ring disabled:opacity-50"
          :style="{ backgroundColor: color }"
          @click="model = color"
        >
          <span
            v-if="model?.toLowerCase() === color.toLowerCase()"
            :style="{ color: tinycolor(color).isLight() ? '#000' : '#fff' }"
            >✓</span
          >
        </button>
        <AppMenu
          :disabled="disabled"
          content-class="p-0"
        >
          <template #trigger>
            <button
              type="button"
              :disabled="disabled"
              aria-label="Другой цвет"
              :aria-pressed="customSelected"
              class="inline-flex h-6 w-6 items-center justify-center rounded-sm border-0 p-0 focus-visible:outline focus-visible:outline-2 focus-visible:outline-ring disabled:opacity-50"
              :class="customSelected && 'ring-2 ring-primary ring-offset-2 ring-offset-background'"
              :style="{
                backgroundColor: customColor,
                color: tinycolor(customColor).isLight() ? '#000' : '#fff',
              }"
            >
              <AppIcon
                :icon="Pipette"
                size="xs"
                aria-hidden="true"
              />
            </button>
          </template>
          <ChromePicker
            :model-value="pickerColor"
            :formats="['hex']"
            disable-alpha
            class="app-color-picker !shadow-none"
            @update:model-value="choose"
          />
        </AppMenu>
      </div>
      <p
        v-if="hint"
        class="text-xs text-muted-foreground"
      >
        {{ hint }}
      </p>
    </div>
  </div>
</template>

<style>
.app-color-picker {
  --vc-body-bg: var(--popover);
  --vc-picker-bg: var(--foreground);
  --vc-input-bg: var(--background);
  --vc-input-text: var(--foreground);
  --vc-input-label: var(--muted-foreground);
  --vc-input-border: var(--border);
  --vc-chrome-toggle-btn-highlighted: var(--accent);
}
</style>
