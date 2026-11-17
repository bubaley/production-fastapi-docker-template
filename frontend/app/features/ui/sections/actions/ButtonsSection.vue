<script setup lang="ts">
import { ArrowRight, Copy, ExternalLink, Plus } from '@lucide/vue'
import type { AppButtonVariant } from '~/shared/ui/app/appButton'
import type { AppControlSize } from '~/shared/ui/app/types/control'
import UiDemo from '../../components/UiDemo.vue'

const variants: AppButtonVariant[] = ['default', 'primary', 'secondary', 'outline', 'ghost', 'link', 'destructive']
const sizes: AppControlSize[] = ['xs', 'sm', 'md', 'lg']
const toast = useToast()
const wait = (): Promise<void> => new Promise((resolve) => setTimeout(resolve, 800))
</script>

<template>
  <UiDemo
    title="Variants and sizes"
    code='variant="default" size="md"'
    description="default is the main action of an area; primary is the colored accent for rare emphasis; secondary and outline sit next to it; ghost for toolbars; destructive only for the action itself, not for opening its confirmation."
  >
    <div class="overflow-x-auto">
      <table class="w-full min-w-[640px] border-separate border-spacing-y-2 text-left">
        <thead>
          <tr class="text-xs text-muted-foreground">
            <th class="w-28 font-normal">variant \ size</th>
            <th
              v-for="size in sizes"
              :key="size"
              class="font-normal"
            >
              {{ size }}
            </th>
            <th class="font-normal">icon-only</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="variant in variants"
            :key="variant"
          >
            <td class="text-xs text-muted-foreground">{{ variant }}</td>
            <td
              v-for="size in sizes"
              :key="size"
            >
              <AppButton
                :variant="variant"
                :size="size"
                label="Action"
                @click="toast.default(`${variant} / ${size}`)"
              />
            </td>
            <td>
              <AppButton
                :variant="variant"
                :icon="Plus"
                aria-label="Add"
              />
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </UiDemo>
  <UiDemo
    title="States"
    code="loading · disabled · icon-position · fluid"
    description="A pending action shows loading on the button itself; disabled keeps the tooltip and cursor."
  >
    <div class="flex flex-wrap items-center gap-3">
      <AppButton
        label="Loading"
        loading
      />
      <AppButton
        label="Disabled"
        disabled
      />
      <AppButton
        label="Icon end"
        variant="outline"
        :icon="ArrowRight"
        icon-position="end"
      />
      <AppButton
        label="Fluid"
        variant="secondary"
        fluid
        class="sm:w-48"
      />
    </div>
  </UiDemo>
  <UiDemo
    title="Text variant"
    code='text-variant="base | muted"'
    description="muted keeps the label quiet until hover or keyboard focus — for secondary toolbar buttons."
  >
    <div class="flex flex-wrap items-center gap-3">
      <AppButton
        label="Base text"
        variant="outline"
      />
      <AppButton
        label="Muted text"
        variant="outline"
        text-variant="muted"
      />
      <AppButton
        label="Muted ghost"
        variant="ghost"
        text-variant="muted"
      />
    </div>
  </UiDemo>
  <UiDemo
    title="Links"
    code='href="/ui/colors" · external'
    description="With href the button renders NuxtLink; external opens a new tab."
  >
    <div class="flex flex-wrap items-center gap-3">
      <AppButton
        label="href (NuxtLink)"
        variant="outline"
        href="/ui/colors"
      />
      <AppButton
        label="external"
        variant="ghost"
        :icon="ExternalLink"
        icon-position="end"
        href="https://nuxt.com"
        external
      />
    </div>
  </UiDemo>
  <UiDemo
    title="Text button"
    code='AppTextButton tone="primary" copied'
    description="An inline action inside text or a value: open, copy, change."
  >
    <div class="flex flex-wrap items-center gap-6 text-sm">
      <AppTextButton
        label="Open settings"
        to="/ui/settings-rows"
      />
      <AppTextButton
        label="PRJ-001"
        :icon="Copy"
        tone="neutral"
        copied
        value="PRJ-001"
      />
      <AppTextButton
        label="Remove"
        tone="destructive"
        @click="toast.default('Remove requested')"
      />
    </div>
  </UiDemo>
  <UiDemo
    title="Row of actions"
    code=':actions="[…]"'
    description="AppTemplateActions renders two or more buttons with per-button loading and an optional success toast."
  >
    <AppTemplateActions
      :actions="[
        { label: 'Save', action: wait, successNotification: 'Saved' },
        { label: 'Save as draft', variant: 'outline', action: () => void toast.default('Draft saved') },
        { label: 'Cancel', variant: 'ghost', action: () => void toast.default('Cancelled') },
      ]"
    />
  </UiDemo>
  <UiDemo
    title="Theme toggle"
    code="AppThemeToggle"
    description="Switches light and dark; the full theme and palette switcher is in the catalogue sidebar."
  >
    <AppThemeToggle />
  </UiDemo>
</template>
