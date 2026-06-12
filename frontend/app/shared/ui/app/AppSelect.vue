<template>
  <AppLabel :label="label">
    <Select
      v-bind="{ ...props, filterFields: undefined }"
      ref="selectRef"
      v-model="model"
      :options="selectData.items.value"
      :option-label="selectData.itemLabel"
      :option-value="selectData.itemValue"
      :filter="false"
      @before-show="show = true"
      @hide="show = false"
      @click="selectRef?.show()"
    >
      <template #header="headerSlotProps">
        <slot
          name="header"
          v-bind="headerSlotProps"
        />
        <div
          v-if="filter"
          class="px-2 pt-2"
        >
          <span class="pi pi-search" />
          <AppInput
            v-model="selectData.search.value"
            autofocus
            :loading="selectData.loadItemsState.loading.value"
            icon="lucide:search"
            placeholder="Поиск"
          />
        </div>
      </template>
      <template #clearicon>
        <div class="flex justify-center items-center">
          <Icon
            name="lucide:x"
            class="fg-tertiary"
            size="18"
            @click.stop="model = undefined"
          />
        </div>
      </template>
      <template #value="valueSlotProps">
        <slot
          name="value"
          :option="selectedOption"
          :label="selectData.getOptionLabel(selectedOption)"
          :placeholder="valueSlotProps.placeholder"
        >
          {{ selectData.getOptionLabel(selectedOption) || '&nbsp;' }}
        </slot>
      </template>
    </Select>
  </AppLabel>
</template>

<script setup generic="T extends any" lang="ts">
import type { SelectProps, SelectMethods } from 'primevue/select'
import type { UseSelectDataProps } from '../../composables/useSelectData'

export type CSelectProps<T> = Omit<SelectProps, 'filterFields' | 'options'> &
  UseSelectDataProps<T> & {
    label?: string
    class?: string
  }

const model = defineModel<T>()

const props = withDefaults(defineProps<CSelectProps<T>>(), {
  autoLoad: false,
  filter: true,
  fluid: true,
  highlightOnSelect: true,
  emptyMessage: 'Не найдено элементов',
  emptyFilterMessage: 'Не найдено элементов',
})

const show = ref(false)

const selectedOption = computed(() => {
  return selectData.getOptionByValue(model.value)
})

const selectRef = ref<SelectMethods>()
const optionsRef = toRef(props, 'options')

const selectData = useSelectData<T>({ ...props, options: optionsRef, show })
</script>
