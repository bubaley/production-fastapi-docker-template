import { icons } from '@lucide/vue'
import type { Component } from 'vue'
import type { AppAppearanceIconOption } from './AppAppearancePicker.vue'

const iconId = (name: string) => name
  .replace(/([A-Z])([A-Z][a-z])/g, '$1-$2')
  .replace(/([a-z0-9])([A-Z])/g, '$1-$2')
  .replace(/([A-Za-z])([0-9]+)/g, '$1-$2')
  .toLowerCase()

export const appearanceIcons: AppAppearanceIconOption[] = Object.entries(icons as Record<string, Component>)
  .map(([name, icon]) => {
    const value = iconId(name)
    const label = value.replaceAll('-', ' ')
    return { value, label, icon, searchText: `${value} ${label}` }
  })
  .sort((a, b) => a.value.localeCompare(b.value, 'en'))
