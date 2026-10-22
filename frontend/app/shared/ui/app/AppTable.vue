<script setup lang="ts" generic="T">
import { Comment, Fragment, Text, defineComponent, h, useSlots, type VNode, type PropType } from 'vue'
import type { AppColumnProps } from './AppColumn.vue'

export type AppTableVariant = 'default' | 'outline'
export type AppTableColumn = AppColumnProps & { key?: string; label?: string; cellClass?: string }
const props = withDefaults(
  defineProps<{
    variant?: AppTableVariant
    items: T[]
    columns?: AppTableColumn[]
    itemKey?: keyof T | ((item: T, index: number) => string | number)
    clickable?: boolean
    selection?: T | T[]
    loading?: boolean
    error?: string
    loadingText?: string
    emptyText?: string
    scrollHeight?: string
  }>(),
  { variant: 'default', clickable: false, emptyText: 'Данные отсутствуют' },
)
const emit = defineEmits<{ rowClick: [event: { data: T; index: number; originalEvent: Event }] }>()
const slots = useSlots()
const flatten = (nodes: VNode[]): VNode[] =>
  nodes.flatMap((node) => {
    if (node.type === Comment || node.type === Text) return []
    if (node.type === Fragment && Array.isArray(node.children)) return flatten(node.children as VNode[])
    return [node]
  })
const getColumns = () =>
  props.columns?.map((column) => ({
    props: {
      ...column,
      field: column.field ?? column.key,
      header: column.header ?? column.label,
      bodyClass: column.bodyClass ?? column.cellClass,
    },
    children: undefined,
  })) ??
  flatten(slots.default?.() ?? [])
    .filter((node) => {
      const type = node.type as { name?: string; __name?: string }
      return (type.name ?? type.__name) === 'AppColumn'
    })
    .map((node) => ({ props: (node.props ?? {}) as AppColumnProps, children: node.children }))
const CellContent = defineComponent({
  props: {
    cellColumn: { type: Object as PropType<ReturnType<typeof getColumns>[number]>, required: true },
    cellItem: { type: null, required: true },
    cellIndex: { type: Number, required: true },
  },
  setup(cell) {
    return () => {
      const scope = { data: cell.cellItem, item: cell.cellItem, index: cell.cellIndex }
      const body = (cell.cellColumn.children as { body?: (scope: unknown) => VNode[] } | null)?.body
      if (body) return body(scope)
      const { field, format } = cell.cellColumn.props
      const value = format
        ? format(cell.cellItem, scope)
        : field?.split('.').reduce((value: any, key) => value?.[key], cell.cellItem)
      return h('span', String(value ?? '—'))
    }
  },
})
const keyFor = (item: T, index: number) => {
  if (typeof props.itemKey === 'function') return props.itemKey(item, index)
  const value = props.itemKey ? item[props.itemKey] : (item as { id?: unknown })?.id
  return typeof value === 'string' || typeof value === 'number' ? value : index
}
const activate = (item: T, index: number, event: Event) => {
  if (!props.clickable) return
  const target = event.target as HTMLElement
  if (
    target !== event.currentTarget &&
    target.closest('button,a,input,select,textarea,[role="button"],[role="checkbox"],[data-row-action]')
  )
    return
  if (event instanceof KeyboardEvent) event.preventDefault()
  emit('rowClick', { data: item, index, originalEvent: event })
}
</script>
<template>
  <div
    class="min-w-0 overflow-auto"
    :class="variant === 'outline' && 'rounded-md border border-border'"
    :style="scrollHeight ? { maxHeight: scrollHeight } : undefined"
    :aria-busy="loading"
  >
    <table class="w-full caption-bottom text-[13px]">
      <thead
        class="border-b border-border text-xs text-muted-foreground"
        :class="variant === 'outline' && 'bg-muted/30'"
      >
        <tr>
          <th
            v-for="(column, index) in getColumns()"
            :key="index"
            scope="col"
            class="h-10 px-3 py-2 text-left font-medium"
            :class="column.props.headerClass"
            :style="column.props.style"
          >
            {{ column.props.header }}
          </th>
        </tr>
      </thead>
      <tbody class="[&_tr:last-child]:border-0">
        <tr
          v-for="(item, index) in items"
          :key="keyFor(item, index)"
          class="h-10 border-b border-border transition-colors"
          :class="[
            clickable &&
              'cursor-pointer hover:bg-muted/50 focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none focus-visible:ring-inset',
            selection === item && 'bg-muted',
          ]"
          :tabindex="clickable ? 0 : undefined"
          @click="activate(item, index, $event)"
          @keydown.enter="activate(item, index, $event)"
          @keydown.space="activate(item, index, $event)"
        >
          <td
            v-for="(column, colIndex) in getColumns()"
            :key="colIndex"
            class="px-3 py-2 align-middle"
            :class="column.props.bodyClass"
            :style="column.props.style"
          >
            <slot
              :name="`cell-${column.props.field ?? colIndex}`"
              :item="item"
              :column="column.props"
              :value="column.props.field ? (item as Record<string, unknown>)[column.props.field] : undefined"
            >
              <CellContent
                :cell-column="column"
                :cell-item="item"
                :cell-index="index"
              />
            </slot>
          </td>
        </tr>
        <tr v-if="!items.length">
          <td
            :colspan="Math.max(1, getColumns().length)"
            class="h-28 px-3 text-center text-muted-foreground"
          >
            <slot
              name="empty"
              :loading="loading"
            >
              <AppLoadingIndicator
                v-if="loading"
                :label="loadingText"
              /><span
                v-else
                :role="error ? 'alert' : undefined"
                :class="error && 'text-destructive'"
                >{{ error || emptyText }}</span
              >
            </slot>
          </td>
        </tr>
        <tr v-else-if="loading || error">
          <td
            :colspan="Math.max(1, getColumns().length)"
            class="p-3 text-center"
          >
            <AppLoadingIndicator
              v-if="loading"
              :label="loadingText"
            /><span
              v-else
              role="alert"
              class="text-destructive"
              >{{ error }}</span
            >
          </td>
        </tr>
      </tbody>
      <tfoot v-if="$slots.footer">
        <tr>
          <td
            :colspan="Math.max(1, getColumns().length)"
            class="border-t border-border p-3"
          >
            <slot name="footer" />
          </td>
        </tr>
      </tfoot>
    </table>
  </div>
</template>
