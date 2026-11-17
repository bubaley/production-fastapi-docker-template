<script setup lang="ts">
import { PAGE_ACTIONS_CLASS } from '../app/pageContainer'

withDefaults(
  defineProps<{ title?: string; titleSize?: TitleSizeToken; description?: string; backAction?: () => void }>(),
  { titleSize: 'xl' },
)
</script>
<template>
  <!-- AppPage pads the header (gutter, space above). Back and prefix lead the title row, the description sits under the
       title, actions sit at the top right on the title line (on phones: a full row under the title). -->
  <header class="flex min-h-control-md w-full flex-wrap items-start gap-3">
    <!-- The lead (back, prefix) and the title line are one control tall, so they line up with the actions. -->
    <div
      v-if="backAction || $slots.prefix"
      class="flex min-h-control-md shrink-0 items-center gap-3"
    >
      <AppBackButton
        v-if="backAction"
        :back-action="backAction"
      />
      <slot name="prefix" />
    </div>
    <div
      v-if="title || description || $slots.title || $slots['title-append']"
      class="min-w-[min(100%,14rem)] flex-1 basis-56"
    >
      <div class="flex min-h-control-md min-w-0 flex-wrap items-center gap-2">
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
        class="mt-1 text-base text-muted-foreground"
      >
        {{ description }}
      </p>
    </div>
    <div
      v-if="$slots.actions"
      class="ml-auto max-w-full"
      :class="PAGE_ACTIONS_CLASS"
    >
      <slot name="actions" />
    </div>
  </header>
</template>
