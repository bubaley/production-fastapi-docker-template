<template>
  <div
    :class="infiniteScroll && scrollHeight && 'overflow-auto'"
    :style="infiniteScroll && scrollHeight ? { maxHeight: scrollHeight } : undefined"
  >
    <div class="flex flex-col gap-4">
      <AppListToolbar
        v-if="!hideToolbar && (showSearch || $slots['search-actions'] || $slots.filters)"
        v-model:search="search"
        class="sticky top-0 z-10 bg-background"
        :show-search="showSearch"
        :search-loading="searchLoading"
        :search-placeholder="searchPlaceholder"
      >
        <template
          v-if="$slots['search-actions']"
          #search-actions
        >
          <slot name="search-actions" />
        </template>
        <template
          v-if="$slots.filters"
          #filters
        >
          <slot name="filters" />
        </template>
      </AppListToolbar>

      <AppTable
        v-if="mode === 'table'"
        :items="items"
        :selection="selection"
        :item-key="itemKey"
        :loading="loading"
        :error="error"
        :empty-text="emptyText"
        :scroll-height="infiniteScroll ? undefined : scrollHeight"
        :variant="tableVariant"
        clickable
        @row-click="handleRowClick"
      >
        <slot />
        <template
          v-if="$slots.empty"
          #empty="scope"
        >
          <slot
            name="empty"
            v-bind="scope"
          />
        </template>
        <template
          v-if="$slots.footer"
          #footer
        >
          <slot name="footer" />
        </template>
      </AppTable>
      <div
        v-else
        :class="contentClass"
      >
        <div
          v-for="(item, index) in items"
          :key="getItemKey(item, index)"
          class="cursor-pointer rounded-md hover:bg-muted/50"
          @click="handleClick(item, index, $event)"
        >
          <slot
            name="list-item"
            :item="item"
            :index="index"
          >
            <slot
              :item="item"
              :index="index"
            />
          </slot>
        </div>
        <slot
          v-if="!items.length"
          name="empty"
          :loading="loading"
        >
          <AppLoadingIndicator
            v-if="loading"
            fluid
          />
          <p
            v-else
            class="py-6 text-sm text-muted-foreground"
          >
            {{ error || emptyText }}
          </p>
        </slot>
      </div>
    </div>

    <AppPagination
      v-if="showPagination && pagination?.has_next && !infiniteScroll"
      v-model="page"
      :loading="loading"
      class="mt-4"
      :pagination="pagination"
      @page-change="emit('pageChange', $event)"
    />

    <AppInfiniteScroll
      v-if="infiniteScroll"
      :has-more="Boolean(pagination?.has_next)"
      :request-key="`${search}:${pagination?.page}:${items.length}`"
      :loading="loading && items.length > 0"
      :error="error"
      @load="emit('loadMore')"
      @retry="emit('loadMore')"
    />
  </div>
</template>

<script setup generic="T" lang="ts">
import AppListToolbar from './AppListToolbar.vue'
import AppPagination from '../template/AppPagination.vue'
import type { AppPaginationEvent } from '../template/AppPagination.vue'

export interface ItemClickEvent<T> {
  item: T
  index: number
  event: Event
}

export type AppListDisplayMode = 'list' | 'table'

export type AppListProps<T> = {
  items: T[]
  mode?: AppListDisplayMode
  selection?: T | T[]
  itemKey?: keyof T | ((item: T, index: number) => string | number)
  contentClass?: string
  scrollable?: boolean
  tableVariant?: import('./AppTable.vue').AppTableVariant
  searchPlaceholder?: string
  scrollHeight?: string
  error?: string
  emptyText?: string
  infiniteScroll?: boolean
  hasNextPage?: boolean
  loading?: boolean
  handleItemClick?: (item: T, index: number, event?: Event) => void
  hideToolbar?: boolean
  showSearch?: boolean
  searchLoading?: boolean
  showPagination?: boolean
  pagination?: AppPagination
  paginationLoading?: boolean
}

const props = withDefaults(defineProps<AppListProps<T>>(), {
  mode: 'table',
  emptyText: 'Данные отсутствуют',
  infiniteScroll: false,
  hasNextPage: false,
  loading: false,
  showSearch: false,
  hideToolbar: false,
  searchLoading: false,
  showPagination: true,
  paginationLoading: false,
})

const search = defineModel<string>('search', { default: '' })
const page = defineModel<number>('page', { default: 1 })

const emit = defineEmits<{
  itemClick: [event: ItemClickEvent<T>]
  rowSelect: [event: { data: T }]
  loadMore: []
  pageChange: [event: AppPaginationEvent]
  'update:selection': [selection: T | T[] | undefined]
}>()

defineSlots<{
  default?: () => any
  filters?: () => any
  'search-actions'?: () => any
  'list-item'?: (props: { item: T; index: number }) => any
  footer?: () => any
  empty?: (props: { loading: boolean }) => any
}>()

const getItemKey = (item: T, index: number): string | number => {
  if (!props.itemKey) return index
  if (typeof props.itemKey === 'function') return props.itemKey(item, index)
  const key = item[props.itemKey]
  if (typeof key === 'string' || typeof key === 'number') return key
  return index
}

const handleClick = (item: T, index: number, event?: Event) => {
  if (props.handleItemClick) {
    props.handleItemClick(item, index, event)
    return
  }

  emit('itemClick', {
    item,
    index,
    event: event || new Event('click'),
  })
}

const handleRowClick = (event: { data: T; originalEvent: Event }) => {
  emit('update:selection', event.data)
  emit('rowSelect', { data: event.data })
  const item = event.data
  const index = props.items.indexOf(item)
  handleClick(item, index, event.originalEvent)
}
</script>
