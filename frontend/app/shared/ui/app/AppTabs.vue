<script setup lang="ts">
import { computed, inject, onMounted, watch, type Component } from 'vue'
import { routerKey } from 'vue-router'
import AppIcon from './AppIcon.vue'
import { Tabs, TabsList, TabsTrigger } from '~/shared/ui/shadcn/tabs'

export type AppTab = {
  label: string
  value: string
  icon?: Component
  disabled?: boolean
}

const props = withDefaults(
  defineProps<{
    tabs: AppTab[]
    queryKey?: string
    fluid?: boolean
    ariaLabel?: string
    variant?: 'segment'
    contentClass?: string
    size?: 'small' | 'large'
    selectClass?: string | string[] | Record<string, boolean>
  }>(),
  {
    ariaLabel: 'Разделы',
    variant: 'segment'
  }
)

const model = defineModel<string>({ required: true })
const tabModel = defineModel<AppTab | undefined>('tab')
watch(model, () => { tabModel.value = props.tabs.find(tab => tab.value === model.value) }, { immediate: true })
const router = inject(routerKey, undefined)
const activeTab = computed(() => props.tabs.find((tab) => tab.value === model.value))

const syncToUrl = (value: string) => {
  if (!props.queryKey || typeof window === 'undefined') return
  if (router) {
    const route = router.currentRoute.value
    if (route.query[props.queryKey] !== value) {
      void router.replace({ query: { ...route.query, [props.queryKey]: value } })
    }
    return
  }
  const url = new URL(window.location.href)
  url.searchParams.set(props.queryKey, value)
  window.history.replaceState(window.history.state, '', url)
}

onMounted(() => {
  if (!props.queryKey) return
  const value = new URL(window.location.href).searchParams.get(props.queryKey)
  if (value && props.tabs.some((tab) => tab.value === value && !tab.disabled)) model.value = value
  else syncToUrl(model.value)
})

watch(model, syncToUrl)
watch(
  () => props.queryKey && router?.currentRoute.value.query[props.queryKey],
  (value) => {
    if (typeof value === 'string' && props.tabs.some((tab) => tab.value === value && !tab.disabled)) {
      model.value = value
    }
  }
)
</script>

<template>
  <Tabs
    v-model="model"
    class="min-w-0"
  >
    <TabsList
      class="max-w-full justify-start overflow-x-auto"
      :aria-label="ariaLabel"
      :class="[fluid && 'flex w-full', selectClass]"
    >
      <TabsTrigger
        v-for="tab in tabs"
        :key="tab.value"
        :value="tab.value"
        :disabled="tab.disabled"
        class="text-[12px]"
        :class="[fluid ? 'flex-1' : 'shrink-0', !tab.disabled && 'cursor-pointer']"
      >
        <slot
          name="tab"
          :tab="tab"
          :active="tab.value === model"
        >
          <slot
            name="option"
            :option="tab"
          >
            <span class="inline-flex items-center gap-1.5">
              <AppIcon
                v-if="tab.icon"
                :icon="tab.icon"
                size="xs"
              />
              <span>{{ tab.label }}</span>
            </span>
          </slot>
        </slot>
      </TabsTrigger>
    </TabsList>
    <div
      v-if="$slots.default"
      :class="contentClass"
    >
      <slot
        :tab="activeTab"
        :value="model"
      />
    </div>
  </Tabs>
</template>
