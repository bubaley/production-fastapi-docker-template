<script setup lang="ts">
import { defineAsyncComponent, type Component } from 'vue'
import { findUiSection, uiSections } from '../catalog'

const props = defineProps<{ sectionKey: string }>()

// One async component per section, created once, so revisiting a section does not reload its chunk.
const sectionComponents = new Map<string, Component>(
  uiSections.map((section) => [section.key, defineAsyncComponent(section.load)]),
)
const entry = computed(() => findUiSection(props.sectionKey))
const sectionComponent = computed<Component | undefined>(() => sectionComponents.get(props.sectionKey))

useHead({ title: () => `${entry.value?.section.title ?? 'UI'} · UI catalogue` })
</script>

<template>
  <AppPageView
    v-if="entry"
    :title="entry.section.title"
    :description="entry.section.description"
    max-width="lg"
    align="start"
  >
    <template #subheader>
      <div class="flex flex-wrap items-center gap-1.5 pb-3">
        <span class="mr-1 text-xs text-muted-foreground">{{ entry.group.title }}</span>
        <code
          v-for="name in entry.section.components"
          :key="name"
          class="rounded-sm bg-muted px-1.5 py-0.5 font-mono text-xs text-muted-foreground"
          >{{ name }}</code
        >
      </div>
    </template>
    <div class="flex flex-col gap-10 pb-8">
      <component
        :is="sectionComponent"
        :key="sectionKey"
      />
    </div>
  </AppPageView>
</template>
