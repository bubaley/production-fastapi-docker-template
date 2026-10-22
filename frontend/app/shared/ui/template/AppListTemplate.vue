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
        v-model:search="repoData.search.value"
        v-model:filters="filters"
        :filter-spec="filterSpec"
        :fixed-fields="fixedFields"
        :available-filters="availableFilters"
        class="py-2"
        :show-search="showSearch"
        :search-loading="repoData.loading.value"
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
      v-model:page="page"
      v-model:search="repoData.search.value"
      :class="templateVariant === 'page' && mode === 'table' && tableBleed && '-mx-3 md:-mx-4'"
      @item-click="onItemClick"
      @load-more="handleLoadMore"
      @page-change="handlePageChange"
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
    <!-- @vue-generic {T} -->
    <AppDetailTemplate
      v-if="selectedItem && detailRepo"
      class="mb-0!"
      hide-back-button
      mode="inline"
      :repo="detailRepo"
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

<script setup generic="T extends AppModel" lang="ts">
import { toValue, watch } from 'vue'
import type { ViewFilters } from '../app/filters/types'
import { deepClone } from '~/shared/lib/clone'
import AppListToolbar from '../app/AppListToolbar.vue'
import AppPageView from '../app/AppPageView.vue'
import AppSection from '../app/AppSection.vue'
import type { AppListTemplateProps } from './types/template-types'
import type { AppListProps, ItemClickEvent } from '../app/AppList.vue'
import type { AppPaginationEvent } from './AppPagination.vue'

const props = withDefaults(defineProps<AppListTemplateProps<T>>(), {
  mode: 'table',
  tableBleed: true,
  showPagination: true,
  infiniteScroll: true,
  detailRouteParam: 'id',
  contentClass: '',
  searchParam: 'search',
  storeInRepo: true,
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
  pageChange: [event: AppPaginationEvent]
  'update:selection': any
}>()

const filters = defineModel<ViewFilters>('filters', { default: () => ({}) })

const router = useRouter()
const itemsRef = computed<T[] | undefined>(() => props.items)
const selectedItem = shallowRef<T | null>(null)
const detailModal = ref(false)
const detailRepo = computed(() => props.repo as AppRepoStore<T> | undefined)
watch(
  () => props.repo?.revision,
  () => {
    selectedItem.value = null
    detailModal.value = false
  },
  { flush: 'sync' },
)

const sectionBind = useSectionBind(props)

const repoData = useRepoData<T>({
  ...props,
  items: itemsRef,
  extraParams: () => ({ ...filters.value, ...toValue(props.extraParams ?? {}) }),
  storeInRepo: props.storeInRepo,
})

const detailModalActionsProps = computed(() => ({
  hideHeaderActions: true,
  disableRouterAutoResolving: props.detailMode === 'modal',
  ...props.detailModalProps?.actionsProps,
}))

const page = computed({
  get: () => repoData.pagination.value.page,
  set: (value: number) => {
    repoData.pagination.value.page = value
  },
})
const hasNextPage = computed(() => repoData.pagination.value.has_next)

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
      infiniteScroll: props.infiniteScroll && Boolean(props.repo) && !props.onlyClientSearch,
      showPagination: props.showPagination,
      handleItemClick: props.handleItemClick,
      itemKey: 'id' as keyof T,
      items: repoData.items.value,
      loading: repoData.loading.value,
      pagination: repoData.pagination.value,
      paginationLoading: repoData.loading.value,
      searchLoading: repoData.loading.value,
      error: repoData.error.value ? 'Не удалось загрузить данные' : undefined,
      hasNextPage: hasNextPage.value,
      showSearch: props.showSearch,
      hideToolbar: props.templateVariant === 'page',
    }) as AppListProps<T>,
)

const { updateListItem, deleteListItem } = useListEvents({
  items: computed(() => repoData.items.value),
  key: 'id' as keyof T,
})

const onItemClick = (event: ItemClickEvent<T>) => {
  emit('itemClick', event)
  _openItem(event.item)
}

const handleCreateClick = () => {
  _openItem(null)
}

const handleSave = (event: AppDetailActionsSaveResult<T>) => {
  if (!event.success) return
  if (event.item) {
    selectedItem.value = event.item
    updateListItem(deepClone(event.item))
  }

  if (props.detailModalProps?.closeOnSave !== false) {
    detailModal.value = false
  }

  if (props.reloadAfterSave) {
    void reload().catch(() => {})
  }
}

const handleDetailAction = (event: AppDetailActionsDeleteResult<T>) => {
  if (!event.success) return
  if (event.item) {
    deleteListItem(event.item)
  }
  detailModal.value = false
}

const _openItem = (item: T | null) => {
  if (props.detailMode === 'modal') {
    if (item) selectedItem.value = deepClone(item)
    else selectedItem.value = props.buildNewItem?.() || props.repo?.decode({})
    detailModal.value = true
    if (item?.id && props.retrieveOnOpen && props.repo) {
      const openedId = item.id
      void props.repo
        .retrieve(openedId, undefined, undefined, { storeInRepo: false })
        .then((retrieved) => {
          if (!retrieved || !detailModal.value) return
          if (String(selectedItem.value?.id) !== String(openedId)) return
          selectedItem.value = deepClone(retrieved)
        })
        .catch(() => {
          if (detailModal.value && String(selectedItem.value?.id) === String(openedId)) {
            useToast().error('Не удалось загрузить запись')
          }
        })
    }
    return
  }

  if (props.detailRouteName && props.detailRouteParam) {
    let id = item?.id
    if (props.detailRouteId && item) id = props.detailRouteId(item)
    router.push({
      name: props.detailRouteName,
      params: { [props.detailRouteParam]: id || 'new' },
    })
  }
}

const openItem = (item: T | null = null) => {
  _openItem(item)
}

const handlePageChange = async (event: AppPaginationEvent) => {
  if (!props.repo) return

  try {
    await repoData.loadItems(undefined, {
      pagination: event.pagination,
      mode: event.append ? 'append' : 'replace',
    })
    emit('pageChange', event)
  } catch (error) {
    console.error('Error loading page:', error)
  }
}

const reload = () =>
  repoData.loadItems(undefined, {
    pagination: paginationFromServer({ size: repoData.pagination.value.size }),
  })

const handleLoadMore = () => {
  if (!props.repo || repoData.loading.value) return
  if (!hasNextPage.value) {
    if (repoData.error.value) void repoData.loadItems().catch(() => {})
    return
  }

  void handlePageChange({
    append: true,
    pagination: { ...repoData.pagination.value, page: repoData.pagination.value.page + 1 },
  })
}

defineExpose({
  openItem,
  reload,
  getItems: () => repoData.items.value,
})
</script>
