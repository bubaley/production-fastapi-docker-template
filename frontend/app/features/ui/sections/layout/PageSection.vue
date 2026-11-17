<script setup lang="ts">
import { Archive, Check, CircleDot, Ellipsis, Pencil, Search, Share2, Users } from '@lucide/vue'
import { ref } from 'vue'
import type { AppMenuAction } from '~/shared/ui/app/AppMenu.vue'
import UiDemo from '../../components/UiDemo.vue'

const toast = useToast()
const stickySearch = ref('')
const pageMenu: AppMenuAction[] = [
  { label: 'Rename', icon: Pencil, action: () => void toast.default('Rename requested') },
  { label: 'Archive', icon: Archive, action: () => void toast.default('Project archived') },
]
</script>

<template>
  <UiDemo
    title="Page view"
    code="AppPageView title description #actions #footer"
    description="Header actions in one row with the title: primary first, then secondary, ⋯ last (44px touch targets on phones). The body scrolls; the footer stays."
    bare
  >
    <AppCard
      padding="none"
      class="h-80 overflow-hidden"
    >
      <AppPageView
        title="Project overview"
        description="Nested page layout example"
      >
        <template #actions>
          <AppButton
            label="New task"
            @click="toast.default('Task created')"
          />
          <AppButton
            variant="outline"
            label="Share"
            :icon="Share2"
            @click="toast.default('Link copied')"
          />
          <AppMenu
            :actions="pageMenu"
            label="Project"
          >
            <template #trigger>
              <AppButton
                variant="ghost"
                :icon="Ellipsis"
                aria-label="More actions"
              />
            </template>
          </AppMenu>
        </template>
        <AppSection title="Key metrics">
          <div class="grid gap-4 sm:grid-cols-3">
            <AppDataLabel
              label="Status"
              value="In progress"
              :icon="CircleDot"
            /><AppDataLabel
              label="Members"
              value="8 members"
              :icon="Users"
            /><AppDataLabel
              label="Completed"
              value="24 issues"
              :icon="Check"
            />
          </div>
        </AppSection>
        <template #footer><div class="text-xs text-muted-foreground">Changes are saved automatically</div></template>
      </AppPageView>
    </AppCard>
  </UiDemo>
  <UiDemo
    title="Sticky regions"
    code='sticky="none | controls | header"'
    description="By default the whole header scrolls away with the content. controls keeps only the filter row pinned (it gets a background and a hairline once content runs under it); header pins the whole header. Scroll inside the frame."
    bare
  >
    <AppCard
      padding="none"
      class="h-80 overflow-hidden"
    >
      <AppPageView
        title="Orders"
        description='sticky="controls"'
        sticky="controls"
      >
        <template #controls>
          <AppInput
            v-model="stickySearch"
            :icon="Search"
            placeholder="Search"
            class="max-w-xs"
          />
        </template>
        <div class="flex flex-col gap-3">
          <AppCard
            v-for="row in 12"
            :key="row"
            class="text-sm"
          >
            Order #{{ 1000 + row }}
          </AppCard>
        </div>
      </AppPageView>
    </AppCard>
  </UiDemo>
  <UiDemo
    title="Section"
    code='AppSection title description #actions title-size="lg"'
    description="Structure without a surface: a heading, a description and actions over its content. Wrap it in AppCard only when the block needs a visible frame."
  >
    <AppSection
      title="Notifications"
      description="Which events reach your inbox."
    >
      <template #actions>
        <AppButton
          size="sm"
          variant="outline"
          label="Edit"
        />
      </template>
      <p class="text-sm">Section content.</p>
    </AppSection>
  </UiDemo>
</template>
