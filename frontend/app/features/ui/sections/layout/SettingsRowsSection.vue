<script setup lang="ts">
import UiDemo from '../../components/UiDemo.vue'

const notifications = ref(true)
</script>

<template>
  <UiDemo
    title="Settings rows"
    code='AppSettingRow label description for-id · stacked · tone="destructive"'
    description="Label and description on the left, the control on the right; stacked below on phones."
  >
    <div class="max-w-2xl">
      <AppSettingRow
        label="Email notifications"
        description="Control on the right, stacked below on phones"
        for-id="ui-setting-notifications"
      >
        <AppSwitch
          id="ui-setting-notifications"
          v-model="notifications"
        />
      </AppSettingRow>
      <AppSettingRow
        label="Webhook URL"
        description="stacked: full-width control"
        for-id="ui-setting-webhook"
        stacked
      >
        <AppInput
          id="ui-setting-webhook"
          model-value="https://example.com/hooks/events"
          fluid
        />
      </AppSettingRow>
      <AppSettingRow
        label="Delete organization"
        description="tone destructive"
        tone="destructive"
      >
        <AppButton
          variant="outline"
          label="Delete"
        />
      </AppSettingRow>
    </div>
  </UiDemo>
  <UiDemo
    title="Scroll area"
    code='AppScrollArea class="h-40"'
    description="A bounded region with thin, theme-colored scrollbars."
    bare
  >
    <AppCard padding="none">
      <AppScrollArea class="h-40">
        <div class="space-y-2 p-4">
          <p
            v-for="row in 12"
            :key="row"
            class="text-sm"
          >
            Row {{ row }} of a long list
          </p>
        </div>
      </AppScrollArea>
    </AppCard>
  </UiDemo>
</template>
