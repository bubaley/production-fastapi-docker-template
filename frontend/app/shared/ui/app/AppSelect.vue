<script setup lang="ts" generic="T">
import { useOverlayStack } from './useOverlayStack'
import { computed, nextTick, ref, shallowRef, watch } from 'vue'
import { Check, ChevronDown, Search } from '@lucide/vue'
import {
  ComboboxRoot,
  ComboboxAnchor,
  ComboboxTrigger,
  ComboboxInput,
  ComboboxPortal,
  ComboboxContent,
  ComboboxViewport,
  ComboboxItem,
  ComboboxItemIndicator,
} from '~/shared/ui/shadcn/combobox'
import AppField from './AppField.vue'
import AppClearButton from './AppClearButton.vue'
import AppButton from './AppButton.vue'
import AppIcon from './AppIcon.vue'
import AppLoadingIndicator from './AppLoadingIndicator.vue'
import SelectChip from './select/SelectChip.vue'
import { useSelectSource } from './select/useSelectSource'
import { normalizeSelection, readItem, selectionKey, valueOf } from './select/selection'
import type { AppSelectProps, SelectSource, SelectValue } from './select/types'
import { resourceSource } from '~/shared/api/resource'
import { useApiClient } from '~/shared/api/useResource'
import {
  activeOutlineClasses,
  appSelectIconSize,
  appSelectSizeClasses,
  appSelectValueSizeClasses,
} from './types/control'

const props = withDefaults(defineProps<AppSelectProps<T>>(), {
  variant: 'outline',
  filter: true,
  size: 'md',
  hideDropdownIcon: undefined,
  locale: 'ru',

  itemDisabled: 'disabled',
  debounce: 300,
  pageSize: 30,
})

const emit = defineEmits<{
  itemPointerEnter: [item: T]
  itemPointerLeave: [item: T]
}>()
defineSlots<{
  item(props: { item: T; label: string; value: SelectValue; selected: boolean }): unknown
  selected(props: { item: T | undefined; label: string; value: SelectValue }): unknown
  selection(props: { selected: { item: T | undefined; label: string; value: SelectValue }[] }): unknown
  trigger(props: { selected: { item: T | undefined; label: string; value: SelectValue }[]; open: boolean }): unknown
  button(): unknown
  actions(): unknown
  footer(): unknown
  placeholder(): unknown
  empty(): unknown
}>()
const model = defineModel<any>()
const open = defineModel<boolean>('open', { default: false })
const { contentStyle: overlayStyle } = useOverlayStack(open)
const search = ref('')
const cache = shallowRef(new Map<SelectValue, T>())
const client = props.resource ? useApiClient() : null
const optionSource = computed<SelectSource<T> | undefined>(
  () => props.source ?? (props.resource && client ? resourceSource(props.resource, client) : undefined),
)
const trigger = ref<HTMLElement>()
const messages = computed(() =>
  props.locale === 'en'
    ? {
        placeholder: 'Select…',
        search: 'Search…',
        empty: 'No results',
        loading: 'Loading…',
        failed: 'Could not load options',
        retry: 'Retry',
        more: 'Load more',
        clear: 'Clear selection',
        remove: 'Remove',
      }
    : {
        placeholder: 'Выберите…',
        search: 'Поиск…',
        empty: 'Ничего не найдено',
        loading: 'Загрузка…',
        failed: 'Не удалось загрузить варианты',
        retry: 'Повторить',
        more: 'Загрузить ещё',
        clear: 'Очистить выбор',
        remove: 'Убрать',
      },
)
const valueAccessor = computed(
  () =>
    props.optionValue ??
    props.itemValue ??
    ((item: T) =>
      typeof item === 'object' && item !== null
        ? ((item as Record<string, any>).id ?? (item as Record<string, any>).value ?? JSON.stringify(item))
        : item),
)
const labelAccessor = computed(
  () =>
    props.optionLabel ??
    props.itemLabel ??
    ((item: T) =>
      typeof item === 'object' && item !== null ? String((item as Record<string, any>).name ?? '') : String(item)),
)
const key = (item: T) => valueOf(item, valueAccessor.value)
const label = (item: T) => String(readItem(item, labelAccessor.value) ?? '')
const itemDisabled = (item: T) => Boolean(readItem(item, props.itemDisabled))
const remember = (items: T[]) => {
  const copy = new Map(cache.value)
  items.forEach((item) => copy.set(key(item), item))
  cache.value = copy
}
watch(
  () => [
    props.options ?? props.items,
    props.selectedItems,
    props.itemValue,
    props.itemLabel,
    props.optionValue,
    props.optionLabel,
    model.value,
  ],
  () => {
    remember([
      ...(props.options ?? props.items ?? []),
      ...(props.selectedItems ?? []),
      ...(normalizeSelection(model.value).filter((value) => typeof value === 'object' && value !== null) as T[]),
    ])
  },
  { immediate: true, deep: true },
)
const source = useSelectSource(() => ({ ...props, source: optionSource.value }), open, search, key, remember)
const options = computed(() => {
  const items = optionSource.value ? source.items.value : (props.options ?? props.items ?? [])
  if ((optionSource.value && !props.onlyClientSearch) || props.filter === false) return items
  const query = search.value.trim().toLocaleLowerCase()
  return items.filter((item) =>
    (props.filterFields?.length
      ? props.filterFields.map((field) => String(readItem(item, field) ?? '')).join(' ')
      : label(item)
    )
      .toLocaleLowerCase()
      .includes(query),
  )
})
const selectedKeys = computed(() =>
  normalizeSelection(model.value).map((value) => selectionKey<T>(value, valueAccessor.value)),
)
const selected = computed(() =>
  selectedKeys.value.map((value) => ({
    value,
    item: cache.value.get(value),
    label: cache.value.has(value) ? label(cache.value.get(value)!) : String(value),
  })),
)
const busy = computed(() => source.loading.value || source.pending.value)
const showDropdownIcon = computed(
  () => props.hideDropdownIcon === false || (props.hideDropdownIcon === undefined && props.variant !== 'ghost'),
)
const setKeys = (value: unknown) => {
  if (props.disabled) return
  const keys = normalizeSelection(value) as SelectValue[]
  const values = keys
    .map((value) => (props.emitValue || props.optionValue ? value : cache.value.get(value)))
    .filter((value) => value !== undefined)
  model.value = props.multiple ? values : (values[0] ?? null)
}
const restoreFocusAfterRemoval = async () => {
  await nextTick()
  if (document.activeElement === document.body) trigger.value?.focus()
}
const remove = (value: SelectValue) => {
  setKeys(selectedKeys.value.filter((key) => key !== value))
  void restoreFocusAfterRemoval()
}
const clear = () => {
  setKeys([])
  void restoreFocusAfterRemoval()
}
watch(open, async (value) => {
  if (props.disabled && value) {
    open.value = false
    return
  }
  if (!value) {
    search.value = ''
    await nextTick()
    if (document.activeElement === document.body) trigger.value?.focus()
  }
})
watch(
  () => props.disabled,
  (value) => {
    if (value) open.value = false
  },
)
const onScroll = (event: Event) => {
  const el = event.target as HTMLElement
  if (el.scrollHeight - el.scrollTop - el.clientHeight < 64) source.loadMore()
}
const onTriggerKey = (event: KeyboardEvent) => {
  if (['ArrowDown', 'ArrowUp'].includes(event.key)) {
    event.preventDefault()
    open.value = true
  }
}
defineExpose({ open, focus: () => trigger.value?.focus() })
</script>
<template>
  <AppField
    :id="id"
    :label="props.label"
    :error="error"
    :hint="hint"
  >
    <template #default="field">
      <ComboboxRoot
        v-model:open="open"
        :model-value="multiple ? selectedKeys : selectedKeys[0]"
        :multiple="multiple"
        :disabled="disabled"
        :name="name"
        :required="required"
        ignore-filter
        :reset-search-term-on-select="false"
        :reset-search-term-on-blur="false"
        @update:model-value="setKeys"
      >
        <ComboboxAnchor as-child>
          <ComboboxTrigger
            v-if="$slots.button"
            as-child
            :disabled="disabled"
            @keydown="onTriggerKey"
          >
            <slot name="button" />
          </ComboboxTrigger>
          <div
            v-else
            data-app-select-trigger
            class="group/select relative flex min-w-0 items-center gap-1 transition-colors"
            :class="[
              appSelectSizeClasses[size],
              variant === 'ghost'
                ? 'group border border-transparent hover:bg-field-hover'
                : variant === 'secondary'
                  ? 'group border border-transparent bg-secondary text-secondary-foreground shadow-none hover:bg-accent'
                  : 'group border border-input bg-background shadow-sm hover:bg-field-hover',
              variant === 'active-outline' && activeOutlineClasses,
              error && 'border-destructive',
              disabled && 'opacity-50',
            ]"
          >
            <ComboboxTrigger as-child>
              <button
                :id="field.id"
                ref="trigger"
                type="button"
                tabindex="0"
                :disabled="disabled"
                :aria-label="ariaLabel || props.label || placeholder || messages.placeholder"
                :aria-describedby="[field.describedBy, `${field.id}-value`].filter(Boolean).join(' ')"
                :aria-invalid="Boolean(error) || undefined"
                :aria-required="required || undefined"
                class="absolute inset-0 w-full cursor-pointer rounded-[inherit] outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed"
                @keydown="onTriggerKey"
              />
            </ComboboxTrigger>
            <AppIcon
              v-if="icon && !$slots.trigger"
              :icon="icon"
              :size="appSelectIconSize[size]"
              :class="!selected.length && 'text-muted-foreground'"
              class="pointer-events-none relative z-10 text-current"
            />
            <div
              :id="`${field.id}-value`"
              data-avatar-owner
              class="pointer-events-none flex min-w-0 flex-1 flex-wrap items-center gap-1"
              :class="[appSelectValueSizeClasses[size], multiple && 'pr-1']"
              @click="!disabled && (open = !open)"
            >
              <slot
                v-if="$slots.trigger"
                name="trigger"
                :selected="selected"
                :open="open"
              />
              <slot
                v-else-if="selected.length && $slots.selection"
                name="selection"
                :selected="selected"
              />
              <template v-else-if="multiple && selected.length">
                <SelectChip
                  v-for="entry in selected"
                  :key="entry.value"
                  :label="entry.label"
                  :disabled="disabled"
                  :remove-label="messages.remove"
                  class="pointer-events-none"
                  @remove="remove(entry.value)"
                >
                  <slot
                    name="selected"
                    :item="entry.item"
                    :label="entry.label"
                    :value="entry.value"
                  >
                    {{ entry.label }}
                  </slot>
                </SelectChip>
              </template>
              <span
                v-else-if="selected.length"
                class="flex min-w-0 items-center truncate"
                ><slot
                  name="selected"
                  :item="selected[0]!.item"
                  :label="selected[0]!.label"
                  :value="selected[0]!.value"
                  >{{ selected[0]!.label }}</slot
                ></span
              >
              <span
                v-else
                class="truncate text-muted-foreground"
                ><slot name="placeholder">{{ placeholder || messages.placeholder }}</slot></span
              >
            </div>
            <AppClearButton
              v-if="(clearable || showClear) && selected.length && !disabled"
              :size="size"
              :active="variant === 'active-outline'"
              type="button"
              :label="messages.clear"
              :class="
                !clearInline
                  ? [
                      'pointer-events-none absolute right-1 opacity-0 transition-opacity group-focus-within/select:pointer-events-auto group-focus-within/select:opacity-100 group-hover/select:pointer-events-auto group-hover/select:opacity-100',
                    ]
                  : 'relative shrink-0'
              "
              @click.stop="clear"
            />
            <div
              v-if="$slots.actions"
              class="relative z-10 flex shrink-0 items-center"
              @click.stop
            >
              <slot name="actions" />
            </div>
            <AppIcon
              v-if="showDropdownIcon && !$slots.trigger"
              :icon="ChevronDown"
              :size="appSelectIconSize[size]"
              :class="!selected.length && 'text-muted-foreground'"
              class="pointer-events-none shrink-0 text-current"
              aria-hidden="true"
            />
          </div>
        </ComboboxAnchor>
        <ComboboxPortal>
          <ComboboxContent
            :style="overlayStyle"
            position="popper"
            align="start"
            :side-offset="5"
            :collision-padding="12"
            class="z-overlay flex max-h-[min(380px,var(--reka-combobox-content-available-height))] w-[max(240px,var(--reka-combobox-trigger-width))] max-w-[calc(100vw-24px)] flex-col overflow-hidden rounded-lg border border-border-strong bg-background text-foreground shadow-overlay"
            @escape-key-down.stop
          >
            <div
              v-if="filter !== false"
              class="flex shrink-0 items-center gap-2 border-b border-border px-3"
            >
              <Search
                class="size-4 text-muted-foreground"
                aria-hidden="true"
              /><ComboboxInput
                v-model="search"
                :display-value="() => ''"
                :aria-label="`${messages.search} ${props.label || ariaLabel || ''}`"
                :placeholder="messages.search"
                class="h-10 min-w-0 flex-1 bg-transparent text-sm outline-none placeholder:text-muted-foreground"
              />
            </div>
            <div
              class="min-h-0 overflow-y-auto overscroll-contain p-1.5"
              @scroll.passive="onScroll"
            >
              <ComboboxViewport
                :aria-label="props.label || ariaLabel || messages.placeholder"
                :aria-busy="busy"
              >
                <ComboboxItem
                  v-for="item in options"
                  :key="key(item)"
                  :value="key(item)"
                  :disabled="itemDisabled(item) || source.pending.value"
                  class="flex min-h-9 cursor-pointer items-center gap-2 rounded-md px-2 py-2 text-[13px] outline-none data-[disabled]:pointer-events-none data-[disabled]:opacity-40 data-[highlighted]:bg-accent"
                  @pointerenter="emit('itemPointerEnter', item)"
                  @pointerleave="emit('itemPointerLeave', item)"
                >
                  <span class="min-w-0 flex-1 truncate"
                    ><slot
                      name="item"
                      :item="item"
                      :label="label(item)"
                      :value="key(item)"
                      :selected="selectedKeys.includes(key(item))"
                      >{{ label(item) }}</slot
                    ></span
                  ><ComboboxItemIndicator>
                    <Check
                      class="size-4 shrink-0"
                      aria-hidden="true"
                    />
                  </ComboboxItemIndicator>
                </ComboboxItem>
              </ComboboxViewport>
              <AppLoadingIndicator
                v-if="busy"
                fluid
                size="md"
                class="p-4"
                :label="messages.loading"
              />
              <div
                v-else-if="source.error.value"
                role="alert"
                class="space-y-2 p-3 text-center text-xs text-muted-foreground"
              >
                <p>{{ messages.failed }}</p>
                <AppButton
                  variant="outline"
                  size="sm"
                  @click="source.retry"
                >
                  {{ messages.retry }}
                </AppButton>
              </div>
              <div
                v-else-if="!options.length"
                role="status"
                class="p-5 text-center text-xs text-muted-foreground"
              >
                <slot name="empty">{{ messages.empty }}</slot>
              </div>
              <AppButton
                v-else-if="source.hasMore.value"
                variant="ghost"
                size="sm"
                fluid
                class="mt-1 text-muted-foreground"
                @click="source.loadMore"
              >
                {{ messages.more }}
              </AppButton>
            </div>
            <div
              v-if="$slots.footer"
              class="shrink-0 border-t border-border p-3"
              @keydown="
                ($event) => {
                  if ($event.key !== 'Escape') $event.stopPropagation()
                }
              "
            >
              <slot name="footer" />
            </div>
          </ComboboxContent>
        </ComboboxPortal>
      </ComboboxRoot>
    </template>
  </AppField>
</template>
