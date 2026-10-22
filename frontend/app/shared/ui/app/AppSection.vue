<script setup lang="ts">
export type AppSectionProps = {
  title?: string
  description?: string
  titleSize?: TitleSizeToken
  flat?: boolean
  templateVariant?: TemplateVariant
  backAction?: () => void
  display?: 'row' | 'column' | 'inline-row'
  class?: string
}
withDefaults(defineProps<AppSectionProps>(), { display: 'column', titleSize: 'lg' })
</script>
<template>
  <section class="flex min-w-0 flex-col gap-4">
    <header
      v-if="title || description || $slots.title || $slots.subtitle || $slots.actions || backAction"
      class="flex flex-col gap-1"
    >
      <div class="flex min-w-0 flex-wrap items-center gap-3">
        <AppBackButton
          v-if="backAction"
          :back-action="backAction"
        />
        <AppTitle
          v-if="title || $slots.title"
          as="h2"
          :size="titleSize"
          class="min-w-0 flex-1"
        >
          <slot name="title">{{ title }}</slot>
        </AppTitle>
        <div
          v-if="$slots.actions"
          class="ml-auto flex flex-wrap items-center gap-2"
        >
          <slot name="actions" />
        </div>
      </div>
      <p
        v-if="description"
        class="text-sm text-muted-foreground"
      >
        {{ description }}
      </p>
      <slot name="subtitle" />
    </header>
    <div :class="display === 'column' ? 'flex min-w-0 flex-col gap-4' : 'flex min-w-0 flex-wrap items-center gap-4'">
      <slot />
    </div>
  </section>
</template>
