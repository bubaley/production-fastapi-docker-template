<template>
  <aside class="sticky top-0 flex h-full min-h-0 max-h-full flex-col self-start overflow-hidden">
    <nav
      class="bg-secondary radius-md flex min-h-0 flex-1 flex-col overflow-y-auto border-base border px-2 py-4 dark:border-none"
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
            <AppButton
              :to="item.to"
              :icon="item.icon"
              :severity="isActiveRoute(item.to) ? 'primary' : 'secondary'"
              :text="!isActiveRoute(item.to)"
            />
          </div>
        </div>
      </div>
      <slot name="after" />
    </nav>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

export type NavigationSection = {
  title: string
  icon?: string
  items: {
    to: Record<string, string>
    label: string
    icon?: string
  }[]
}

defineProps<{
  sections?: NavigationSection[]
}>()

const isActiveRoute = computed(() => (to: Record<string, string>) => {
  return !!route.matched.find((v) => v.name?.toString().includes(to.name || ''))
})
</script>
