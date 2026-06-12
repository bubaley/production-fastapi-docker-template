<template>
  <AppBlock
    v-bind="$attrs"
    :variant="resolvedFlat ? 'text' : 'outlined'"
    :radius="resolvedFlat ? 'unset' : 'lg'"
    :class="{ 'app-section': !resolvedFlat }"
    :display="display"
    style="position: relative"
    class="gap-md"
  >
    <div
      v-if="$slots.actions || title"
      class="flex items-center gap-sm"
    >
      <AppBackButton
        v-if="backAction"
        :back-action="backAction"
      />
      <div>
        <div class="flex items-center gap-sm">
          <AppTitle
            v-if="title"
            :size="resolvedTitleSize"
            :title="title"
            class="mr-1"
          />
          <slot name="actions" />
        </div>
        <div
          v-if="description"
          class="fg-secondary"
        >
          {{ description }}
        </div>
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
}

const props = withDefaults(defineProps<AppSectionProps>(), {
  display: 'column',
})

const resolvedFlat = computed(() => (props.flat !== undefined ? props.flat : props.templateVariant !== 'section'))

const resolvedTitleSize = computed((): TitleSizeToken => {
  if (props.titleSize) return props.titleSize
  if (props.templateVariant === 'page') return 'xl'
  if (props.templateVariant === 'flat-section') return 'md'
  return 'xl'
})
</script>
