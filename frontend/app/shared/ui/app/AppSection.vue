<template>
  <AppBlock
    v-bind="$attrs"
    :variant="resolvedFlat ? 'text' : 'outlined'"
    :radius="resolvedFlat ? 'unset' : 'lg'"
    :class="[props.class, { 'app-section': !resolvedFlat }]"
    :display="display"
    style="position: relative"
    class="gap-md"
  >
    <div
      v-if="!hideData.hideTitleBlock || !hideData.hideDescription"
      class="flex flex-col"
    >
      <div
        v-if="!hideData.hideTitleBlock"
        class="flex items-center w-full"
      >
        <AppBackButton
          v-if="backAction"
          :back-action="backAction"
          class="mr-2"
        />
        <div class="flex items-center gap-sm flex-1 min-w-0">
          <AppTitle
            v-if="title"
            :size="resolvedTitleSize"
            :title="title"
            class="mr-1"
          />
          <div class="flex items-center gap-sm flex-1 min-w-0">
            <slot name="actions" />
          </div>
        </div>
      </div>
      <div
        v-if="!hideData.hideDescription"
        :class="backAction ? 'ml-12' : ''"
      >
        <div
          v-if="description"
          class="fg-secondary"
        >
          {{ description }}
        </div>
        <slot name="subtitle" />
      </div>
    </div>

    <slot />
  </AppBlock>
</template>

<script setup lang="ts">
defineOptions({
  inheritAttrs: false,
})

export type AppSectionProps = {
  title?: string
  description?: string
  titleSize?: TitleSizeToken
  flat?: boolean
  templateVariant?: TemplateVariant
  backAction?: () => void
  display?: 'row' | 'column' | 'inline-row'
  class?: string
}

const props = withDefaults(defineProps<AppSectionProps>(), {
  display: 'column',
})

const slots = useSlots()

const hideData = computed(() => {
  const hideTitleBlock = !props.title && !slots.title?.()
  const hideDescription = !props.description && !slots.subtitle?.()
  return {
    hideTitleBlock,
    hideDescription,
  }
})

const resolvedFlat = computed(() => (props.flat !== undefined ? props.flat : props.templateVariant !== 'section'))

const resolvedTitleSize = computed((): TitleSizeToken => {
  if (props.titleSize) return props.titleSize
  if (props.templateVariant === 'page') return 'xl'
  if (props.templateVariant === 'flat-section') return 'md'
  return 'xl'
})
</script>
