<template>
  <div
    v-if="showPagination"
    class="flex justify-center"
  >
    <div class="flex justify-center mt-4 lg:mt-0">
      <AppButton
        v-if="pagination.has_next"
        label="Показать еще"
        :loading="loading"
        font-weight="normal"
        severity="secondary"
        @click="handlePageChange(model + 1, true)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

export type AppPaginationEvent = {
  pagination: AppPagination
  append: boolean
}

export type AppPaginationProps = {
  pagination: AppPagination
  loading?: boolean
}

const props = withDefaults(defineProps<AppPaginationProps>(), {
  loading: false,
})

const emit = defineEmits<{
  pageChange: [event: AppPaginationEvent]
}>()

const model = defineModel<number>({ default: 1 })

const showPagination = computed(() => props.pagination.has_next || props.pagination.pages > 1)

const handlePageChange = (page: number, append: boolean) => {
  emit('pageChange', {
    append: append,
    pagination: {
      ...props.pagination,
      page,
    },
  })
}
</script>
