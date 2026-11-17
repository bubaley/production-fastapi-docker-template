<script setup lang="ts">
import { computed, ref, useSlots, useTemplateRef } from 'vue'
import { createReusableTemplate } from '@vueuse/core'
import {
  PAGE_CONTENT_AFTER_CONTROLS_CLASS,
  PAGE_CONTENT_CLASS,
  PAGE_CONTROLS_CLASS,
  PAGE_DIVIDER_CLASS,
  PAGE_FOOTER_CLASS,
  PAGE_GUTTER_CLASS,
  PAGE_HEADER_CLASS,
  PAGE_PINNED_CLASS,
  PAGE_SUBHEADER_CLASS,
  PAGE_TITLE_CLASS,
  pageColumnClass,
  type PageAlign,
  type PageMaxWidth,
  type PageSticky,
} from './pageContainer'

export type AppPageShellProps = {
  /** A line between the header group (header, subheader) and the controls and body. Off by default. */
  divided?: boolean
  /** Limits the header, controls, body and footer to one column (`--page-width-*`). Full width by default. */
  maxWidth?: PageMaxWidth
  /** With `maxWidth`: center the column (default) or keep it at the start, next to the navigation. */
  align?: PageAlign
  /** What stays on screen while the body scrolls: `none` (default), the `controls` bar or the whole `header` area. */
  sticky?: PageSticky
}
export type AppPageProps = AppPageShellProps & {
  title?: string
  /** Replaces the default body padding (`PAGE_CONTENT_CLASS`, or `PAGE_CONTENT_AFTER_CONTROLS_CLASS` under controls). */
  contentClass?: string
}

const props = withDefaults(defineProps<AppPageProps>(), {
  title: '',
  contentClass: undefined,
  maxWidth: undefined,
  align: 'center',
  sticky: 'none',
})
const slots = useSlots()

const column = computed<string | undefined>(() => pageColumnClass(props.maxWidth, props.align))
const hasHeader = computed<boolean>(() => Boolean(props.title || slots.header))
const hasHeaderGroup = computed<boolean>(() => Boolean(hasHeader.value || slots.subheader))
const bodyClass = computed<string>(
  () => props.contentClass ?? (slots.controls ? PAGE_CONTENT_AFTER_CONTROLS_CLASS : PAGE_CONTENT_CLASS),
)

// The header group is rendered above the body (`sticky="header"`) or inside it (it scrolls away); one template for both.
const [DefineHeaderGroup, HeaderGroup] = createReusableTemplate()

// A pinned region shows its bottom hairline only once content scrolls under it.
const body = useTemplateRef<HTMLElement>('body')
const controlsMark = useTemplateRef<HTMLElement>('controlsMark')
const stuck = ref<boolean>(false)
const onScroll = (): void => {
  const top = body.value?.scrollTop ?? 0
  if (props.sticky === 'header') stuck.value = top > 0
  else if (props.sticky === 'controls') stuck.value = top > 0 && top >= (controlsMark.value?.offsetTop ?? 0)
  else stuck.value = false
}
</script>

<template>
  <section class="flex h-full min-h-0 w-full min-w-0 flex-col overflow-hidden">
    <DefineHeaderGroup>
      <div
        v-if="hasHeaderGroup"
        data-slot="page-header"
        :class="[PAGE_GUTTER_CLASS, divided && PAGE_DIVIDER_CLASS]"
      >
        <div
          v-if="hasHeader"
          :class="[PAGE_HEADER_CLASS, column, title && 'flex items-start gap-3']"
        >
          <h1
            v-if="title"
            class="m-0 min-w-0 flex-1"
            :class="PAGE_TITLE_CLASS"
          >
            {{ title }}
          </h1>
          <slot name="header" />
        </div>
        <div
          v-if="$slots.subheader"
          :class="[hasHeader ? PAGE_SUBHEADER_CLASS : PAGE_HEADER_CLASS, column]"
        >
          <slot name="subheader" />
        </div>
      </div>
    </DefineHeaderGroup>
    <!-- Header, subheader, controls, body and footer share one gutter and one column (pageContainer.ts). -->
    <div
      v-if="sticky === 'header' && (hasHeaderGroup || $slots.controls)"
      class="shrink-0"
      :class="PAGE_PINNED_CLASS"
      :data-stuck="stuck || undefined"
    >
      <HeaderGroup />
      <div
        v-if="$slots.controls"
        data-slot="page-controls"
        :class="[PAGE_GUTTER_CLASS, PAGE_CONTROLS_CLASS]"
      >
        <div :class="column">
          <slot name="controls" />
        </div>
      </div>
    </div>
    <!-- The layout owns the page's single <main>; this is the scrolling body. A flex column (not h-full) keeps the
         bottom padding below long content. -->
    <div
      ref="body"
      data-slot="page-body"
      class="relative min-h-0 flex-1 overflow-auto"
      @scroll.passive="onScroll"
    >
      <div class="flex min-h-full flex-col">
        <template v-if="sticky !== 'header'">
          <HeaderGroup />
          <template v-if="$slots.controls">
            <!-- Where the controls bar starts: once the body scrolls past it, a sticky bar is stuck. -->
            <div
              ref="controlsMark"
              aria-hidden="true"
            />
            <div
              data-slot="page-controls"
              :class="[
                PAGE_GUTTER_CLASS,
                PAGE_CONTROLS_CLASS,
                sticky === 'controls' && ['sticky top-0 z-10', PAGE_PINNED_CLASS],
              ]"
              :data-stuck="(sticky === 'controls' && stuck) || undefined"
            >
              <div :class="column">
                <slot name="controls" />
              </div>
            </div>
          </template>
        </template>
        <div
          class="flex flex-1 flex-col"
          :class="bodyClass"
        >
          <div
            class="flex-1"
            :class="column"
          >
            <slot />
          </div>
        </div>
      </div>
    </div>
    <footer
      v-if="$slots.footer"
      class="shrink-0"
      :class="[PAGE_GUTTER_CLASS, PAGE_FOOTER_CLASS]"
    >
      <div :class="column">
        <slot name="footer" />
      </div>
    </footer>
  </section>
</template>
