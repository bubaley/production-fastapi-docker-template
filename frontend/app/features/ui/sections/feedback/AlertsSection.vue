<script setup lang="ts">
import UiDemo from '../../components/UiDemo.vue'

const alertTones = ['info', 'success', 'warning', 'destructive', 'neutral'] as const
</script>

<template>
  <UiDemo
    title="Tones"
    code='tone="info | success | warning | destructive | neutral"'
    description="Status alerts are role=status; warning and destructive are role=alert."
    bare
  >
    <div class="flex flex-col gap-3">
      <AppAlert
        v-for="tone in alertTones"
        :key="tone"
        :tone="tone"
        :title="`Tone: ${tone}`"
        description="Alerts announce status or problems inside the page."
      />
    </div>
  </UiDemo>
</template>
