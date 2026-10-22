<script setup lang="ts">
import { ref } from 'vue'
import AppButton from './AppButton.vue'
import AppLoadingIndicator from './AppLoadingIndicator.vue'
import { useAutoPagination } from './infinite-scroll/useAutoPagination'
const props = withDefaults(
  defineProps<{
    hasMore: boolean
    requestKey: unknown
    loading?: boolean
    disabled?: boolean
    error?: boolean | string
    showError?: boolean
    locale?: 'ru' | 'en'
  }>(),
  { locale: 'ru', showError: true },
)
const emit = defineEmits<{ load: []; retry: [] }>()
const sentinel = ref<HTMLElement>()
useAutoPagination(sentinel, {
  hasMore: () => props.hasMore,
  requestKey: () => props.requestKey,
  loading: () => !!props.loading,
  disabled: () => !!props.disabled,
  error: () => !!props.error,
  load: () => emit('load'),
})
</script>
<template>
  <div
    v-if="hasMore || loading || error"
    ref="sentinel"
    class="flex min-h-12 shrink-0 flex-col items-center justify-center gap-2 py-3"
    :aria-busy="loading || undefined"
  >
    <AppLoadingIndicator
      v-if="loading"
      fluid
      size="md"
      :locale="locale"
    />
    <template v-else-if="error && showError">
      <p
        role="alert"
        class="text-sm text-destructive"
      >
        {{
          typeof error === 'string'
            ? error
            : locale === 'en'
              ? 'Could not load the next page.'
              : 'Не удалось загрузить следующие записи.'
        }}
      </p>
      <AppButton
        variant="outline"
        :disabled="disabled"
        :label="locale === 'en' ? 'Retry' : 'Повторить'"
        @click="emit('retry')"
      />
    </template>
  </div>
</template>
