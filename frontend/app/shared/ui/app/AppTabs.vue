<template>
  <div class="app-tabs flex flex-col gap-md">
    <SelectButton
      v-model="model"
      :options="tabs"
      option-label="label"
      option-value="value"
      :fluid="fluid"
      class="no-wrap text-nowrap"
      :allow-empty="false"
      :size="size"
      :class="selectClass"
    >
      <template
        v-if="$slots.option"
        #option="slotProps"
      >
        <slot
          name="option"
          v-bind="slotProps"
        />
      </template>
    </SelectButton>
    <div v-if="_ready && hasActiveTabPanel()">
      <slot
        :tab="activeTab"
        :value="model"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, provide, ref, useSlots, watch, type VNode } from 'vue'

export type AppTab = { label: string; value: string }

const props = withDefaults(
  defineProps<{
    tabs: AppTab[]
    queryKey?: string
    fluid?: boolean
    size?: 'small' | 'large'
    selectClass?: string | string[] | Record<string, boolean>
  }>(),
  {
    queryKey: undefined,
    fluid: false,
    size: undefined,
    selectClass: undefined,
  },
)

const model = defineModel<string>({ required: true })

provide('app-tab-active', model)

const tabModel = defineModel<AppTab | undefined>('tab')
const slots = useSlots()

const _ready = ref(false)

const activeTab = computed(() => props.tabs.find((t) => t.value === model.value))

const isAppTabPanel = (node: VNode) => {
  if (typeof node.type !== 'object') return false
  const component = node.type as { name?: string; __name?: string }
  return component.name === 'AppTabPanel' || component.__name === 'AppTabPanel'
}

const getTabPanelValue = (node: VNode) => {
  return node.props?.tabValue || node.props?.['tab-value']
}

const hasActiveTabPanelNode = (node: VNode): boolean => {
  if (isAppTabPanel(node) && getTabPanelValue(node) === model.value) return true
  if (!Array.isArray(node.children)) return false
  return node.children.some((child) => hasActiveTabPanelNode(child as VNode))
}

const hasActiveTabPanel = () => {
  const nodes = slots.default?.({ tab: activeTab.value, value: model.value }) || []
  return nodes.some(hasActiveTabPanelNode)
}

function syncToUrl(val: string | undefined) {
  if (!props.queryKey || val === undefined || val === '') return
  const url = new URL(window.location.href)
  url.searchParams.set(props.queryKey, val)
  history.replaceState(history.state, '', url.toString())
}

function syncTabObject(val: string | undefined) {
  if (val === undefined) return
  tabModel.value = props.tabs.find((t) => t.value === val)
}

function removeQueryParam() {
  if (!props.queryKey) return
  const url = new URL(window.location.href)
  if (!url.searchParams.has(props.queryKey)) return
  url.searchParams.delete(props.queryKey)
  history.replaceState(history.state, '', url.toString())
}

onMounted(() => {
  if (props.queryKey) {
    const urlVal = new URL(window.location.href).searchParams.get(props.queryKey)
    const tab = urlVal ? props.tabs.find((t) => t.value === urlVal) : undefined
    if (urlVal && tab) model.value = urlVal
    else syncToUrl(model.value)
  }
  syncTabObject(model.value)
  _ready.value = true
})

watch(model, (val) => {
  syncToUrl(val)
  syncTabObject(val)
})

onUnmounted(() => {
  removeQueryParam()
})
</script>
