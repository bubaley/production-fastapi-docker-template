<script setup lang="ts">
/**
 * One line of a settings list: label and description on the left, the control on the right;
 * stacked below on phones. Rows separate themselves with a hairline.
 */
withDefaults(
  defineProps<{
    label?: string
    description?: string
    /** `id` of the control, so clicking the label focuses it. */
    forId?: string
    /** The control takes the full width under the label (text areas, pickers). */
    stacked?: boolean
    tone?: 'neutral' | 'destructive'
  }>(),
  { tone: 'neutral' },
)
</script>

<template>
  <div
    class="flex min-w-0 flex-col gap-2 border-b border-border py-3.5 last:border-b-0"
    :class="!stacked && 'sm:flex-row sm:items-center sm:gap-6'"
  >
    <div class="min-w-0 flex-1">
      <component
        :is="forId ? 'label' : 'div'"
        :for="forId"
        class="block text-sm font-medium"
        :class="tone === 'destructive' ? 'text-destructive' : 'text-foreground'"
        >{{ label }}<slot name="label"
      /></component>
      <p
        v-if="description || $slots.description"
        class="mt-0.5 text-sm text-muted-foreground"
      >
        <slot name="description">{{ description }}</slot>
      </p>
    </div>
    <div
      v-if="$slots.default"
      class="flex min-w-0 shrink-0 flex-wrap items-center gap-2"
      :class="stacked ? 'w-full' : 'sm:max-w-[60%] sm:justify-end'"
    >
      <slot />
    </div>
  </div>
</template>
