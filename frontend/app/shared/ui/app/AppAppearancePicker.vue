<script setup lang="ts">
import { useVirtualizer } from '@tanstack/vue-virtual'
import { Circle, Search } from '@lucide/vue'
import { computed, nextTick, ref, shallowRef, watch, type Component } from 'vue'
import AppButton from './AppButton.vue'
import AppColorPicker from './AppColorPicker.vue'
import AppIcon from './AppIcon.vue'
import AppInput from './AppInput.vue'
import AppLoadingIndicator from './AppLoadingIndicator.vue'
import AppMenu from './AppMenu.vue'

export type AppAppearanceIconOption = {
  value: string
  label: string
  icon: Component
  searchText: string
}

const props = withDefaults(
  defineProps<{
    currentIcon?: Component
    disabled?: boolean
    locale?: 'ru' | 'en'
    subject: 'product' | 'label'
    loadIcons?: () => Promise<AppAppearanceIconOption[]>
    normalizeIcon?: (value?: string | null) => string
  }>(),
  {
    locale: 'ru',
    normalizeIcon: (value?: string | null) => value || 'circle',
    loadIcons: () => import('./appearanceIconCatalog').then((module) => module.appearanceIcons),
  },
)
const icon = defineModel<string | null>('icon', { default: null })
const color = defineModel<string | null>('color', { default: null })
const emit = defineEmits<{ change: [] }>()
const search = ref('')
const open = ref(false)
const loadingIcons = ref(false)
const icons = shallowRef<AppAppearanceIconOption[]>([])
const iconScrollElement = ref<HTMLElement | null>(null)
const filteredIcons = computed(() =>
  icons.value.filter((item) => item.searchText.includes(search.value.trim().toLocaleLowerCase())),
)
const columnCount = 6
const rowHeight = 40
const rowGap = 4
const viewportHeight = 288
const iconRowCount = computed(() => Math.ceil(filteredIcons.value.length / columnCount))
const iconRowVirtualizer = useVirtualizer(
  computed(() => ({
    count: iconRowCount.value,
    getScrollElement: () => iconScrollElement.value,
    estimateSize: () => rowHeight,
    gap: rowGap,
    overscan: 3,
  })),
)
const virtualRows = computed(() => iconRowVirtualizer.value.getVirtualItems())
const iconListHeight = computed(() => Math.min(iconRowVirtualizer.value.getTotalSize(), viewportHeight))
const iconsForRow = (rowIndex: number) => {
  const start = rowIndex * columnCount
  return filteredIcons.value.slice(start, start + columnCount)
}
const selectedIcon = computed(
  () => props.currentIcon || icons.value.find((item) => item.value === selectedIconId.value)?.icon || Circle,
)
const selectedIconId = computed(() => props.normalizeIcon(icon.value))
const subjectLabels = computed(() => {
  if (props.locale === 'en')
    return props.subject === 'label' ? (['label', 'Label'] as const) : (['product', 'Product'] as const)
  return props.subject === 'label' ? (['метки', 'метки'] as const) : (['продукта', 'продукта'] as const)
})
const triggerLabel = computed(() =>
  props.locale === 'en'
    ? `Choose ${subjectLabels.value[0]} icon and color`
    : `Выбрать иконку и цвет ${subjectLabels.value[0]}`,
)

function selectIcon(value: string) {
  icon.value = value
  emit('change')
}
function selectColor(value: string | null) {
  color.value = value
  emit('change')
}
watch(search, () => {
  void nextTick(() => iconRowVirtualizer.value.scrollToOffset(0))
})
watch(
  [open, icon],
  async ([isOpen, selected]) => {
    if ((!isOpen && (!selected || props.currentIcon)) || icons.value.length || loadingIcons.value) return
    loadingIcons.value = true
    try {
      icons.value = await props.loadIcons()
    } finally {
      loadingIcons.value = false
    }
  },
  { immediate: true },
)
</script>

<template>
  <AppMenu
    v-model:open="open"
    :disabled="disabled"
    align="start"
    content-class="p-0"
  >
    <template #trigger>
      <slot
        name="trigger"
        :aria-label="triggerLabel"
      >
        <AppButton
          variant="outline"
          size="icon"
          :disabled="disabled"
          :aria-label="triggerLabel"
        >
          <AppIcon
            :icon="selectedIcon"
            size="lg"
            :style="{ color: color || undefined }"
          />
        </AppButton>
      </slot>
    </template>
    <div class="w-80 overflow-hidden">
      <div class="p-3">
        <AppInput
          v-model="search"
          :placeholder="locale === 'en' ? 'Search icons' : 'Поиск иконок'"
          :icon="Search"
          autofocus
          :aria-label="locale === 'en' ? 'Search icons' : 'Поиск иконок'"
        />
        <AppLoadingIndicator
          v-if="loadingIcons"
          class="h-72"
          fluid
          :label="locale === 'en' ? 'Loading icons…' : 'Загрузка иконок…'"
        />
        <div
          v-else
          ref="iconScrollElement"
          class="mt-3 overflow-y-auto"
          :style="{ height: `${iconListHeight}px` }"
          role="group"
          :aria-label="locale === 'en' ? `${subjectLabels[1]} icons` : `Иконки ${subjectLabels[1]}`"
        >
          <div
            class="relative w-full"
            :style="{ height: `${iconRowVirtualizer.getTotalSize()}px` }"
          >
            <div
              v-for="virtualRow in virtualRows"
              :key="String(virtualRow.key)"
              class="absolute top-0 left-0 grid w-full grid-cols-6 justify-items-center gap-1"
              :style="{
                height: `${virtualRow.size}px`,
                transform: `translateY(${virtualRow.start}px)`,
              }"
            >
              <AppButton
                v-for="item in iconsForRow(virtualRow.index)"
                :key="item.value"
                :icon="item.icon"
                size="icon-lg"
                variant="ghost"
                :class="
                  selectedIconId === item.value &&
                  'border border-[color:var(--appearance-icon-color)] bg-transparent hover:bg-transparent'
                "
                :aria-label="item.label"
                :title="item.label"
                :aria-pressed="selectedIconId === item.value"
                :disabled="disabled"
                :style="{
                  color: color || undefined,
                  '--appearance-icon-color': color || 'currentColor',
                }"
                @click="selectIcon(item.value)"
              />
            </div>
          </div>
        </div>
        <p
          v-if="!loadingIcons && !filteredIcons.length"
          class="py-4 text-center text-sm text-muted-foreground"
        >
          {{ locale === 'en' ? 'No icons found' : 'Иконки не найдены' }}
        </p>
      </div>
      <div class="border-t border-border px-3 py-3">
        <AppColorPicker
          :model-value="color"
          :disabled="disabled"
          @update:model-value="selectColor"
        />
      </div>
    </div>
  </AppMenu>
</template>
