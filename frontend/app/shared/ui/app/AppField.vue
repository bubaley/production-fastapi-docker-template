<script setup lang="ts">
import { computed, useId } from 'vue'
import { Label } from '~/shared/ui/shadcn/label'
const props = defineProps<{ id?: string; label?: string; error?: string; hint?: string }>()
const generatedId = useId()
const fieldId = computed(() => props.id || generatedId)
const messageId = computed(() => `${fieldId.value}-message`)
</script>
<template>
  <div class="flex min-w-0 flex-col gap-1.5">
    <Label
      v-if="label"
      :for="fieldId"
      class="leading-[inherit] text-foreground"
      >{{ label }}</Label
    ><slot
      :id="fieldId"
      :described-by="error || hint ? messageId : undefined"
    /><span
      v-if="error || hint"
      :id="messageId"
      class="text-xs"
      :class="error ? 'text-destructive' : 'text-muted-foreground'"
      >{{ error || hint }}</span
    >
  </div>
</template>
