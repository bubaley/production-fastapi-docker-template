<script setup lang="ts">
import { Check, CircleCheck, CircleDot, Copy, TriangleAlert } from '@lucide/vue'
import type { AppLabelConfig } from '~/shared/ui/app/types/label-types'
import { TONES } from '~/shared/ui/app/tone'
import UiDemo from '../../components/UiDemo.vue'

const labels: AppLabelConfig[] = [
  { label: 'In progress', icon: CircleDot, tone: 'primary' },
  { label: 'Success', icon: Check, tone: 'success' },
  { label: 'Warning', icon: TriangleAlert, tone: 'warning' },
  { label: 'Info', icon: CircleDot, tone: 'info' },
  { label: 'Danger', icon: TriangleAlert, tone: 'destructive' },
]
const labelVariants = ['default', 'soft', 'outline'] as const
const badgeVariants = ['solid', 'soft', 'outline'] as const
</script>

<template>
  <UiDemo
    title="Status labels"
    code=':config="{ label, icon, tone }" variant="default | soft | outline"'
    description="Statuses of entities. Keep the configs in one map per feature; icon-only needs a tooltip."
  >
    <div class="flex flex-col gap-5">
      <div
        v-for="variant in labelVariants"
        :key="variant"
        class="flex flex-wrap items-center gap-4"
      >
        <span class="w-16 text-xs text-muted-foreground">{{ variant }}</span>
        <AppLabel
          v-for="item in labels"
          :key="item.label"
          :config="item"
          :variant="variant"
        />
        <AppDataLabel
          :config="labels[1]"
          :variant="variant"
          icon-only
        />
      </div>
    </div>
  </UiDemo>
  <UiDemo
    title="Values"
    code='AppDataLabel label value copied size="xl" · AppEmptyData'
    description="A caption over a value for cards and details. A missing value is a muted dash (AppEmptyData), not an empty state."
  >
    <div class="grid gap-4 sm:grid-cols-4">
      <AppDataLabel
        label="Project code"
        value="PRJ-001"
        :icon="Copy"
        copied
      />
      <AppDataLabel
        label="Active issues"
        :value="24"
        size="xl"
        tone="primary"
        :icon="CircleDot"
      />
      <AppDataLabel label="Owner">
        <template #label-tooltip>The person responsible for the project.</template>
      </AppDataLabel>
      <div class="flex flex-col gap-1 text-sm">
        <span class="text-xs text-muted-foreground">Due date</span>
        <AppEmptyData label="Not set" />
      </div>
    </div>
  </UiDemo>
  <UiDemo
    title="Badges"
    code='tone="…" variant="solid | soft | outline"'
    description="Counters and short tags. Use a status label for entity states."
  >
    <div class="flex flex-col gap-3">
      <div
        v-for="variant in badgeVariants"
        :key="variant"
        class="flex flex-wrap items-center gap-2"
      >
        <span class="w-16 text-xs text-muted-foreground">{{ variant }}</span>
        <AppBadge
          v-for="tone in TONES"
          :key="tone"
          :tone="tone"
          :variant="variant"
          :label="tone"
        />
      </div>
      <div class="flex flex-wrap items-center gap-2 border-t border-border pt-3">
        <span class="w-16 text-xs text-muted-foreground">icon</span>
        <AppBadge
          tone="success"
          :icon="CircleCheck"
          label="With icon"
        />
      </div>
    </div>
  </UiDemo>
</template>
