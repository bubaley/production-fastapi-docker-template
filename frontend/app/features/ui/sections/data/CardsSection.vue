<script setup lang="ts">
import { TONES } from '~/shared/ui/app/tone'
import UiDemo from '../../components/UiDemo.vue'

const cardVariants = ['outline', 'default', 'muted', 'elevated'] as const
</script>

<template>
  <UiDemo
    title="Variants"
    code='variant="outline | default | muted | elevated"'
    description="outline is the default surface; muted for a quiet nested block."
    bare
  >
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
  </UiDemo>
  <UiDemo
    title="Tones and interaction"
    code='tone="success" · interactive · padding="sm"'
    bare
  >
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
  </UiDemo>
  <UiDemo
    title="Avatars"
    code='AppAvatar name variant="soft"'
    description="Initials from the name; AppSkeleton circle while the person loads."
  >
    <div class="flex flex-wrap items-center gap-3">
      <AppAvatar
        name="Soft Avatar"
        variant="soft"
      />
      <AppAvatar name="Solid Avatar" />
      <AppAvatar
        name="Small"
        size="small"
      />
      <AppSkeleton circle />
    </div>
  </UiDemo>
</template>
