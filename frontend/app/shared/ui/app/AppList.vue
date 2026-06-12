<template>
  <div>
    <div class="flex flex-col gap-4">
      <AppInput
        v-if="showSearch"
        v-model="search"
        icon="lucide:search"
        class="max-w-xs"
        :loading="searchLoading"
        placeholder="Поиск"
      />

      <div
        v-if="items.length"
        :class="contentClass"
      >
        <div v-if="mode === 'list'">
          <div
            v-for="(item, index) in items"
            :key="getItemKey(item, index)"
            class="cursor-pointer hover-bg rounded-md"
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
        </div>

        <div v-else-if="mode === 'table'">
          <DataTable
            :selection="selection"
            :scroll-height="scrollHeight"
            :scrollable="scrollable"
            :value="items"
            table-style="min-width: 50rem"
            selection-mode="single"
            @update:selection="emit('update:selection', $event)"
            @row-click="handleRowClick"
          >
            <template
              v-for="(vnode, index) in columnVNodes"
              :key="index"
            >
              <component :is="vnode" />
            </template>
            <template
              v-if="$slots.footer"
              #footer
            >
              <slot name="footer" />
            </template>
          </DataTable>
        </div>
      </div>
      <div
        v-else
        class="flex items-center"
      >
        <div class="fg-secondary">{{ emptyText }}</div>
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

    <div
      v-if="infiniteScroll && pagination?.has_next"
      ref="infiniteScrollRef"
      class="w-full h-10 flex justify-center items-center mt-4"
    >
      <div
        v-if="loading"
        class="fg-secondary"
      >
        Загрузка...
      </div>
    </div>
  </div>
</template>

<script setup generic="T" lang="ts">
import { Comment, Fragment, Text, type VNode } from 'vue'
import { useIntersectionObserver } from '@vueuse/core'
import Column, { type ColumnProps } from 'primevue/column'
import AppPagination from '../template/AppPagination.vue'
import type { AppPaginationEvent } from '../template/AppPagination.vue'
import type { AppColumnProps } from './AppColumn.vue'
import AppColumn from './AppColumn.vue'

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
  scrollHeight?: string
  emptyText?: string
  infiniteScroll?: boolean
  hasNextPage?: boolean
  loading?: boolean
  handleItemClick?: (item: T, index: number, event?: Event) => void
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
  'list-item'?: (props: { item: T; index: number }) => any
  footer?: () => any
}>()

const slots = useSlots()

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
  const item = event.data
  const index = props.items.indexOf(item)
  handleClick(item, index, event.originalEvent)
}

function getComponentName(type: VNode['type']): string | undefined {
  if (!type || typeof type !== 'object') return undefined
  return (type as { __name?: string; name?: string }).__name ?? (type as { name?: string }).name
}

function flattenSlotVNodes(vnodes: VNode[]): VNode[] {
  return vnodes.flatMap((vnode) => {
    if (!vnode || typeof vnode !== 'object') return []
    if (vnode.type === Comment || vnode.type === Text) return []
    if (vnode.type === Fragment && Array.isArray(vnode.children)) {
      return flattenSlotVNodes(vnode.children as VNode[])
    }
    return [vnode]
  })
}

function isColumnVNode(vnode: VNode): boolean {
  return vnode.type === Column || getComponentName(vnode.type) === 'Column'
}

function isAppColumnVNode(vnode: VNode): boolean {
  return vnode.type === AppColumn || getComponentName(vnode.type) === 'AppColumn'
}

const columnVNodes = computed(() => {
  const defaultSlot = slots.default ? slots.default() : []

  return flattenSlotVNodes(defaultSlot)
    .map((vnode: VNode) => {
      if (isColumnVNode(vnode)) {
        const columnProps = vnode.props as ColumnProps
        return h(Column, columnProps, vnode.children as any)
      }
      if (isAppColumnVNode(vnode)) {
        return h(Column, vnode.props as AppColumnProps, {
          body: (v: any) => {
            return vnode.props?.format?.(v.data, v)
          },
        })
      }
    })
    .filter((v) => !!v)
})

const infiniteScrollRef = ref<HTMLElement | null>(null)

useIntersectionObserver(infiniteScrollRef, (entries) => {
  const isIntersecting = entries[0]?.isIntersecting
  if (isIntersecting && props.infiniteScroll && props.pagination?.has_next && !props.loading) {
    emit('loadMore')
  }
})
</script>
