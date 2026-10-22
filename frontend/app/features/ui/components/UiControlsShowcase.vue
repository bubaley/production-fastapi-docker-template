<script setup lang="ts">
import type { AppButtonProps } from '~/shared/ui/app/AppButton.vue'
import type { AppControlSize } from '~/shared/ui/app/types/control'
const variants: { label: string; variant: AppButtonProps['variant'] }[] = [
  { label: 'default', variant: 'default' },
  { label: 'Primary', variant: 'primary' },
  { label: 'outline', variant: 'outline' },
  { label: 'secondary', variant: 'secondary' },
  { label: 'ghost', variant: 'ghost' },
  { label: 'destructive', variant: 'destructive' },
]
const sizes: AppControlSize[] = ['xs', 'sm', 'default', 'lg']
const toast = useToast()
</script>
<template>
  <AppSection
    title="Buttons and actions"
    description="Consistent size props across buttons, inputs and selects."
  >
    <AppCard>
      <p class="mb-5 text-sm text-muted-foreground">
        Default: main action (save, create, continue). Secondary: supporting action (cancel, back). Outline: toolbar
        actions (filters, export, columns). Ghost: compact row and menu actions. Destructive: destructive confirmation.
        Primary: brand-colored emphasis. Accent is reserved for hover and active surfaces.
      </p>
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="item in variants"
          :key="item.label"
          class="flex items-center justify-between gap-3"
        >
          <span class="text-xs text-muted-foreground">{{ item.label }}</span>
          <AppButton
            :variant="item.variant"
            label="Action"
            @click="toast.default('Action completed')"
          />
        </div>
      </div>
      <div class="mt-5 border-t border-border pt-5">
        <p class="mb-3 text-sm text-muted-foreground">
          Цвет текста кнопки: base сохраняет цвет варианта, muted становится обычным при наведении.
        </p>
        <AppTemplateActions
          :actions="[
            { label: 'Обычный текст', variant: 'outline', textVariant: 'base' },
            { label: 'Приглушённый текст', variant: 'outline', textVariant: 'muted' },
          ]"
        />
      </div>
      <div class="mt-5 flex flex-wrap items-center gap-3 border-t border-border pt-5">
        <AppButton
          v-for="size in sizes"
          :key="size"
          :size="size"
          variant="outline"
          :label="size"
        />
        <AppButton
          icon="lucide:plus"
          variant="outline"
          aria-label="Add"
        />
        <AppButton
          label="Loading"
          loading
        />
        <AppButton
          label="Disabled"
          disabled
        />
      </div>
    </AppCard>
  </AppSection>
</template>
