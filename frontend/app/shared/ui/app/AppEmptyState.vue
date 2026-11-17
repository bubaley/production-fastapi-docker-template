<script setup lang="ts">
import { computed, type Component } from 'vue'
import { Inbox } from '@lucide/vue'
import { cn } from '~/shared/lib/utils'
import AppIcon from './AppIcon.vue'
import { toneVariants, type Tone } from './tone'

export type AppEmptyStateVariant = 'default' | 'inline' | 'quiet'
export type AppEmptyStateAlign = 'center' | 'start'
export type AppEmptyStateSize = 'sm' | 'md'

/**
 * A block in place of content that has nothing to show: an empty list, a search without results, a failed load.
 * Icon in a soft tinted square, title, description, then one primary and at most one secondary action.
 * `variant="inline"` lays it out as a row (actions at the end) for a slot inside a card, table or form.
 * `variant="quiet"` is one calm muted line under a small icon, no frame and no heading weight: the empty or failed
 * state inside a table or list (`AppTable`, `AppList`).
 */
const props = withDefaults(
  defineProps<{
    title?: string
    description?: string
    icon?: Component
    /** Tint of the icon square: `primary` — no data yet, `muted` — nothing found, `destructive` — failed to load. */
    tone?: Tone
    variant?: AppEmptyStateVariant
    /** Stacked variant only; `inline` always starts at the left. */
    align?: AppEmptyStateAlign
    /** Dashed frame; turn off when the state sits inside an already framed surface. */
    bordered?: boolean
    size?: AppEmptyStateSize
    as?: 'h2' | 'h3' | 'h4' | 'div'
  }>(),
  {
    title: 'Здесь пока пусто',
    icon: () => Inbox,
    tone: 'primary',
    variant: 'default',
    align: 'center',
    bordered: true,
    size: 'md',
    as: 'h3',
  },
)

const inline = computed<boolean>(() => props.variant === 'inline')
const quiet = computed<boolean>(() => props.variant === 'quiet')
const centered = computed<boolean>(() => !inline.value && props.align === 'center')
const small = computed<boolean>(() => props.size === 'sm')

const rootClass = computed<string>(() =>
  cn(
    'flex w-full min-w-0 rounded-xl',
    props.bordered && !quiet.value && 'border border-dashed border-border-strong',
    quiet.value
      ? ['flex-col gap-2', centered.value ? 'items-center text-center' : 'items-start text-left']
      : inline.value
        ? ['flex-col gap-3 sm:flex-row sm:items-center sm:gap-4', small.value ? 'px-4 py-3' : 'px-5 py-4']
        : [
            'flex-col',
            small.value ? 'gap-3' : 'gap-4',
            centered.value ? 'items-center text-center' : 'items-start text-left',
            props.bordered && (small.value ? 'px-5 py-6' : 'px-8 py-10'),
          ],
  ),
)
</script>

<template>
  <div
    :class="rootClass"
    :role="tone === 'destructive' || tone === 'warning' ? 'alert' : 'status'"
  >
    <AppIcon
      v-if="quiet"
      :icon="icon"
      size="md"
      :class="tone === 'destructive' || tone === 'warning' ? toneVariants({ tone }) : 'text-muted-foreground/70'"
    />
    <span
      v-else
      class="flex shrink-0 items-center justify-center rounded-lg"
      :class="[small ? 'size-9' : 'size-12', toneVariants({ tone, appearance: 'soft' })]"
    >
      <AppIcon
        :icon="icon"
        :size="small ? 'md' : 22"
      />
    </span>
    <div
      class="flex min-w-0 flex-col gap-1"
      :class="inline && 'flex-1'"
    >
      <component
        :is="quiet ? 'p' : as"
        :class="
          quiet
            ? 'text-sm text-muted-foreground'
            : ['font-semibold text-foreground', small || inline ? 'text-base' : 'text-lg', centered && 'text-balance']
        "
      >
        {{ title }}
      </component>
      <p
        v-if="description || $slots.default"
        class="max-w-md text-sm text-muted-foreground"
        :class="centered && 'text-balance'"
      >
        <slot>{{ description }}</slot>
      </p>
    </div>
    <div
      v-if="$slots.actions"
      class="flex shrink-0 flex-wrap items-center gap-2"
      :class="[centered && 'justify-center', !inline && !small && !quiet && 'mt-1']"
    >
      <slot name="actions" />
    </div>
  </div>
</template>
