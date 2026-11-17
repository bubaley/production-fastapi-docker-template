<template>
  <component
    :is="templateVariant === 'page' ? AppPageView : AppSection"
    v-bind="rootBind"
  >
    <template
      v-if="currentItem && showHeaderActions"
      #actions
    >
      <AppDetailActions
        v-if="!actionsProps?.hidden"
        :resource="resource"
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

    <AppLoadingIndicator
      v-if="loading && !currentItem"
      label="Загрузка записи…"
    />
    <div
      v-else-if="error && !currentItem"
      role="alert"
      class="flex flex-col items-start gap-3"
    >
      <p>Не удалось загрузить запись. Проверьте доступ и попробуйте ещё раз.</p>
      <AppButton
        variant="outline"
        @click="loadItem"
      >
        Повторить
      </AppButton>
    </div>
    <!-- Fields sit 14px apart; a nested section (a member list, tokens) gets extra room above its heading. -->
    <div
      v-if="currentItem"
      class="flex flex-col gap-4 [&>section]:mt-4"
    >
      <slot v-bind="{ item: currentItem, isCreating: !currentItem.id, loading }" />
      <!-- In a modal the actions follow the dialog footer layout; elsewhere they stretch under the form. -->
      <component
        :is="inModal ? AppModalFooter : 'div'"
        v-if="showFooterActions && !actionsProps?.hidden"
      >
        <AppDetailActions
          :resource="resource"
          v-bind="actionsProps"
          full-width
          :item="currentItem"
          @cancel="emit('cancel')"
          @delete="handleDelete"
          @save="handleSave"
        />
      </component>
    </div>
  </component>
</template>

<script setup generic="T extends ResourceItem, F extends ResourceForm" lang="ts">
import type { ResourceForm, ResourceItem } from '~/shared/api/resource'
import { inject } from 'vue'
import AppModalFooter from '../app/AppModalFooter.vue'
import { IN_MODAL } from '../app/modalFooter'
import AppPageView from '../app/AppPageView.vue'
import AppSection from '../app/AppSection.vue'
import type { AppDetailTemplateProps } from './types/template-types'

export type { AppDetailTemplateActionsProps, AppDetailTemplateProps } from './types/template-types'

const emit = defineEmits<{
  save: [event: AppDetailActionsSaveResult<F, T>]
  delete: [event: AppDetailActionsDeleteResult<F>]
  cancel: []
}>()

const props = withDefaults(defineProps<AppDetailTemplateProps<T, F>>(), {
  detailRouteParam: 'id',
  mode: 'page',
  templateVariant: 'page',
  maxWidth: 'md',
  align: 'start',
})

const router = useRouter()
const inModal = inject(IN_MODAL, false)

const sectionBind = useSectionBind(props, {
  resolveBackAction: () => {
    if (props.backAction) return props.backAction
    if (props.mode === 'page') return () => router.back()
    return undefined
  },
})

// A form reads best in a column: the page is `md` wide next to the navigation unless `fluid` asks for the full width.
const rootBind = computed(() => ({ ...sectionBind.value, ...(props.fluid && { maxWidth: undefined }) }))

const {
  item: detailItem,
  loading,
  error,
  loadItem,
  setItem,
} = useTemplateDetail(() => props.resource, props.detailRouteParam, props.buildNewItem, props.mode === 'page')

const currentItem = computed(() => props.item ?? detailItem.value)

const showHeaderActions = computed(() => {
  if (props.hideHeader) return false
  return props.mode === 'page' && !props.actionsProps?.hideHeaderActions
})

const showFooterActions = computed(() => {
  return props.mode === 'inline' || !!props.actionsProps?.hideHeaderActions
})

const handleSave = (event: AppDetailActionsSaveResult<F, T>) => {
  if (event.item && !props.item) setItem(event.item)
  emit('save', event)
}

const handleDelete = (event: AppDetailActionsDeleteResult<F>) => {
  if (props.listRouteName) {
    void router.replace({ name: props.listRouteName })
  }
  emit('delete', event)
}
</script>
