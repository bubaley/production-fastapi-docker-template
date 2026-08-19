<template>
  <UiShowcaseSection
    title="AppBlock & AppTitle"
    description="Surface containers and typography used to compose page sections."
  >
    <UiShowcaseItem label="AppTitle sizes">
      <div class="flex w-full flex-col gap-3">
        <AppTitle
          v-for="item in titles"
          :key="item.size"
          :size="item.size"
          :title="`Size ${item.size}`"
          :subtitle="item.subtitle"
        />
      </div>
    </UiShowcaseItem>

    <UiShowcaseItem
      label="AppBlock variants"
      caption="outlined / ghost / ghost-outlined / filled"
    >
      <AppBlock
        v-for="item in blocks"
        :key="item.variant"
        :variant="item.variant"
        :icon="item.icon"
        :color="item.color"
        size="lg"
        class="px-3"
      >
        {{ item.text }}
      </AppBlock>
    </UiShowcaseItem>

    <UiShowcaseItem label="AppAvatar">
      <AppAvatar
        v-for="item in avatars"
        :key="item.name"
        v-bind="item"
      />
    </UiShowcaseItem>
  </UiShowcaseSection>
</template>

<script setup lang="ts">
import type { AppAvatarProps } from '~/shared/ui/app/AppAvatar.vue'
import type { BlockVariantToken, ColorToken, TitleSizeToken } from '~/shared/ui/template/types/template-ui-tokens'
import UiShowcaseItem from './UiShowcaseItem.vue'
import UiShowcaseSection from './UiShowcaseSection.vue'

const titles: { size: TitleSizeToken; subtitle: string }[] = [
  { size: 'sm', subtitle: 'medium weight' },
  { size: 'md', subtitle: 'semibold weight' },
  { size: 'lg', subtitle: 'bold weight' },
  { size: 'xl', subtitle: 'bold weight' },
]

const blocks: { variant: BlockVariantToken; icon: string; color: ColorToken; text: string }[] = [
  { variant: 'outlined', icon: 'lucide:home', color: 'primary', text: 'Outlined' },
  { variant: 'ghost', icon: 'lucide:home', color: 'primary', text: 'Ghost' },
  { variant: 'ghost-outlined', icon: 'lucide:info', color: 'orange', text: 'Ghost outlined' },
  { variant: 'filled', icon: 'lucide:check-circle', color: 'pink', text: 'Filled' },
]

const avatars: AppAvatarProps[] = [
  { name: 'Ada Lovelace' },
  { name: 'Grace Hopper', size: 'large' },
  { name: 'Alan Turing', size: 'xlarge', color: '#6366f1' },
]
</script>
