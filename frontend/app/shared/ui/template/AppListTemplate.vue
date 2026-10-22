<template>
  <component
    :is="templateVariant === 'page' ? AppPageView : AppSection"
    v-bind="sectionBind"
  >
    <template
      v-if="!hideHeader"
      #actions
    >
      <slot name="actions" />
      <AppButton
        v-if="!hideCreateButton && !$slots.actions"
        variant="default"
        @click="handleCreateClick"
      >
        {{ createLabel || 'Создать' }}
      </AppButton>
    </template>

    <template
      v-if="templateVariant === 'page' && (showSearch || filterSpec || $slots['search-actions'] || $slots.filters)"
      #controls
    >
      <AppListToolbar
        v-model:search="listData.search.value"
        v-model:filters="filters"
        :filter-spec="filterSpec"
        :fixed-fields="fixedFields"
        :available-filters="availableFilters"
        class="py-2"
        :show-search="showSearch"
        :search-loading="listData.loading.value"
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
    </template>

    <AppList
      v-bind="listBind"
      v-model:search="listData.search.value"
      :class="templateVariant === 'page' && mode === 'table' && tableBleed && '-mx-3 md:-mx-4'"
      @item-click="onItemClick"
      @load-more="handleLoadMore"
      @update:selection="$emit('update:selection', $event)"
    >
      <template
        v-if="$slots.empty"
        #empty
      >
        <slot
          name="empty"
          :loading="Boolean(listBind.loading)"
        />
      </template>
      <template
        v-if="templateVariant !== 'page' && $slots['search-actions']"
        #search-actions
      >
        <slot name="search-actions" />
      </template>
      <template
        v-if="templateVariant !== 'page' && (filterSpec || $slots.filters)"
        #filters
      >
        <AppListToolbar
          v-model:filters="filters"
          :filter-spec="filterSpec"
          :fixed-fields="fixedFields"
          :available-filters="availableFilters"
        >
          <template #filters><slot name="filters" /></template>
        </AppListToolbar>
      </template>
      <slot />
      <template
        v-if="$slots['list-item']"
        #list-item="slotProps"
      >
        <slot
          name="list-item"
          v-bind="slotProps"
        />
      </template>
      <template
        v-if="$slots.footer"
        #footer
      >
        <slot name="footer" />
      </template>
    </AppList>
  </component>

  <AppModal
    v-model="detailModal"
    :close-label="detailModalProps?.closeLabel"
    :title="detailModalProps?.title || (selectedItem?.id ? 'Обновление' : 'Создание')"
    :width="detailModalProps?.width || '30rem'"
    :class="detailModalProps?.class"
  >
    <!-- @vue-generic {T, F} -->
    <AppDetailTemplate
      v-if="selectedItem && resource"
      class="mb-0!"
      hide-back-button
      mode="inline"
      :resource="resource"
      :item="selectedItem"
      template-variant="flat-section"
      v-bind="detailModalProps"
      :actions-props="{ ...detailModalActionsProps }"
      hide-header
      @cancel="detailModal = false"
      @delete="handleDetailAction"
      @save="handleSave"
    >
      <slot
        name="detail-modal"
        :detail-item="selectedItem"
      />
    </AppDetailTemplate>
  </AppModal>
</template>

<script setup generic="T extends ResourceItem, F extends ResourceForm" lang="ts">
import { watch } from 'vue'
import type { ViewFilters } from '../app/filters/types'
import { deepClone } from '~/shared/lib/clone'
import type { ResourceForm, ResourceItem } from '~/shared/api/resource'
import { useResourceItem } from '~/shared/api/useResource'
import AppListToolbar from '../app/AppListToolbar.vue'
import AppPageView from '../app/AppPageView.vue'
import AppSection from '../app/AppSection.vue'
import type { AppListTemplateProps } from './types/template-types'
import type { AppListProps, ItemClickEvent } from '../app/AppList.vue'
import { useListData } from './composables/useListData'

const props = withDefaults(defineProps<AppListTemplateProps<T, F>>(), {
  mode: 'table',
  tableBleed: true,
  showPagination: true,
  infiniteScroll: true,
  detailRouteParam: 'id',
  contentClass: '',
  searchParam: 'search',
  autoLoad: true,
  templateVariant: 'page',
  detailMode: 'route',
  reloadAfterSave: false,
  retrieveOnOpen: true,
  filter: false,
  showSearch: true,
})

const emit = defineEmits<{
  itemClick: [event: ItemClickEvent<T>]
  rowSelect: [event: { data: T }]
  save: [event: AppDetailActionsSaveResult<F, T>]
  'update:selection': any
}>()

const filters = defineModel<ViewFilters>('filters', { default: () => ({}) })

const router = useRouter()
const toast = useToast()
const selectedItem = shallowRef<F | null>(null)
const detailModal = ref(false)

const sectionBind = useSectionBind(props)
const listData = useListData<T, F>(() => props, filters)

// Modal mode shows the row at once, then replaces it with a fresh `[key, id]` record once that has loaded.
const openedId = ref<string | null>(null)
let hydratedId: string | null = null
const opened = props.resource ? useResourceItem(() => props.resource!, openedId) : null
watch(
  () => [opened?.data.value, opened?.asyncStatus.value] as const,
  ([data, status]) => {
    if (!data || status !== 'idle' || !detailModal.value || !props.resource) return
    if (selectedItem.value?.id !== data.id || hydratedId === data.id) return
    hydratedId = data.id
    selectedItem.value = props.resource.toForm(deepClone(data))
  },
)
watch(
  () => opened?.error.value,
  (error) => {
    if (error && detailModal.value && selectedItem.value?.id === openedId.value)
      toast.error('Не удалось загрузить запись')
  },
)
watch(detailModal, (open) => {
  if (open) return
  openedId.value = null
  hydratedId = null
})

const detailModalActionsProps = computed(() => ({
  hideHeaderActions: true,
  disableRouterAutoResolving: props.detailMode === 'modal',
  ...props.detailModalProps?.actionsProps,
}))

const listBind = computed(
  () =>
    ({
      mode: props.mode,
      contentClass: props.contentClass,
      selection: props.selection,
      scrollable: props.scrollable,
      scrollHeight: props.scrollHeight,
      searchPlaceholder: props.searchPlaceholder,
      tableVariant: props.tableVariant,
      emptyText: props.emptyText,
      infiniteScroll: props.infiniteScroll && listData.remote,
      showPagination: props.showPagination,
      handleItemClick: props.handleItemClick,
      itemKey: 'id' as keyof T,
      items: listData.items.value,
      loading: listData.loading.value,
      searchLoading: listData.loading.value,
      error: listData.error.value ? 'Не удалось загрузить данные' : undefined,
      hasNextPage: listData.hasNextPage.value,
      showSearch: props.showSearch,
      hideToolbar: props.templateVariant === 'page',
    }) as AppListProps<T>,
)

const onItemClick = (event: ItemClickEvent<T>) => {
  emit('itemClick', event)
  _openItem(event.item)
}

const handleCreateClick = () => {
  _openItem(null)
}

const handleSave = (event: AppDetailActionsSaveResult<F, T>) => {
  if (!event.success) return
  if (event.item) selectedItem.value = event.item
  emit('save', event)
  if (props.detailModalProps?.closeOnSave !== false) detailModal.value = false
  if (props.reloadAfterSave) void reload().catch(() => {})
}

const handleDetailAction = (event: AppDetailActionsDeleteResult<F>) => {
  if (!event.success) return
  detailModal.value = false
}

const _openItem = (item: T | null) => {
  if (props.detailMode === 'modal') {
    if (!props.resource) return
    selectedItem.value = item
      ? props.resource.toForm(deepClone(item))
      : (props.buildNewItem?.() ?? props.resource.toForm())
    hydratedId = null
    detailModal.value = true
    openedId.value = item?.id && props.retrieveOnOpen ? item.id : null
    return
  }

  if (props.detailRouteName && props.detailRouteParam) {
    let id: string | number | undefined = item?.id
    if (props.detailRouteId && item) id = props.detailRouteId(item)
    void router.push({
      name: props.detailRouteName,
      params: { [props.detailRouteParam]: id || 'new' },
    })
  }
}

const openItem = (item: T | null = null) => {
  _openItem(item)
}

const reload = () => listData.reload()

const handleLoadMore = () => {
  void listData.loadMore()
}

defineExpose({
  openItem,
  reload,
  getItems: () => listData.items.value,
})
</script>
