<script setup lang="ts">
import { ArrowRight, CircleCheck, Plus, Star } from '@lucide/vue'
import type { AppButtonVariant } from '~/shared/ui/app/appButton'
import type { AppControlSize } from '~/shared/ui/app/types/control'
import { TONES } from '~/shared/ui/app/tone'

const variants: AppButtonVariant[] = ['default', 'secondary', 'outline', 'ghost', 'link', 'destructive']
const sizes: AppControlSize[] = ['xs', 'sm', 'md', 'lg']
const badgeVariants = ['solid', 'soft', 'outline'] as const
const toast = useToast()
</script>
<template>
  <div class="space-y-10">
    <AppSection
      title="Buttons"
      description="AppButton: variant × size. Icon-only buttons become square and require aria-label."
    >
      <AppCard class="space-y-6">
        <div class="overflow-x-auto">
          <table class="w-full min-w-[640px] border-separate border-spacing-y-2 text-left">
            <thead>
              <tr class="text-xs text-muted-foreground">
                <th class="w-28 font-normal">variant \ size</th>
                <th
                  v-for="size in sizes"
                  :key="size"
                  class="font-normal"
                >
                  {{ size }}
                </th>
                <th class="font-normal">icon-only</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="variant in variants"
                :key="variant"
              >
                <td class="text-xs text-muted-foreground">{{ variant }}</td>
                <td
                  v-for="size in sizes"
                  :key="size"
                >
                  <AppButton
                    :variant="variant"
                    :size="size"
                    label="Action"
                    @click="toast.default(`${variant} / ${size}`)"
                  />
                </td>
                <td>
                  <AppButton
                    :variant="variant"
                    :icon="Plus"
                    aria-label="Add"
                  />
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="flex flex-wrap items-center gap-3 border-t border-border pt-5">
          <span class="w-28 text-xs text-muted-foreground">states</span>
          <AppButton
            label="Loading"
            loading
          />
          <AppButton
            label="Disabled"
            disabled
          />
          <AppButton
            label="Icon end"
            variant="outline"
            :icon="ArrowRight"
            icon-position="end"
          />
          <AppButton
            label="Muted text"
            variant="outline"
            text-variant="muted"
          />
          <AppButton
            label="Fluid"
            variant="secondary"
            fluid
            class="sm:w-48"
          />
        </div>
      </AppCard>
    </AppSection>

    <AppSection
      title="Badges and tooltips"
      description="AppBadge: tone × variant. AppTooltip wraps any trigger."
    >
      <AppCard class="space-y-3">
        <div
          v-for="variant in badgeVariants"
          :key="variant"
          class="flex flex-wrap items-center gap-2"
        >
          <span class="w-28 text-xs text-muted-foreground">{{ variant }}</span>
          <AppBadge
            v-for="tone in TONES"
            :key="tone"
            :tone="tone"
            :variant="variant"
            :label="tone"
          />
        </div>
        <div class="flex flex-wrap items-center gap-3 border-t border-border pt-4">
          <span class="w-28 text-xs text-muted-foreground">tooltip</span>
          <AppTooltip text="Tooltips use the foreground color and open on hover or focus.">
            <template #trigger>
              <AppButton
                variant="outline"
                :icon="Star"
                aria-label="Favourite"
              />
            </template>
          </AppTooltip>
          <AppBadge
            tone="success"
            :icon="CircleCheck"
            label="With icon"
          />
        </div>
      </AppCard>
    </AppSection>
  </div>
</template>
