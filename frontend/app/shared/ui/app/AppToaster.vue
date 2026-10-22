<script setup lang="ts">
import { X } from '@lucide/vue'
import { Sonner } from '~/shared/ui/shadcn/sonner'
withDefaults(defineProps<{ locale?: 'ru' | 'en' }>(), { locale: 'ru' })
const colors = {
  '--normal-bg': 'var(--background)',
  '--normal-text': 'var(--popover-foreground)',
  '--normal-border': 'var(--border)',
  ...Object.fromEntries(
    [
      ['success', 'success'],
      ['info', 'info'],
      ['warning', 'warning'],
      ['error', 'destructive'],
    ].flatMap(([kind, token]) => [
      [`--${kind}-bg`, `color-mix(in srgb, var(--${token}) 15%, var(--popover))`],
      [`--${kind}-text`, 'var(--popover-foreground)'],
      [`--${kind}-border`, `color-mix(in srgb, var(--${token}) 65%, var(--border))`],
    ]),
  ),
}
</script>

<template>
  <Sonner
    position="top-center"
    rich-colors
    close-button
    close-button-position="top-right"
    :icons="{ close: X }"
    :offset="12"
    :mobile-offset="12"
    :duration="4000"
    :visible-toasts="4"
    :style="colors"
    :container-aria-label="locale === 'en' ? 'Notifications' : 'Уведомления'"
    :toast-options="{
      closeButtonAriaLabel: locale === 'en' ? 'Dismiss notification' : 'Закрыть уведомление',
      classes: {
        toast: 'font-sans pointer-events-auto py-2 pl-3 pr-8',
        description: 'text-sm text-inherit opacity-70',
        closeButton:
          'top-1.5 right-1.5 left-auto transform-none size-[22px] rounded-sm border-0 bg-transparent p-0 text-[color:var(--normal-border)] opacity-100 cursor-pointer transition-colors duration-150 hover:bg-transparent hover:text-white focus-visible:bg-transparent focus-visible:text-white focus-visible:outline-2 focus-visible:outline-ring focus-visible:outline-offset-2 [&_svg]:size-3 [&_svg]:pointer-events-none',
        success: '[--normal-border:var(--success-border)] [&_[data-icon]]:text-success',
        info: '[--normal-border:var(--info-border)] [&_[data-icon]]:text-info',
        warning: '[--normal-border:var(--warning-border)] [&_[data-icon]]:text-warning',
        error: '[--normal-border:var(--error-border)] [&_[data-icon]]:text-destructive',
      },
    }"
  />
</template>
