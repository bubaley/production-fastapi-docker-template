<script setup lang="ts">
import { CircleDot, Check, TriangleAlert } from '@lucide/vue'
import type { AppLabelConfig } from '~/shared/ui/app/types/label-types'
const labels: AppLabelConfig[] = [{ label: 'In progress', icon: CircleDot, tone: 'primary' }, { label: 'Success', icon: Check, tone: 'positive' }, { label: 'Warning', icon: TriangleAlert, tone: 'warning' }]
labels.push({ label: 'Info', icon: CircleDot, tone: 'info' }, { label: 'Danger', icon: TriangleAlert, tone: 'destructive' })
const labelVariants = ['default', 'soft', 'outline'] as const
const cards = [
  { title: 'Neutral', color: 'neutral', variant: 'outlined' },
  { title: 'Primary', color: 'primary', variant: 'outlined' },
  { title: 'Success', color: 'success', variant: 'outlined' },
  { title: 'Info', color: 'info', variant: 'outlined' },
  { title: 'Warning', color: 'warning', variant: 'outlined' },
  { title: 'Danger', color: 'danger', variant: 'outlined' },
  { title: 'Elevated', color: 'neutral', variant: 'elevated' },
  { title: 'Muted', color: 'neutral', variant: 'muted' },
  { title: 'Default', color: 'neutral', variant: 'default' },
] as const
</script>
<template>
  <div class="space-y-10">
    <AppSection
      title="Typography"
      description="AppTitle: semantic heading tags and Tailwind font sizes."
    >
      <AppCard class="space-y-4">
        <AppTitle
          v-for="sample in [{ size: 'xl', as: 'h1', text: 'xl · text-3xl · h1' }, { size: 'lg', as: 'h2', text: 'lg · text-xl · h2' }, { size: 'md', as: 'h3', text: 'md · text-base · h3' }, { size: 'sm', as: 'h4', text: 'sm · text-sm · h4' }] as const"
          :key="sample.size"
          :size="sample.size"
          :as="sample.as"
          :title="sample.text"
        />
      </AppCard>
    </AppSection>
    <AppSection
      title="Labels and values"
      description="Semantic colors, compact labels, field captions and copyable values."
    >
      <AppCard class="space-y-5">
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
        <div class="grid gap-4 border-t border-border pt-4 sm:grid-cols-3">
          <AppDataLabel
            label="Project code"
            value="PRJ-001"
            icon="lucide:copy"
            copied
          />
          <AppDataLabel
            label="Active issues"
            :value="24"
            size="xl"
            color="primary"
            icon="lucide:circle-dot"
          />
          <AppDataLabel label="Owner" />
        </div>
      </AppCard>
    </AppSection>
    <AppSection
      title="Sections and cards"
      description="AppSection provides structure. AppCard adds a surface with independent color and variant props."
    >
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <AppCard
          v-for="card in cards"
          :key="card.title"
          :color="card.color"
          :variant="card.variant"
        >
          <div class="text-sm font-medium">{{ card.title }}</div>
          <code class="mt-1 block text-xs text-muted-foreground">color="{{ card.color }}" variant="{{ card.variant }}"</code><p class="mt-2 text-sm text-muted-foreground">Card content: description, data or settings.</p>
        </AppCard>
      </div>
    </AppSection>
    <AppSection
      title="Page layout"
      description="AppPageView combines a header, actions, content and footer slots."
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
              size="sm"
              variant="outline"
              label="Share"
              icon="lucide:share-2"
            />
          </template>
          <AppSection title="Key metrics">
            <div class="grid gap-4 sm:grid-cols-3">
              <AppDataLabel
                label="Status"
                value="In progress"
                icon="lucide:circle-dot"
              /><AppDataLabel
                label="Members"
                value="8 members"
                icon="lucide:users"
              /><AppDataLabel
                label="Completed"
                value="24 issues"
                icon="lucide:check"
              />
            </div>
          </AppSection>
          <template #footer><div class="text-xs text-muted-foreground">Changes are saved automatically</div></template>
        </AppPageView>
      </AppCard>
    </AppSection>
    <AppSection
      title="Data states"
      description="Loading and empty states preserve the page structure."
    >
      <div class="grid gap-4 sm:grid-cols-3">
        <AppCard class="flex min-h-28 items-center justify-center"><AppLoadingIndicator label="Loading data…" /></AppCard>
        <AppCard class="flex min-h-28 items-center justify-center gap-2"><AppEmptyData label="No data" /><span class="text-sm text-muted-foreground">No data</span></AppCard>
        <AppCard class="flex min-h-28 items-center justify-center gap-4"><AppCircularProgress :value="68" /><span class="text-sm">68% complete</span></AppCard>
      </div>
    </AppSection>
  </div>
</template>
