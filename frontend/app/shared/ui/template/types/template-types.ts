import type { MaybeRefOrGetter } from 'vue'
import type { ViewFilterSpec, ViewFixedField } from '../../app/filters/types'
import type { AppButtonProps } from '../../app/AppButton.vue'
import type { AppListProps } from '../../app/AppList.vue'
import type { AppDetailActionsProps } from '../AppDetailActions.vue'
import type { ActionDisplayMode } from './template-ui-tokens'
import type { AppSectionProps } from '../../app/AppSection.vue'
import type { ListQuery, Resource, ResourceForm, ResourceItem } from '~/shared/api/resource'

export type AppTemplateAction = AppButtonProps & {
  class?: string
  action?: () => Promise<void> | void
  hidden?: boolean
  mode?: ActionDisplayMode
  successNotification?: string
  errorNotification?: string
}

export type AppDetailTemplateActionsProps<F extends ResourceForm> = Omit<
  AppDetailActionsProps<ResourceItem, F>,
  'resource' | 'item'
> & {
  hidden?: boolean
  hideHeaderActions?: boolean
}

export type AppDetailTemplateProps<T extends ResourceItem, F extends ResourceForm> = AppSectionProps & {
  resource: Resource<T, F, any, any>
  /** Form state owned by the caller (modal mode); without it the template loads the record from the route. */
  item?: F | null
  detailRouteParam?: string
  buildNewItem?: () => F
  listRouteName?: string
  fluid?: boolean
  hideBackButton?: boolean
  hideHeader?: boolean
  mode?: 'page' | 'inline'
  actionsProps?: AppDetailTemplateActionsProps<F>
}

/** Where list rows come from: an API resource (Pinia Colada infinite query) or local `items`. */
export type AppListDataProps<T extends ResourceItem, F extends ResourceForm = ResourceForm> = {
  resource?: Resource<T, F, any, any>
  items?: T[]
  /** Query parameter for the search box (`name` for organizations). */
  searchParam?: string
  debounce?: number
  /** Filter `items` locally instead of querying the resource. */
  onlyClientSearch?: boolean
  filterFields?: (keyof T)[]
  filter?: boolean
  /** Extra list query parameters (scope such as `{ organization_id }`); reactive values restart from page 1. */
  extraParams?: MaybeRefOrGetter<ListQuery>
  autoLoad?: boolean
  pageSize?: number
  itemLabel?: string | ((v: T) => string)
  itemValue?: string | ((v: T) => string)
}

export type AppListTemplateBaseProps<F> = AppSectionProps & {
  filterSpec?: ViewFilterSpec
  fixedFields?: ViewFixedField[]
  availableFilters?: string[]
  tableBleed?: boolean
  createLabel?: string
  hideCreateButton?: boolean
  hideHeader?: boolean
  detailMode?: 'modal' | 'route'
  detailRouteName?: string
  detailRouteParam?: string
  buildNewItem?: () => F
}

export type AppListTemplateDataManagedProps = 'items' | 'loading' | 'searchLoading' | 'hasNextPage'

export type AppListTemplateDetailModalProps<T extends ResourceItem, F extends ResourceForm> = Omit<
  AppDetailTemplateProps<T, F>,
  'resource' | 'item'
> & {
  width?: string
  closeLabel?: string
  closeOnSave?: boolean
}

export type AppListTemplateProps<T extends ResourceItem, F extends ResourceForm> = AppListTemplateBaseProps<F> &
  AppListDataProps<T, F> &
  Omit<AppListProps<T>, AppListTemplateDataManagedProps> & {
    detailRouteId?: (item: T) => string | number
    reloadAfterSave?: boolean
    retrieveOnOpen?: boolean
    detailModalProps?: AppListTemplateDetailModalProps<T, F>
  }
