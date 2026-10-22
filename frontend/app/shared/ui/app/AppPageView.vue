<script setup lang="ts">
import PageHeader from '../template/PageHeader.vue'
import type { AppSectionProps } from './AppSection.vue'

export type AppPageViewProps = AppSectionProps & { contentClass?: string }
withDefaults(defineProps<AppPageViewProps>(), { contentClass: 'p-3 md:p-4' })
</script>
<template>
  <AppPage :content-class="contentClass">
    <template
      v-if="
        title ||
        description ||
        $slots.header ||
        $slots.title ||
        $slots.prefix ||
        $slots['title-append'] ||
        $slots.actions ||
        backAction
      "
      #header
    >
      <slot name="header">
        <PageHeader
          :title="title"
          :title-size="titleSize"
          :description="description"
          :back-action="backAction"
        >
          <template
            v-if="$slots.title"
            #title
          >
            <slot name="title" />
          </template>
          <template
            v-if="$slots.prefix"
            #prefix
          >
            <slot name="prefix" />
          </template>
          <template
            v-if="$slots['title-append']"
            #title-append
          >
            <slot name="title-append" />
          </template>
          <template
            v-if="$slots.actions"
            #actions
          >
            <slot name="actions" />
          </template>
        </PageHeader>
      </slot>
    </template>
    <template
      v-if="$slots.subheader || $slots.subtitle"
      #subheader
    >
      <slot name="subheader"><slot name="subtitle" /></slot>
    </template>
    <template
      v-if="$slots.controls"
      #controls
    >
      <slot name="controls" />
    </template>
    <slot />
    <template
      v-if="$slots.footer"
      #footer
    >
      <slot name="footer" />
    </template>
  </AppPage>
</template>
