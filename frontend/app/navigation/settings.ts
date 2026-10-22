import { Building, User, Users } from '@lucide/vue'
import type { Component } from 'vue'

export type SettingsNavigationItem = {
  to: { name: string }
  label: string
  icon: Component
  superuserOnly?: boolean
}

// Drawer of the settings layout, in display order. `make new-domain` inserts its entry above the marker line.
export const settingsNavigation: SettingsNavigationItem[] = [
  { to: { name: 'settings-profile' }, label: 'Профиль', icon: User },
  { to: { name: 'settings-organizations' }, label: 'Организации', icon: Building },
  { to: { name: 'settings-users' }, label: 'Пользователи', icon: Users, superuserOnly: true },
  // new-domain: entries above this line
]
