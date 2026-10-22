<script setup lang="ts">
export type AppPageProps = { title?: string; contentClass?: string }

withDefaults(defineProps<AppPageProps>(), { title: '', contentClass: 'p-4' })
</script>

<template>
  <section class="flex h-full min-h-0 w-full min-w-0 flex-col overflow-hidden">
    <div
      v-if="title || $slots.header"
      class="shrink-0"
      :class="title && 'flex min-h-[40px] items-center gap-3 px-3'"
    >
      <h1
        v-if="title"
        class="m-0 min-w-0 flex-1 text-lg font-semibold tracking-tight"
      >
        {{ title }}
      </h1>
      <slot name="header" />
    </div>
    <div
      v-if="$slots.subheader"
      class="shrink-0 px-3"
    >
      <slot name="subheader" />
    </div>
    <div
      v-if="title || $slots.header || $slots.subheader"
      class="shrink-0 border-b border-border"
    />
    <div
      v-if="$slots.controls"
      class="shrink-0 px-3"
    >
      <slot name="controls" />
    </div>
    <main class="min-h-0 flex-1 overflow-auto">
      <div
        class="h-full min-h-full"
        :class="contentClass"
      >
        <slot />
      </div>
    </main>
    <footer
      v-if="$slots.footer"
      class="shrink-0 border-t border-border p-4"
    >
      <slot name="footer" />
    </footer>
  </section>
</template>
