<script setup lang="ts">
import { Mail } from '@lucide/vue'
import type { AppControlSize } from '~/shared/ui/app/types/control'
import UiDemo from '../../components/UiDemo.vue'
import { uiPeople } from '../../composables/useUiPeople'

const sizes: AppControlSize[] = ['xs', 'sm', 'md', 'lg']
const name = ref('New project')
const notes = ref('Build the first workflow and verify the interface.')
const quantity = ref<number | null>(8)
const member = ref<string | null>('anna')
const enabled = ref(true)
const focusName = ref('')
const focusNotes = ref('')
</script>

<template>
  <UiDemo
    title="Text fields"
    code="label · hint · error · clearable · loading · disabled"
    description="A short label above, a hint or an error below. Placeholders show an example, never the label."
  >
    <div class="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
      <AppInput
        v-model="name"
        label="Name"
        clearable
        hint="A short, clear name"
      />
      <AppInput
        label="Search"
        placeholder="Find a project"
        is-search
        clearable
      />
      <AppInput
        label="Invalid"
        error="Name is required"
        placeholder="Enter a name"
      />
      <AppInput
        label="Loading"
        model-value="Checking…"
        loading
      />
      <AppInput
        label="With icon"
        :icon="Mail"
        placeholder="name@company.com"
      />
      <AppInput
        label="Disabled"
        model-value="Read only"
        disabled
      />
    </div>
  </UiDemo>
  <UiDemo
    title="Number and multi-line"
    code="AppNumberInput :min :max · AppTextarea :rows"
  >
    <div class="grid gap-5 md:grid-cols-3">
      <AppNumberInput
        v-model="quantity"
        label="Quantity"
        :min="0"
        :max="100"
      />
      <AppTextarea
        v-model="notes"
        label="Description"
        :rows="3"
      />
      <AppTextarea
        label="Invalid textarea"
        error="Too short"
        :rows="3"
      />
    </div>
  </UiDemo>
  <UiDemo
    title="Control sizes"
    code='size="xs | sm | md | lg"'
    description="Inputs, selects, buttons and switches of one size line up in a row."
  >
    <div class="flex flex-col gap-3">
      <div
        v-for="size in sizes"
        :key="size"
        class="grid items-center gap-3 sm:grid-cols-[3rem_1fr_1fr_auto_auto]"
      >
        <span class="text-xs text-muted-foreground">{{ size }}</span>
        <AppInput
          :size="size"
          placeholder="Input"
          aria-label="Input"
        />
        <AppSelect
          v-model="member"
          :size="size"
          :items="uiPeople"
          item-label="name"
          item-value="id"
          emit-value
          aria-label="Select"
        />
        <AppButton
          :size="size"
          label="Button"
          variant="outline"
        />
        <AppSwitch
          v-model="enabled"
          :size="size"
          aria-label="Switch"
        />
      </div>
    </div>
  </UiDemo>
  <UiDemo
    title="Keyboard focus and width"
    code="fluid"
    description="Press Tab: Input, Select and Textarea share one focus ring (ring border + 2px ring/30). fluid fills the container."
  >
    <div class="flex flex-col gap-5">
      <div class="grid gap-5 md:grid-cols-3">
        <AppInput
          v-model="focusName"
          label="Input"
          placeholder="Tab here"
        />
        <AppSelect
          v-model="member"
          label="Select"
          :items="uiPeople"
          item-label="name"
          item-value="id"
          emit-value
        />
        <AppTextarea
          v-model="focusNotes"
          label="Textarea"
          placeholder="Then here"
          :rows="1"
        />
      </div>
      <div class="flex flex-col items-start gap-3 border-t border-border pt-5">
        <AppInput
          label="Default width"
          placeholder="Natural width"
        />
        <AppInput
          label="fluid"
          placeholder="Fills the container"
          fluid
        />
      </div>
    </div>
  </UiDemo>
</template>
