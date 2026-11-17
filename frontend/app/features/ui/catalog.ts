import {
  AppWindow,
  BellRing,
  CalendarDays,
  CircleCheckBig,
  CircleDashed,
  Filter,
  Inbox,
  LayoutTemplate,
  Layers,
  ListFilter,
  Loader,
  MousePointerClick,
  Palette,
  PanelRight,
  PanelsTopLeft,
  Pipette,
  Rows3,
  Shapes,
  Ruler,
  SquareMenu,
  Table,
  Tags,
  TextCursorInput,
  ToggleRight,
  Type,
  Columns3,
  MessageSquareWarning,
  WalletCards,
} from '@lucide/vue'
import type { Component } from 'vue'

export type UiCatalogSection = {
  /** Route segment: `/ui/<key>`. */
  key: string
  title: string
  icon: Component
  /** The usage rule shown under the title: when to reach for these components. */
  description: string
  /** Components and composables the section demonstrates. */
  components: string[]
  load: () => Promise<{ default: Component }>
}

export type UiCatalogGroup = { title: string; sections: UiCatalogSection[] }

// The order here is the order of the catalogue sidebar; `/ui` opens the first section.
export const uiCatalog: UiCatalogGroup[] = [
  {
    title: 'Foundations',
    sections: [
      {
        key: 'colors',
        title: 'Colors',
        icon: Palette,
        description:
          'Every color is a token from assets/styles/theme.css used through utilities (bg-card, text-success). No hex values in components; switch theme and palette in the sidebar to compare.',
        components: ['theme.css', 'useTheme', 'AppThemeSwitcher'],
        load: () => import('./sections/foundations/ColorsSection.vue'),
      },
      {
        key: 'typography',
        title: 'Typography',
        icon: Type,
        description:
          'AppTitle renders the heading tag and maps sizes to the type scale. The rem base is 14px (--font-size-root); body text is text-sm.',
        components: ['AppTitle'],
        load: () => import('./sections/foundations/TypographySection.vue'),
      },
      {
        key: 'sizing',
        title: 'Radius and sizes',
        icon: Ruler,
        description:
          'Radii derive from --radius; control heights from --size-control-*. Buttons, inputs, selects and switches share the same xs–lg scale.',
        components: ['rounded-*', 'h-control-*'],
        load: () => import('./sections/foundations/SizingSection.vue'),
      },
      {
        key: 'shadows',
        title: 'Shadows',
        icon: Layers,
        description:
          'Surfaces on the page are flat and separated by borders. One soft shadow, shadow-overlay, marks every floating surface: menus, popovers, pickers, tooltips and dialogs.',
        components: ['shadow-overlay', 'AppCard'],
        load: () => import('./sections/foundations/ShadowsSection.vue'),
      },
      {
        key: 'icons',
        title: 'Icons',
        icon: Shapes,
        description:
          'AppIcon renders a Lucide component at a size of the scale, with an optional tone or a loading spinner. Import icons from @lucide/vue and pass the component.',
        components: ['AppIcon'],
        load: () => import('./sections/foundations/IconsSection.vue'),
      },
    ],
  },
  {
    title: 'Actions',
    sections: [
      {
        key: 'buttons',
        title: 'Buttons',
        icon: MousePointerClick,
        description:
          'AppButton is the only button. One main action per area; a row of two or more goes through AppTemplateActions. Icon-only buttons are square and need aria-label.',
        components: ['AppButton', 'AppTextButton', 'AppTemplateActions', 'AppThemeToggle'],
        load: () => import('./sections/actions/ButtonsSection.vue'),
      },
      {
        key: 'menus',
        title: 'Menus',
        icon: SquareMenu,
        description:
          'AppMenu is the one overlay primitive: an action list on click (mode="menu") or on right click (mode="cursor"). Destructive items go last after a separator.',
        components: ['AppMenu'],
        load: () => import('./sections/actions/MenusSection.vue'),
      },
    ],
  },
  {
    title: 'Forms',
    sections: [
      {
        key: 'inputs',
        title: 'Inputs',
        icon: TextCursorInput,
        description:
          'Label above the control, hint or error below. Text, search, number and multi-line fields share sizes and one focus ring.',
        components: ['AppInput', 'AppNumberInput', 'AppTextarea', 'AppField'],
        load: () => import('./sections/forms/InputsSection.vue'),
      },
      {
        key: 'selects',
        title: 'Selects',
        icon: ListFilter,
        description:
          'AppSelect works with a local items list or a paginated source. Loaded options stay on screen while it refetches.',
        components: ['AppSelect'],
        load: () => import('./sections/forms/SelectsSection.vue'),
      },
      {
        key: 'dates',
        title: 'Dates',
        icon: CalendarDays,
        description:
          'AppDatePicker for a date or date and time, AppDateRangePicker for a period. Format dates with useDate().',
        components: ['AppDatePicker', 'AppDateRangePicker', 'AppDateLabel'],
        load: () => import('./sections/forms/DatesSection.vue'),
      },
      {
        key: 'choice',
        title: 'Checkbox, switch, radio',
        icon: ToggleRight,
        description:
          'A switch applies at once; a checkbox is part of a form that is saved. A radio group picks one of a few visible options.',
        components: ['AppCheckbox', 'AppSwitch', 'AppRadioGroup'],
        load: () => import('./sections/forms/ChoiceSection.vue'),
      },
      {
        key: 'pickers',
        title: 'Color and icon',
        icon: Pipette,
        description: 'AppColorPicker and AppAppearancePicker let a user pick a color and a Lucide icon for an entity.',
        components: ['AppColorPicker', 'AppAppearancePicker'],
        load: () => import('./sections/forms/PickersSection.vue'),
      },
      {
        key: 'filters',
        title: 'Filters',
        icon: Filter,
        description:
          'AppFilterToolbar builds list conditions from a field spec: + adds a condition, fixed fields stay visible.',
        components: ['AppFilterToolbar', 'ViewFilterSpec'],
        load: () => import('./sections/forms/FiltersSection.vue'),
      },
    ],
  },
  {
    title: 'Data',
    sections: [
      {
        key: 'labels',
        title: 'Labels and badges',
        icon: Tags,
        description:
          'One tone vocabulary (tone.ts) for labels, badges and values. A status is an AppLabelConfig { label, icon, tone }; an empty value is AppEmptyData.',
        components: ['AppLabel', 'AppDataLabel', 'AppBadge', 'AppEmptyData'],
        load: () => import('./sections/data/LabelsSection.vue'),
      },
      {
        key: 'cards',
        title: 'Cards and avatars',
        icon: WalletCards,
        description:
          'AppCard is a visible surface; AppSection only groups content. Tint a card with tone only when the color carries meaning.',
        components: ['AppCard', 'AppAvatar'],
        load: () => import('./sections/data/CardsSection.vue'),
      },
      {
        key: 'tables',
        title: 'Tables',
        icon: Table,
        description:
          'AppTable with declarative AppColumn. The header stays visible through loading, empty and error states; row actions do not open the row.',
        components: ['AppTable', 'AppColumn'],
        load: () => import('./sections/data/TablesSection.vue'),
      },
      {
        key: 'templates',
        title: 'List and detail templates',
        icon: LayoutTemplate,
        description:
          'AppListTemplate and AppDetailTemplate own CRUD through a resource descriptor: search, pagination, modal or route detail, save and delete.',
        components: ['AppListTemplate', 'AppDetailTemplate', 'defineResource'],
        load: () => import('./sections/data/TemplatesSection.vue'),
      },
    ],
  },
  {
    title: 'Feedback',
    sections: [
      {
        key: 'empty-state',
        title: 'Empty state',
        icon: Inbox,
        description:
          'In place of a list, table or block with nothing to show. Says what will appear here, why it is empty and what to do: one primary action, at most one secondary.',
        components: ['AppEmptyState'],
        load: () => import('./sections/feedback/EmptyStateSection.vue'),
      },
      {
        key: 'result-state',
        title: 'Result state',
        icon: CircleCheckBig,
        description:
          'The outcome of a flow or a whole-page error: a confirmed email, a missing page. Not for empty lists — use AppEmptyState there.',
        components: ['AppResultState'],
        load: () => import('./sections/feedback/ResultStateSection.vue'),
      },
      {
        key: 'alerts',
        title: 'Alerts',
        icon: MessageSquareWarning,
        description:
          'A message inside the page: an explanation, a warning or an error. It is part of the content and does not close itself.',
        components: ['AppAlert'],
        load: () => import('./sections/feedback/AlertsSection.vue'),
      },
      {
        key: 'toasts',
        title: 'Toasts',
        icon: BellRing,
        description:
          'useToast reports the result of an action the user just took. Errors that need attention stay on the page instead.',
        components: ['useToast'],
        load: () => import('./sections/feedback/ToastsSection.vue'),
      },
      {
        key: 'progress',
        title: 'Progress and loading',
        icon: Loader,
        description:
          'AppProgress for a known share, AppLoadingIndicator for a short wait, AppSkeleton in place of content that is loading.',
        components: ['AppProgress', 'AppCircularProgress', 'AppLoadingIndicator', 'AppSkeleton'],
        load: () => import('./sections/feedback/ProgressSection.vue'),
      },
    ],
  },
  {
    title: 'Layout',
    sections: [
      {
        key: 'page',
        title: 'Page shell',
        icon: PanelsTopLeft,
        description:
          'AppPageView: one heading row with actions (primary first, ⋯ last), optional subheader and controls, a scrolling body and a fixed footer.',
        components: ['AppPageView', 'AppSection'],
        load: () => import('./sections/layout/PageSection.vue'),
      },
      {
        key: 'tabs',
        title: 'Tabs',
        icon: Columns3,
        description: 'AppTabs switches sections of one screen. query-key keeps the active tab in the URL.',
        components: ['AppTabs', 'AppTabPanel'],
        load: () => import('./sections/layout/TabsSection.vue'),
      },
      {
        key: 'settings-rows',
        title: 'Settings rows and scroll',
        icon: Rows3,
        description:
          'AppSettingRow puts a label and description next to its control and stacks on phones. AppScrollArea bounds a region with thin scrollbars.',
        components: ['AppSettingRow', 'AppScrollArea'],
        load: () => import('./sections/layout/SettingsRowsSection.vue'),
      },
    ],
  },
  {
    title: 'Overlays',
    sections: [
      {
        key: 'modals',
        title: 'Modals',
        icon: AppWindow,
        description:
          'AppModal for a focused task, AppConfirmModal before a destructive action, AppUnsavedChangesModal before losing edits. Footer buttons go through AppTemplateActions.',
        components: ['AppModal', 'AppConfirmModal', 'AppUnsavedChangesModal'],
        load: () => import('./sections/overlays/ModalsSection.vue'),
      },
      {
        key: 'drawers',
        title: 'Drawers',
        icon: PanelRight,
        description:
          'AppDrawer is a side sheet for secondary settings without leaving the page. Surfaces opened from it stack above it.',
        components: ['AppDrawer'],
        load: () => import('./sections/overlays/DrawersSection.vue'),
      },
      {
        key: 'popovers',
        title: 'Popovers and tooltips',
        icon: CircleDashed,
        description:
          'AppMenu mode="popover" holds a small free-form task (it gets close()). AppTooltip explains a control on hover or focus. The image lightbox opens from a store.',
        components: ['AppMenu', 'AppTooltip', 'useAppImageLightboxStore'],
        load: () => import('./sections/overlays/PopoversSection.vue'),
      },
    ],
  },
]

export const uiSections: UiCatalogSection[] = uiCatalog.flatMap((group) => group.sections)

export const findUiSection = (key: string): { group: UiCatalogGroup; section: UiCatalogSection } | null => {
  for (const group of uiCatalog) {
    const section = group.sections.find((item) => item.key === key)
    if (section) return { group, section }
  }
  return null
}
