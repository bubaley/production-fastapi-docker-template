<script setup lang="ts">
import UiDemo from '../../components/UiDemo.vue'
</script>

<template>
  <UiDemo
    title="Elevation"
    code='shadow-overlay · AppCard variant="elevated"'
    description="Page surfaces stay flat with a border. Floating surfaces get shadow-overlay (denser in the dark theme); elevated cards are for rare highlighted blocks."
    bare
  >
    <div class="grid gap-4 sm:grid-cols-3">
      <AppCard>
        <code class="text-xs text-muted-foreground">flat · border</code>
        <p class="mt-2 text-sm">Cards, sections and tables.</p>
      </AppCard>
      <AppCard variant="elevated">
        <code class="text-xs text-muted-foreground">variant="elevated"</code>
        <p class="mt-2 text-sm">A highlighted block on the page.</p>
      </AppCard>
      <div class="rounded-lg border border-border bg-popover p-4 shadow-overlay">
        <code class="text-xs text-muted-foreground">shadow-overlay</code>
        <p class="mt-2 text-sm">Menus, popovers, pickers, dialogs.</p>
      </div>
    </div>
  </UiDemo>
</template>
