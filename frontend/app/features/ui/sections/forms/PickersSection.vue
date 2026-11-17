<script setup lang="ts">
import UiDemo from '../../components/UiDemo.vue'

const color = ref<string | null>('#7779ed')
const icon = ref<string | null>('folder')
</script>

<template>
  <UiDemo
    title="Color"
    code="AppColorPicker v-model"
    description="Preset swatches and a custom color; the list is data, not theme tokens."
  >
    <AppColorPicker
      v-model="color"
      label="Project color"
    />
  </UiDemo>
  <UiDemo
    title="Icon and color"
    code='AppAppearancePicker v-model:icon v-model:color subject="product"'
    description="Searchable, virtualized Lucide catalogue together with the color."
  >
    <div class="flex flex-wrap items-center gap-4">
      <AppAppearancePicker
        v-model:icon="icon"
        v-model:color="color"
        subject="product"
      />
      <span class="text-sm text-muted-foreground">Project icon and color</span>
    </div>
  </UiDemo>
</template>
