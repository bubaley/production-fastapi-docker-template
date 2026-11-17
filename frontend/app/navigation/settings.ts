import { Building, User, Users } from '@lucide/vue'
import type { Component } from 'vue'

export type SettingsNavigationSection = 'organization' | 'account' | 'instance'

export type SettingsNavigationItem = {
  to: { name: string }
  label: string
  icon: Component
  /** Sidebar group; entries without one belong to the selected organization (what `make new-domain` adds). */
  section?: SettingsNavigationSection
  /** Only superusers see it. */
  superuserOnly?: boolean
}

// Groups of the settings sidebar, in display order; an empty group is not shown.
export const settingsSections: { key: SettingsNavigationSection; title: string }[] = [
  { key: 'organization', title: 'Организация' },
  { key: 'account', title: 'Учётная запись' },
  { key: 'instance', title: 'Сервер' },
]

// Settings sidebar entries, in display order within their group. `make new-domain` inserts its entry above the marker line.
export const settingsNavigation: SettingsNavigationItem[] = [
  { to: { name: 'settings-profile' }, label: 'Профиль', icon: User, section: 'account' },
  { to: { name: 'settings-organizations' }, label: 'Организации', icon: Building, section: 'account' },
  { to: { name: 'settings-users' }, label: 'Пользователи', icon: Users, section: 'instance', superuserOnly: true },
  // new-domain: entries above this line
]
