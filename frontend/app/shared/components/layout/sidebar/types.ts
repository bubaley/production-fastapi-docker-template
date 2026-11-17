import type { Component } from 'vue'
import type { RouteLocationRaw } from 'vue-router'

export type SidebarItem = {
  /** Route of a link item; an item without one renders as a button and needs `onClick`. */
  to?: RouteLocationRaw
  onClick?: () => void
  label: string
  icon?: Component
}

export type SidebarSection = {
  /** Small muted heading; a section without one is a plain group of items. */
  title?: string
  items: SidebarItem[]
  /** Icon button next to the heading (for example «+» to create an entry of the section). */
  action?: { label: string; icon: Component; onClick: () => void }
  /** The heading folds the section; the folded state is remembered in the `sidebar-folded` cookie under this id. */
  collapsibleId?: string
}
