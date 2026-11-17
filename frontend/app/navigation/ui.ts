import type { SidebarSection } from '~/shared/components/layout/sidebar/types'
import { uiCatalog } from '~/features/ui/catalog'

// Sidebar of the `/ui` catalogue: one group per catalogue group, one link per section (`/ui/<key>`).
export const uiNavigation: SidebarSection[] = uiCatalog.map((group) => ({
  title: group.title,
  items: group.sections.map((section) => ({
    to: { name: 'ui-section', params: { section: section.key } },
    label: section.title,
    icon: section.icon,
  })),
}))
