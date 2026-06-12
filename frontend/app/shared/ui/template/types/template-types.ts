import type { UseRepoDataProps } from '../../../toolkits/repo/composables/useRepoData'
import type { AppButtonProps } from '../../app/AppButton.vue'
import type { AppListProps } from '../../app/AppList.vue'
import type { AppDetailActionsProps } from '../AppDetailActions.vue'
import type { ActionDisplayMode } from './template-ui-tokens'
import type { AppSectionProps } from '../../app/AppSection.vue'

export type AppTemplateAction = AppButtonProps & {
  action?: () => Promise<void> | void
  hidden?: boolean
  mode?: ActionDisplayMode
  successNotification?: string
  errorNotification?: string
}

export type AppDetailTemplateActionsProps<T extends AppModel> = Omit<AppDetailActionsProps<T>, 'repo' | 'item'> & {
  hidden?: boolean
  hideHeaderActions?: boolean
}

export type AppDetailTemplateProps<T extends AppModel> = AppSectionProps & {
  repo: AppRepoStore<T>
  item?: T | null
  detailRouteParam?: string
  buildNewItem?: () => T
  listRouteName?: string
  fluid?: boolean
  hideBackButton?: boolean
  hideHeader?: boolean
  mode?: 'page' | 'inline'
  actionsProps?: AppDetailTemplateActionsProps<T>
}

export type AppListTemplateBaseProps<T> = AppSectionProps & {
  hideCreateButton?: boolean
  hideHeader?: boolean
  detailMode?: 'modal' | 'route'
  detailRouteName?: string
  detailRouteParam?: string
  buildNewItem?: () => T
}

export type AppListTemplateRepoManagedProps =
  | 'items'
  | 'pagination'
  | 'loading'
  | 'paginationLoading'
  | 'searchLoading'
  | 'hasNextPage'

export type AppListTemplateDetailModalProps<T extends AppModel> = Omit<
  AppDetailTemplateProps<T>,
  'repo' | 'item'
> & {
  width?: string
  closeOnSave?: boolean
}

export type AppListTemplateProps<T extends AppModel> = AppListTemplateBaseProps<T> &
  UseRepoDataProps<T> &
  Omit<AppListProps<T>, AppListTemplateRepoManagedProps> & {
    detailRouteId?: (item: T) => string | number
    reloadAfterSave?: boolean
    detailModalProps?: AppListTemplateDetailModalProps<T>
  }
