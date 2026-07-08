<template>
  <AppSection v-bind="sectionBind">
    <template
      v-if="!hideCreateButton && !hideHeader"
      #actions
    >
      <AppButton
        severity="secondary"
        @click="handleCreateClick"
      >
        Создать
      </AppButton>
    </template>

    <AppList
      v-bind="listBind"
      v-model:page="page"
      v-model:search="repoData.search.value"
      @item-click="onItemClick"
      @load-more="handleLoadMore"
      @page-change="handlePageChange"
      @update:selection="$emit('update:selection', $event)"
    >
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
  </AppSection>

  <AppModal
    v-model="detailModal"
    :width="detailModalProps?.width || '30rem'"
  >
    <AppDetailTemplate
      v-if="selectedItem && repo"
      class="mb-0!"
      hide-back-button
      mode="inline"
      :repo="repo"
      :item="selectedItem"
      template-variant="flat-section"
      v-bind="detailModalProps"
      :actions-props="detailModalActionsProps"
      :title="detailModalProps?.title || (selectedItem?.id ? 'Обновление' : 'Создание')"
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
import { cloneDeep } from 'lodash-es'
import type { AppListTemplateProps } from './types/template-types'
import type { AppListProps, ItemClickEvent } from '../app/AppList.vue'
import type { AppPaginationEvent } from './AppPagination.vue'

const props = withDefaults(defineProps<AppListTemplateProps<T>>(), {
  mode: 'table',
  showPagination: true,
  infiniteScroll: false,
  detailRouteParam: 'id',
  contentClass: '',
  searchParam: 'search',
  storeInRepo: true,
  autoLoad: true,
  templateVariant: 'page',
  detailMode: 'route',
  reloadAfterSave: false,
  filter: false,
  showSearch: true,
})

const emit = defineEmits<{
  itemClick: [event: ItemClickEvent<T>]
  rowSelect: [event: { data: T }]
  pageChange: [event: AppPaginationEvent]
  'update:selection': any
}>()

const router = useRouter()
const itemsRef = toRef(props, 'items')
const selectedItem = ref<T | null>(null)
const detailModal = ref(false)

const sectionBind = useSectionBind(props)

const repoData = useRepoData<T>({
  ...props,
  items: itemsRef,
  autoLoad: props.autoLoad,
  storeInRepo: props.storeInRepo,
})

const detailModalActionsProps = computed(() => ({
  hideHeaderActions: true,
  ...props.detailModalProps?.actionsProps,
}))

const page = computed({
  get: () => props.repo?.pagination.page ?? 1,
  set: (value: number) => {
    if (props.repo) {
      props.repo.pagination.page = value
    }
  },
})

const hasNextPage = computed(() => {
  if (!props.repo) return false
  return props.repo.pagination.has_next
})

const listBind = computed(
  () =>
    ({
      mode: props.mode,
      contentClass: props.contentClass,
      selection: props.selection,
      scrollable: props.scrollable,
      scrollHeight: props.scrollHeight,
      emptyText: props.emptyText,
      infiniteScroll: props.infiniteScroll,
      showPagination: props.showPagination,
      handleItemClick: props.handleItemClick,
      itemKey: 'id' as keyof T,
      items: repoData.items.value,
      loading: props.repo?.loading.list,
      pagination: props.repo?.pagination,
      paginationLoading: props.repo?.loading.list,
      searchLoading: repoData.loadItemsState.loading.value,
      hasNextPage: hasNextPage.value,
      showSearch: props.showSearch,
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
  if (event.item) {
    selectedItem.value = event.item
    updateListItem(cloneDeep(event.item))
  }

  if (props.detailModalProps?.closeOnSave !== false) {
    detailModal.value = false
  }

  if (props.reloadAfterSave) {
    void repoData.loadItems()
  }
}

const handleDetailAction = (event: AppDetailActionsDeleteResult<T>) => {
  if (event.item) {
    deleteListItem(event.item)
  }
  detailModal.value = false
}

const _openItem = (item: T | null) => {
  if (props.detailMode === 'modal') {
    if (item) selectedItem.value = cloneDeep(item)
    else selectedItem.value = props.buildNewItem?.() || props.repo?.decode({})
    detailModal.value = true
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

const handleLoadMore = () => {
  if (!props.repo) return

  handlePageChange({
    append: true,
    pagination: { ...props.repo.pagination, page: props.repo.pagination.page + 1 },
  })
}

defineExpose({
  openItem,
  reload: () => repoData.loadItems(),
  getItems: () => repoData.items.value,
})
</script>
