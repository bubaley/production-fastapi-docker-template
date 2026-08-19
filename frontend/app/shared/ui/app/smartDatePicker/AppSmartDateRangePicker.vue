<template>
  <div class="smart-date-range-picker inline-flex">
    <AppButton
      severity="secondary"
      variant="outlined"
      rounded
      size="small"
      style="border-radius: 1000px"
      class="px-3!"
      icon="lucide:clock"
      :label="triggerLabel"
      icon-pos="left"
      @click="togglePopover"
    />

    <Popover
      ref="popoverRef"
      class="smart-date-range-popover"
    >
      <div class="picker-panel">
        <div class="picker-body">
          <div class="absolute-column">
            <div class="column-title">Абсолютный период</div>

            <div class="flex flex-col gap-3">
              <div class="field-block">
                <label class="field-label">От</label>
                <CSmartDatePicker
                  v-model="draftFrom"
                  placeholder="now-1h"
                />
              </div>

              <div class="field-block">
                <label class="field-label">До</label>
                <CSmartDatePicker
                  v-model="draftTo"
                  placeholder="now"
                />
              </div>

              <p
                v-if="draftError"
                class="text-sm text-[var(--p-danger-500)]"
              >
                {{ draftError }}
              </p>

              <div class="flex mt-2">
                <AppButton
                  label="Применить период"
                  @click="applyAbsolute"
                />
              </div>
            </div>

            <div
              v-if="recentRanges.length"
              class="recent-block"
            >
              <div class="column-title">Недавние периоды</div>
              <button
                v-for="item in recentRanges"
                :key="`${item.from}|${item.to}`"
                type="button"
                class="recent-item"
                @click="applyRange(item)"
              >
                {{ formatRecent(item) }}
              </button>
            </div>
          </div>

          <div class="quick-column">
            <CSmartDateQuickList
              :items="SMART_QUICK_RANGES"
              :active-id="activeQuickId"
              search-placeholder="Поиск быстрых периодов"
              @select="selectQuickRange"
            />
          </div>
        </div>
      </div>
    </Popover>
  </div>
</template>

<script setup lang="ts">
import Popover from 'primevue/popover'
import type { PopoverMethods } from 'primevue/popover'
import {
  SMART_DATE_RANGE_DEFAULT,
  SMART_QUICK_RANGES,
  useSmartDateRange,
  type SmartDateRange,
  type SmartQuickRange,
} from '~/shared/ui/app/smartDatePicker/composables/useSmartDateRange'
import CSmartDatePicker from './AppSmartDatePicker.vue'
import CSmartDateQuickList from './AppSmartDateQuickList.vue'

const RECENT_STORAGE_KEY = 'smart-date-range-recent'
const MAX_RECENT = 5

const model = defineModel<SmartDateRange>({
  default: () => ({ ...SMART_DATE_RANGE_DEFAULT }),
})

const emit = defineEmits<{
  apply: [value: SmartDateRange]
}>()

const { getRangeLabel, resolveRange, toRangeFromQuick } = useSmartDateRange()

const popoverRef = ref<PopoverMethods | null>(null)

const draftFrom = ref<string | null>(model.value.from)
const draftTo = ref<string | null>(model.value.to)
const draftError = ref<string | null>(null)
const recentRanges = ref<SmartDateRange[]>([])

const triggerLabel = computed(() => getRangeLabel(model.value))

const activeQuickId = computed(() => {
  if (model.value.quickRangeId) return model.value.quickRangeId
  return SMART_QUICK_RANGES.find((item) => item.from === model.value.from && item.to === model.value.to)?.id ?? null
})

const syncDraftFromModel = () => {
  draftFrom.value = model.value.from
  draftTo.value = model.value.to
  draftError.value = null
}

const togglePopover = (event: Event) => {
  syncDraftFromModel()
  popoverRef.value?.toggle(event)
}

const loadRecent = () => {
  if (!import.meta.client) return
  try {
    const raw = localStorage.getItem(RECENT_STORAGE_KEY)
    if (!raw) return
    const parsed = JSON.parse(raw) as SmartDateRange[]
    if (Array.isArray(parsed)) recentRanges.value = parsed.slice(0, MAX_RECENT)
  } catch {
    recentRanges.value = []
  }
}

const saveRecent = (range: SmartDateRange) => {
  if (!import.meta.client) return
  const next = [
    { from: range.from, to: range.to, quickRangeId: range.quickRangeId ?? null },
    ...recentRanges.value.filter((item) => !(item.from === range.from && item.to === range.to)),
  ].slice(0, MAX_RECENT)
  recentRanges.value = next
  localStorage.setItem(RECENT_STORAGE_KEY, JSON.stringify(next))
}

const commitRange = (range: SmartDateRange, options?: { close?: boolean; remember?: boolean }) => {
  const resolved = resolveRange(range)
  if (!resolved) {
    draftError.value = 'Некорректный период. Используйте now, now-1h или YYYY-MM-DD HH:mm:ss'
    return false
  }

  const next: SmartDateRange = {
    from: range.from.trim(),
    to: range.to.trim(),
    quickRangeId: range.quickRangeId ?? null,
  }
  model.value = next
  draftFrom.value = next.from
  draftTo.value = next.to
  draftError.value = null
  if (options?.remember !== false) saveRecent(next)
  emit('apply', next)
  if (options?.close !== false) popoverRef.value?.hide()
  return true
}

const applyRange = (range: SmartDateRange) => {
  commitRange(range)
}

const selectQuickRange = (item: SmartQuickRange) => {
  commitRange(toRangeFromQuick(item), { remember: true })
}

const applyAbsolute = () => {
  const from = (draftFrom.value || '').trim()
  const to = (draftTo.value || '').trim()
  const quick = SMART_QUICK_RANGES.find((item) => item.from === from && item.to === to)
  commitRange({
    from,
    to,
    quickRangeId: quick?.id ?? null,
  })
}

const formatRecent = (item: SmartDateRange) => {
  if (item.quickRangeId) {
    const quick = SMART_QUICK_RANGES.find((entry) => entry.id === item.quickRangeId)
    if (quick) return quick.label
  }
  return `${item.from} → ${item.to}`
}

watch(
  () => model.value,
  () => syncDraftFromModel(),
  { deep: true },
)

onMounted(() => {
  loadRecent()
})
</script>

<style scoped lang="scss">
.picker-panel {
  min-width: min(720px, 92vw);
}

.picker-body {
  display: grid;
  grid-template-columns: minmax(280px, 1.1fr) minmax(220px, 0.9fr);
}

.absolute-column,
.quick-column {
  padding: 1rem;
}

.absolute-column {
  border-right: 1px solid var(--border-base);
}

.column-title {
  margin-bottom: 0.75rem;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--fg-secondary);
}

.field-block {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.field-label {
  font-size: 0.75rem;
  color: var(--fg-tertiary);
}

.recent-block {
  margin-top: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.recent-item {
  width: 100%;
  text-align: left;
  border: 0;
  background: transparent;
  color: var(--fg-secondary);
  cursor: pointer;
  border-radius: var(--radius-sm);
  padding: 0.45rem 0.65rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 0.8rem;
  transition: background-color 0.15s ease;

  &:hover {
    background: var(--bg-tertiary, var(--p-content-hover-background));
  }
}

@media (max-width: 640px) {
  .picker-body {
    grid-template-columns: 1fr;
  }

  .absolute-column {
    border-right: 0;
    border-bottom: 1px solid var(--border-base);
  }
}
</style>
