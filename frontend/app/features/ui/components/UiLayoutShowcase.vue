<script setup lang="ts">
import { Check, CircleDot, Copy, Share2, TriangleAlert, Users } from '@lucide/vue'
import type { AppLabelConfig } from '~/shared/ui/app/types/label-types'
import { TONES } from '~/shared/ui/app/tone'
const labels: AppLabelConfig[] = [
  { label: 'In progress', icon: CircleDot, tone: 'primary' },
  { label: 'Success', icon: Check, tone: 'success' },
  { label: 'Warning', icon: TriangleAlert, tone: 'warning' },
  { label: 'Info', icon: CircleDot, tone: 'info' },
  { label: 'Danger', icon: TriangleAlert, tone: 'destructive' },
]
const labelVariants = ['default', 'soft', 'outline'] as const
const cardVariants = ['outline', 'default', 'muted', 'elevated'] as const
const alertTones = ['info', 'success', 'warning', 'destructive', 'neutral'] as const
const progressTones = ['primary', 'success', 'info', 'warning', 'destructive'] as const
</script>
<template>
  <div class="space-y-10">
    <AppSection
      title="Typography"
      description="AppTitle: semantic heading tags and Tailwind font sizes."
    >
      <AppCard class="space-y-4">
        <AppTitle
          v-for="sample in [
            { size: 'xl', as: 'h1', text: 'xl · text-3xl · h1' },
            { size: 'lg', as: 'h2', text: 'lg · text-xl · h2' },
            { size: 'md', as: 'h3', text: 'md · text-base · h3' },
            { size: 'sm', as: 'h4', text: 'sm · text-sm · h4' },
          ] as const"
          :key="sample.size"
          :size="sample.size"
          :as="sample.as"
          :title="sample.text"
        />
      </AppCard>
    </AppSection>
    <AppSection
      title="Labels and values"
      description="One tone vocabulary (tone.ts) for labels, cards, badges, icons, alerts and progress."
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
        </div>
      </AppCard>
    </AppSection>
    <AppSection
      title="Cards"
      description="AppCard: variant × tone. AppSection provides structure without a surface."
    >
      <div class="space-y-4">
        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <AppCard
            v-for="variant in cardVariants"
            :key="variant"
            :variant="variant"
          >
            <code class="text-xs text-muted-foreground">variant="{{ variant }}"</code>
            <p class="mt-2 text-sm">Card content.</p>
          </AppCard>
        </div>
        <div class="grid gap-4 sm:grid-cols-3 lg:grid-cols-4">
          <AppCard
            v-for="tone in TONES"
            :key="tone"
            :tone="tone"
            padding="sm"
          >
            <code class="text-xs">tone="{{ tone }}"</code>
          </AppCard>
          <AppCard
            interactive
            padding="sm"
          >
            <code class="text-xs">interactive</code>
          </AppCard>
        </div>
      </div>
    </AppSection>
    <AppSection
      title="Feedback"
      description="AppAlert, AppProgress, AppCircularProgress, AppSkeleton, AppLoadingIndicator and AppEmptyData."
    >
      <div class="grid gap-4 lg:grid-cols-2">
        <div class="space-y-3">
          <AppAlert
            v-for="tone in alertTones"
            :key="tone"
            :tone="tone"
            :title="`Tone: ${tone}`"
            description="Alerts announce status (role=status) or problems (role=alert)."
          />
        </div>
        <AppCard class="space-y-5">
          <div
            v-for="(tone, index) in progressTones"
            :key="tone"
            class="flex items-center gap-3"
          >
            <code class="w-24 text-xs text-muted-foreground">{{ tone }}</code>
            <AppProgress
              :value="30 + index * 15"
              :tone="tone"
              :aria-label="`${tone} progress`"
            />
          </div>
          <div class="flex flex-wrap items-center gap-4 border-t border-border pt-4">
            <AppCircularProgress :value="68" />
            <AppCircularProgress
              :value="40"
              tone="success"
            />
            <AppLoadingIndicator label="Loading data…" />
            <AppEmptyData label="No data" />
          </div>
          <div class="border-t border-border pt-4">
            <AppSkeleton :lines="3" />
          </div>
        </AppCard>
      </div>
    </AppSection>
    <AppSection
      title="Scroll area"
      description="AppScrollArea gives a bounded region thin, theme-colored scrollbars."
    >
      <AppCard padding="none">
        <AppScrollArea class="h-40">
          <div class="space-y-2 p-4">
            <p
              v-for="row in 12"
              :key="row"
              class="text-sm"
            >
              Row {{ row }} of a long list
            </p>
          </div>
        </AppScrollArea>
      </AppCard>
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
              :icon="Share2"
            />
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
    </AppSection>
  </div>
</template>
