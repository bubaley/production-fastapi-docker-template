<script setup lang="ts">
import { Moon, Sun } from '@lucide/vue'

/**
 * One-click light/dark switch for screens without a profile menu (public pages, auth, landing).
 * Both icons are rendered and CSS picks one, so the server markup never depends on the visitor's theme.
 * The full mode and palette picker is `AppThemeSwitcher`.
 */
const { mode, resolvedMode } = useTheme()
const toggle = () => {
  mode.value = resolvedMode.value === 'dark' ? 'light' : 'dark'
}
</script>

<template>
  <AppButton
    variant="ghost"
    size="icon"
    text-variant="muted"
    aria-label="Переключить тему: светлая или тёмная"
    title="Светлая / тёмная тема"
    @click="toggle"
  >
    <!-- Wrappers: the icon's own display class would beat `hidden`. -->
    <span class="inline-flex dark:hidden">
      <AppIcon
        :icon="Moon"
        size="sm"
      />
    </span>
    <span class="hidden dark:inline-flex">
      <AppIcon
        :icon="Sun"
        size="sm"
      />
    </span>
  </AppButton>
</template>
