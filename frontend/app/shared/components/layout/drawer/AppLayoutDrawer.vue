<template>
  <aside class="sticky top-0 flex h-full max-h-full min-h-0 flex-col self-start overflow-hidden">
    <nav
      aria-label="Основная навигация"
      class="flex min-h-0 flex-1 flex-col overflow-y-auto rounded-md border border-border bg-card px-2 py-4 dark:border-none"
    >
      <div
        v-for="section in sections"
        :key="section.title"
        class="space-y-2"
      >
        <div class="space-y-2">
          <div
            v-for="(item, index) in section.items"
            :key="index"
          >
            <AppTooltip
              :text="item.label"
              side="right"
            >
              <template #trigger>
                <AppButton
                  :to="item.to"
                  :aria-label="item.label"
                  :aria-current="isActiveRoute(item.to) ? 'page' : undefined"
                  :icon="item.icon"
                  :variant="isActiveRoute(item.to) ? 'default' : 'ghost'"
                />
              </template>
            </AppTooltip>
          </div>
        </div>
      </div>
      <slot name="after" />
    </nav>
  </aside>
</template>

<script setup lang="ts">
import { computed, type Component } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

export type NavigationSection = {
  title: string
  items: {
    to: Record<string, string>
    label: string
    icon: Component
  }[]
}

defineProps<{
  sections?: NavigationSection[]
}>()

const isActiveRoute = computed(() => (to: Record<string, string>) => {
  return !!route.matched.find((v) => v.name?.toString().includes(to.name || ''))
})
</script>
