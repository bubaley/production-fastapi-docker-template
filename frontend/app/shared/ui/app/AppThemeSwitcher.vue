<script setup lang="ts">
import { Monitor, Moon, Sun } from '@lucide/vue'
import type { Palette, ThemeMode } from '~/shared/lib/theme'

withDefaults(defineProps<{ locale?: 'ru' | 'en'; hidePalette?: boolean }>(), { locale: 'ru' })
const { mode, palette, palettes } = useTheme()

const modeOptions: { value: ThemeMode; icon: typeof Sun; label: Record<'ru' | 'en', string> }[] = [
  { value: 'system', icon: Monitor, label: { ru: 'Системная', en: 'System' } },
  { value: 'light', icon: Sun, label: { ru: 'Светлая', en: 'Light' } },
  { value: 'dark', icon: Moon, label: { ru: 'Тёмная', en: 'Dark' } },
]
const paletteLabels: Record<Palette, Record<'ru' | 'en', string>> = {
  neutral: { ru: 'Нейтральная', en: 'Neutral' },
  blue: { ru: 'Синяя', en: 'Blue' },
  violet: { ru: 'Фиолетовая', en: 'Violet' },
  green: { ru: 'Зелёная', en: 'Green' },
  orange: { ru: 'Оранжевая', en: 'Orange' },
}
// Swatch colors are the dark-theme primaries from theme.css.
const swatches: Record<Palette, string> = {
  neutral: 'bg-[#9a9da8]',
  blue: 'bg-[#3b82f6]',
  violet: 'bg-[#7779ed]',
  green: 'bg-[#22c55e]',
  orange: 'bg-[#f97316]',
}
</script>

<template>
  <div class="flex flex-col gap-3">
    <div
      role="group"
      :aria-label="locale === 'en' ? 'Theme' : 'Тема'"
      class="inline-flex w-full gap-0.5 rounded-md border border-border bg-muted p-0.5"
    >
      <button
        v-for="option in modeOptions"
        :key="option.value"
        type="button"
        :aria-pressed="mode === option.value"
        class="inline-flex h-control-sm flex-1 cursor-pointer items-center justify-center gap-1.5 rounded-sm px-2 text-xs text-muted-foreground transition-colors outline-none hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring aria-pressed:bg-card aria-pressed:text-foreground aria-pressed:shadow-sm"
        @click="mode = option.value"
      >
        <AppIcon
          :icon="option.icon"
          size="xs"
        />
        {{ option.label[locale] }}
      </button>
    </div>
    <div
      v-if="!hidePalette"
      role="group"
      :aria-label="locale === 'en' ? 'Accent color' : 'Акцентный цвет'"
      class="flex items-center gap-2"
    >
      <span class="mr-auto text-xs text-muted-foreground">{{ locale === 'en' ? 'Accent' : 'Акцент' }}</span>
      <button
        v-for="item in palettes"
        :key="item"
        type="button"
        :aria-pressed="palette === item"
        :aria-label="paletteLabels[item][locale]"
        :title="paletteLabels[item][locale]"
        class="size-5 cursor-pointer rounded-full ring-offset-2 ring-offset-background transition-shadow outline-none focus-visible:ring-2 focus-visible:ring-ring aria-pressed:ring-2 aria-pressed:ring-foreground"
        :class="swatches[item]"
        @click="palette = item"
      />
    </div>
  </div>
</template>
