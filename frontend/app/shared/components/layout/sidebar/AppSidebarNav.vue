<template>
  <nav
    :aria-label="label"
    class="flex flex-col gap-4"
  >
    <div
      v-for="(section, sectionIndex) in sections"
      :key="section.collapsibleId || section.title || sectionIndex"
      class="flex flex-col gap-px"
    >
      <div
        v-if="section.title"
        class="flex h-[44px] items-center gap-1 pr-1 pl-2 md:h-8"
      >
        <button
          v-if="section.collapsibleId"
          type="button"
          class="flex min-w-0 flex-1 items-center gap-1 rounded-sm text-left text-xs font-medium text-muted-foreground outline-none hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring"
          :aria-expanded="!isFolded(section)"
          @click="toggleFold(section)"
        >
          <span class="truncate">{{ section.title }}</span>
          <AppIcon
            :icon="ChevronRight"
            size="xs"
            class="transition-transform"
            :class="!isFolded(section) && 'rotate-90'"
          />
        </button>
        <span
          v-else
          class="min-w-0 flex-1 truncate text-xs font-medium text-muted-foreground"
          >{{ section.title }}</span
        >
        <AppButton
          v-if="section.action"
          variant="ghost"
          size="icon-xs"
          text-variant="muted"
          class="size-[44px] md:size-control-xs"
          :icon="section.action.icon"
          :aria-label="section.action.label"
          :title="section.action.label"
          @click="section.action.onClick"
        />
      </div>
      <template v-if="!isFolded(section)">
        <AppSidebarLink
          v-for="(item, index) in section.items"
          :key="index"
          :item="item"
          :active="activeKey === `${sectionIndex}:${index}`"
        />
      </template>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ChevronRight } from '@lucide/vue'
import { useRoute, useRouter } from 'vue-router'
import AppSidebarLink from './AppSidebarLink.vue'
import type { SidebarSection } from './types'

const props = withDefaults(defineProps<{ sections: SidebarSection[]; label?: string }>(), {
  label: 'Основная навигация',
})

const route = useRoute()
const router = useRouter()

const sameRoute = (name: string, current: string): boolean => current === name || current.startsWith(`${name}-`)

// Exactly one active item: the route name matches the item's route or is nested under it (`settings-users-id` under
// `settings-users`), and the item's own params and query match the current ones. The item with the most matching
// query keys wins, so `?archived=1` beats the plain list on the same route; a longer route name breaks ties.
const activeKey = computed<string | null>(() => {
  const current = route.name?.toString() ?? ''
  let best: { key: string; score: number } | null = null
  props.sections.forEach((section, sectionIndex) =>
    section.items.forEach((item, index) => {
      if (!item.to) return
      const target = router.resolve(item.to)
      const name = target.name?.toString()
      if (!name || !sameRoute(name, current)) return
      const params = Object.entries(target.params)
      if (params.some(([key, value]) => String(route.params[key] ?? '') !== String(value))) return
      const keys = Object.keys(target.query)
      if (keys.some((key) => String(route.query[key] ?? '') !== String(target.query[key] ?? ''))) return
      const extra = Object.keys(route.query).filter((key) => !keys.includes(key)).length
      const score = keys.length * 10 - extra + name.length / 1000
      if (!best || score > best.score) best = { key: `${sectionIndex}:${index}`, score }
    }),
  )
  return (best as { key: string } | null)?.key ?? null
})

// Folded sections are remembered per browser.
const folded = useCookie<string[]>('sidebar-folded', {
  default: () => [],
  maxAge: 60 * 60 * 24 * 365,
  sameSite: 'lax',
})
const isFolded = (section: SidebarSection): boolean =>
  Boolean(section.collapsibleId && folded.value.includes(section.collapsibleId))
const toggleFold = (section: SidebarSection): void => {
  const id = section.collapsibleId
  if (!id) return
  folded.value = folded.value.includes(id) ? folded.value.filter((value) => value !== id) : [...folded.value, id]
}
</script>
