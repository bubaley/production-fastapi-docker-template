<template>
  <AppLabel :label="label">
    <MultiSelect
      v-bind="{ ...props, filterFields: undefined }"
      ref="selectRef"
      v-model="model"
      :options="selectData.items.value"
      :option-label="selectData.itemLabel"
      :option-value="selectData.itemValue"
      :filter="false"
      :pt="{
        label: 'flex flex-wrap',
      }"
      @before-show="show = true"
      @hide="show = false"
      @click="selectRef?.show()"
    >
      <template
        v-if="filter"
        #header
      >
        <div class="px-2 pt-2">
          <AppInput
            v-model="selectData.search.value"
            autofocus
            is-search
            :loading="selectData.loadItemsState.loading.value"
            placeholder="Поиск"
          />
        </div>
      </template>
      <template #value>
        <div
          v-for="(el, index) in model"
          :key="index"
        >
          <Chip class="pr-2! gap-1.5!">
            <span class="line-clamp-1 text-ellipsis">{{
              selectData.getOptionLabel(selectData.getOptionByValue(el)) || '&nbsp;'
            }}</span>
            <Icon
              name="lucide:x"
              class="opacity-50 hover:opacity-80 transition-opacity"
              @click.stop="model?.splice(index, 1)"
            />
          </Chip>
        </div>
      </template>
    </MultiSelect>
  </AppLabel>
</template>

<script setup generic="T extends any" lang="ts">
import AppLabel from './AppLabel.vue'
import { ref } from 'vue'
import type { SelectMethods } from 'primevue/select'
import type { MultiSelectProps } from 'primevue'
import AppInput from './AppInput.vue'
import { useSelectData, type UseSelectDataProps } from '../../composables/useSelectData'

export type CMultiSelectProps<T> = Omit<MultiSelectProps, 'filterFields' | 'options'> &
  UseSelectDataProps<T> & {
    label?: string
    class?: string
  }

const props = withDefaults(defineProps<CMultiSelectProps<T>>(), {
  showToggleAll: false,
  autoLoad: false,
  filter: true,
  fluid: true,
  emptyMessage: 'Не найдено элементов',
  emptyFilterMessage: 'Не найдено элементов',
  display: 'chip',
})

const model = defineModel<T[]>()
const selectRef = ref<SelectMethods>()
const optionsRef = toRef(props, 'options')

const show = ref(false)

const selectData = useSelectData<T>({ ...props, options: optionsRef, show })
</script>
