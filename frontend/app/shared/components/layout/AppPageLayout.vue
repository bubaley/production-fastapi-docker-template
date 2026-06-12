<template>
  <div class="flex min-h-0 w-full flex-1 flex-col pb-1 px-1">
    <div
      class="page-view h-full w-full"
      :class="{
        'page-view-nested': hasParentPageView,
        'page-view-with-header': hasHeader,
        'page-view-with-footer': hasFooter,
        'border-base border radius-md': bordered,
      }"
    >
      <div :class="{ 'p-4': !noPadding }">
        <div
          v-if="hasHeader"
          class="page-view-header column gap-4"
        >
          <div
            v-if="$slots.title || title || $slots.actions"
            class="row gap-4 items-center"
          >
            <slot name="title" />
            <div
              v-if="title"
              class="header3 bold content-1"
            >
              {{ title }}
            </div>
            <slot name="actions" />
          </div>
          <div
            v-if="$slots.subactions"
            class="row"
          >
            <slot name="subactions" />
          </div>
          <!-- <q-separator v-if="$slots['nested-actions']" /> -->
          <div
            v-if="$slots['nested-actions']"
            class="row"
          >
            <slot name="nested-actions" />
          </div>
        </div>
        <div
          class="page-view-content"
          :class="contentClass"
        >
          <slot />
        </div>
        <div
          v-if="hasFooter"
          class="page-view-footer bg-black"
        >
          <!-- <q-separator /> -->
          <div class="row">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, inject, onMounted, onUnmounted, provide, useSlots } from 'vue'

const PAGE_VIEW_KEY = Symbol('PageView')

const props = withDefaults(
  defineProps<{
    title?: string
    bordered?: boolean
    contentClass?: string
    noPadding?: boolean
  }>(),
  {
    // contentClass: 'px-5 pb-5',
  },
)

const slots = useSlots()
const hasHeader = computed(
  () => !!props.title || !!slots.actions || !!slots.subactions || !!slots.title || !!slots['nested-actions'],
)
const hasFooter = computed(() => !!slots.footer)

const hasParentPageView = inject(PAGE_VIEW_KEY, false)
provide(PAGE_VIEW_KEY, true)

onMounted(() => {
  if (!hasParentPageView) {
    document.body.style.overflow = 'hidden'
  }
})

onUnmounted(() => {
  if (!hasParentPageView) {
    document.body.style.overflow = ''
  }
})
</script>

<style scoped lang="scss">
.page-view {
  display: flex;
  flex-direction: column;
  width: 100%;
  position: relative;

  &.page-view-nested {
    height: 100%;
    max-height: 100%;
  }

  &:not(.page-view-with-header):not(.page-view-with-footer) {
    overflow-y: auto;
    overflow-x: hidden;
    -webkit-overflow-scrolling: touch;
  }

  &.page-view-with-header,
  &.page-view-with-footer {
    overflow: hidden;
  }
}

.page-view-header {
  flex-shrink: 0;
  z-index: 1;
}

.page-view-content {
  flex: 1;
  min-height: 0;

  .page-view-with-header &,
  .page-view-with-footer & {
    overflow-y: auto;
    overflow-x: hidden;
    -webkit-overflow-scrolling: touch;
  }
}

.page-view-footer {
  flex-shrink: 0;
  z-index: 1;
}
</style>

<style lang="scss">
.q-page-container {
  overflow: hidden !important;
}
</style>
