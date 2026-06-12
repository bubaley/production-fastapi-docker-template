<template>
  <AppSection v-bind="sectionBind">
    <template
      v-if="currentItem && showHeaderActions"
      #actions
    >
      <AppDetailActions
        v-if="!actionsProps?.hidden"
        :repo="repo"
        v-bind="actionsProps"
        :item="currentItem"
        @cancel="emit('cancel')"
        @delete="handleDelete"
        @save="handleSave"
      />
      <slot
        name="actions"
        v-bind="{ item: currentItem, isCreating: !currentItem.id, loading }"
      />
    </template>

    <div
      v-if="currentItem"
      class="flex flex-col gap-4"
      :class="{ 'c-detail-template': !fluid }"
    >
      <slot v-bind="{ item: currentItem, isCreating: !currentItem.id, loading }" />
      <AppDetailActions
        v-if="showFooterActions && !actionsProps?.hidden"
        class="c-detail-actions"
        :repo="repo"
        v-bind="actionsProps"
        full-width
        :item="currentItem"
        @cancel="emit('cancel')"
        @delete="handleDelete"
        @save="handleSave"
      />
    </div>
  </AppSection>
</template>

<script setup generic="T extends AppModel" lang="ts">
import type { AppDetailTemplateProps } from './types/template-types'

export type { AppDetailTemplateActionsProps, AppDetailTemplateProps } from './types/template-types'

const emit = defineEmits<{
  save: [event: AppDetailActionsSaveResult<T>]
  delete: [event: AppDetailActionsDeleteResult<T>]
  cancel: []
}>()

const props = withDefaults(defineProps<AppDetailTemplateProps<T>>(), {
  detailRouteParam: 'id',
  mode: 'page',
  templateVariant: 'page',
})

const router = useRouter()

const sectionBind = useSectionBind(props, {
  resolveBackAction: () => {
    if (props.backAction) return props.backAction
    if (props.mode === 'page') return () => router.back()
    return undefined
  },
})

const { item: detailItem, loading } = useTemplateDetail(
  props.repo,
  props.detailRouteParam,
  props.buildNewItem,
  props.mode === 'page',
)

const currentItem = computed(() => props.item ?? detailItem.value)

const showHeaderActions = computed(() => {
  if (props.hideHeader) return false
  return props.mode === 'page' && !props.actionsProps?.hideHeaderActions
})

const showFooterActions = computed(() => {
  return props.mode === 'inline' || !!props.actionsProps?.hideHeaderActions
})

const handleSave = (event: AppDetailActionsSaveResult<T>) => {
  emit('save', event)
}

const handleDelete = (event: AppDetailActionsDeleteResult<T>) => {
  if (props.listRouteName) {
    void router.replace({ name: props.listRouteName })
  }
  emit('delete', event)
}
</script>
