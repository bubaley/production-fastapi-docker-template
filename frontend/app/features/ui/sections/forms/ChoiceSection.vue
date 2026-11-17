<script setup lang="ts">
import UiDemo from '../../components/UiDemo.vue'

const checked = ref(true)
const channels = ref<string[]>(['email'])
const enabled = ref(true)
const off = ref(false)
const priority = ref('normal')
</script>

<template>
  <UiDemo
    title="Checkbox"
    code='v-model · val="email" · indeterminate'
    description="A boolean model or an array model with val."
  >
    <div class="flex flex-col items-start gap-3">
      <AppCheckbox
        v-model="checked"
        label="Receive notifications"
      />
      <AppCheckbox
        v-model="channels"
        val="email"
        label="Email (array model)"
      />
      <AppCheckbox
        v-model="channels"
        val="sms"
        label="SMS (array model)"
      />
      <AppCheckbox
        :model-value="false"
        indeterminate
        label="Indeterminate"
      />
      <AppCheckbox
        :model-value="true"
        disabled
        label="Disabled"
      />
    </div>
  </UiDemo>
  <UiDemo
    title="Switch"
    code='variant="default | contrast"'
    description="Applies immediately. Off is a light knob on a muted track."
  >
    <div class="flex flex-col gap-3">
      <label class="flex items-center gap-2 text-sm"
        ><AppSwitch
          v-model="enabled"
          aria-label="Project is active"
        />Project is active</label
      >
      <label class="flex items-center gap-2 text-sm"
        ><AppSwitch
          v-model="enabled"
          variant="contrast"
          aria-label="Contrast variant"
        />Contrast variant</label
      >
      <label class="flex items-center gap-2 text-sm"
        ><AppSwitch
          v-model="off"
          aria-label="Off by default"
        />{{ off ? 'On' : 'Off' }}</label
      >
      <label class="flex items-center gap-2 text-sm text-muted-foreground"
        ><AppSwitch
          :model-value="false"
          disabled
          aria-label="Disabled"
        />Disabled</label
      >
    </div>
  </UiDemo>
  <UiDemo
    title="Radio group"
    code=':items="[{ label, value, disabled }]"'
  >
    <AppRadioGroup
      v-model="priority"
      aria-label="Priority"
      :items="[
        { label: 'Normal', value: 'normal' },
        { label: 'High', value: 'high' },
        { label: 'Disabled', value: 'none', disabled: true },
      ]"
    />
  </UiDemo>
</template>
