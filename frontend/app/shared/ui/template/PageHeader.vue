<script setup lang="ts">
withDefaults(
  defineProps<{ title?: string; titleSize?: TitleSizeToken; description?: string; backAction?: () => void }>(),
  { titleSize: 'xl' },
)
</script>
<template>
  <header class="flex min-h-12 w-full flex-wrap items-center gap-3 px-4 py-3">
    <AppBackButton
      v-if="backAction"
      :back-action="backAction"
    />
    <slot name="prefix" />
    <div
      v-if="title || description || $slots.title || $slots['title-append']"
      class="min-w-[min(100%,14rem)] flex-1 basis-56"
    >
      <div class="flex min-w-0 flex-wrap items-center gap-2">
        <AppTitle
          v-if="title || $slots.title"
          as="h1"
          :size="titleSize"
        >
          <slot name="title">{{ title }}</slot> </AppTitle
        ><slot name="title-append" />
      </div>
      <p
        v-if="description"
        class="mt-0.5 text-sm text-muted-foreground"
      >
        {{ description }}
      </p>
    </div>
    <div
      v-if="$slots.actions"
      class="ml-auto flex max-w-full flex-wrap items-center justify-end gap-2"
    >
      <slot name="actions" />
    </div>
  </header>
</template>
