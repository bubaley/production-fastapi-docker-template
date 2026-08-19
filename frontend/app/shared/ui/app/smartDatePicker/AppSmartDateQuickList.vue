<template>
  <div class="smart-date-quick-list">
    <AppInput
      v-model="quickSearch"
      is-search
      clearable
      :placeholder="searchPlaceholder"
    />
    <div class="quick-list">
      <button
        v-for="item in filteredItems"
        :key="item.id"
        type="button"
        class="quick-item"
        :class="{ active: item.id === activeId }"
        @click="emit('select', item)"
      >
        {{ item.label }}
      </button>
      <div
        v-if="!filteredItems.length"
        class="fg-tertiary px-2 py-3 text-sm"
      >
        Ничего не найдено
      </div>
    </div>
  </div>
</template>

<script setup lang="ts" generic="T extends { id: string; label: string }">
const props = withDefaults(
  defineProps<{
    items: T[]
    activeId?: string | null
    searchPlaceholder?: string
  }>(),
  {
    activeId: null,
    searchPlaceholder: 'Поиск',
  },
)

const emit = defineEmits<{
  select: [item: T]
}>()

const quickSearch = ref<string | null>(null)

const filteredItems = computed(() => {
  const query = (quickSearch.value || '').trim().toLowerCase()
  if (!query) return props.items
  return props.items.filter((item) => item.label.toLowerCase().includes(query))
})
</script>

<style scoped lang="scss">
.smart-date-quick-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  min-height: 320px;
}

.quick-list {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  overflow: auto;
  max-height: 360px;
  margin: 0 -0.35rem;
  padding: 0 0.35rem;
}

.quick-item {
  position: relative;
  width: 100%;
  text-align: left;
  border: 0;
  background: transparent;
  color: var(--fg-base);
  cursor: pointer;
  border-radius: var(--radius-sm);
  padding: 0.45rem 0.65rem;
  font-size: 0.875rem;
  transition: background-color 0.15s ease;

  &:hover {
    background: var(--bg-tertiary, var(--p-content-hover-background));
  }

  &.active {
    background: var(--bg-tertiary, var(--p-content-hover-background));
    font-weight: 600;

    &::before {
      content: '';
      position: absolute;
      left: 0;
      top: 0.35rem;
      bottom: 0.35rem;
      width: 3px;
      border-radius: 999px;
      background: var(--p-primary-color, var(--p-primary-500));
    }
  }
}

@media (max-width: 640px) {
  .smart-date-quick-list {
    min-height: auto;
  }
}
</style>
