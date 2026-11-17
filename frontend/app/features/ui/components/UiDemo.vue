<script setup lang="ts">
/** One demo of a catalogue section: title, the prop it shows, a short rule and the live example. */
withDefaults(
  defineProps<{
    title?: string
    /** Prop or usage hint next to the title, e.g. `variant="default"`. */
    code?: string
    description?: string
    /** Without the frame, for examples that bring their own surface. */
    bare?: boolean
  }>(),
  {},
)
</script>

<template>
  <section class="flex min-w-0 flex-col gap-3">
    <header
      v-if="title || code || description"
      class="flex flex-col gap-1"
    >
      <div class="flex min-w-0 flex-wrap items-baseline gap-x-3 gap-y-1">
        <AppTitle
          v-if="title"
          as="h2"
          size="md"
          :title="title"
        />
        <code
          v-if="code"
          class="font-mono text-xs [overflow-wrap:anywhere] text-muted-foreground"
          >{{ code }}</code
        >
      </div>
      <p
        v-if="description"
        class="max-w-3xl text-sm text-muted-foreground"
      >
        {{ description }}
      </p>
    </header>
    <slot v-if="bare" />
    <AppCard
      v-else
      class="min-w-0"
    >
      <slot />
    </AppCard>
  </section>
</template>
