<template>
  <div
    v-if="hasNext"
    class="flex justify-center"
  >
    <div class="mt-4 flex justify-center lg:mt-0">
      <AppButton
        label="Показать еще"
        :loading="loading"
        variant="secondary"
        @click="emit('loadMore')"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
export type AppPaginationProps = {
  hasNext: boolean
  loading?: boolean
}

withDefaults(defineProps<AppPaginationProps>(), {
  loading: false,
})

const emit = defineEmits<{
  loadMore: []
}>()
</script>
