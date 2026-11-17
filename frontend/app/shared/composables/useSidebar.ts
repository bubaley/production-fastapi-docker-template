import type { Ref } from 'vue'

export type SidebarState = {
  /** The desktop sidebar is hidden; remembered in the `sidebar-collapsed` cookie, so SSR renders the same shell. */
  collapsed: Ref<boolean>
  /** The navigation sheet on narrow screens; never persisted. */
  mobileOpen: Ref<boolean>
}

/** App shell sidebar state shared by the layout, its sidebar and anything that toggles it. */
export const useSidebar = (): SidebarState => {
  const collapsed = useCookie<boolean>('sidebar-collapsed', {
    default: () => false,
    maxAge: 60 * 60 * 24 * 365,
    sameSite: 'lax',
  })
  const mobileOpen = useState<boolean>('sidebar-mobile-open', () => false)
  return { collapsed, mobileOpen }
}
