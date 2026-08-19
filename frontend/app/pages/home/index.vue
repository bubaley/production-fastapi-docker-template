<template>
  <div>
    <AppSection
      title="Home"
      flat
      description="Welcome to the home page"
    >
      <div>
        <AppTemplateActions
          size="small"
          :actions="actions"
        />
      </div>
    </AppSection>
  </div>
</template>

<script setup lang="ts">
const actions = ref<AppTemplateAction[]>([
  {
    label: 'Settings',
    icon: 'lucide:settings',
    severity: 'secondary',
    onClick: () => navigateTo({ name: 'settings-profile' }),
  },
  {
    label: 'Switch organization',
    icon: 'lucide:building-2',
    severity: 'secondary',
    onClick: () => navigateTo({ name: 'home-setup' }),
  },
  {
    label: 'UI Kit',
    icon: 'lucide:palette',
    severity: 'secondary',
    onClick: () => navigateTo({ name: 'home-ui' }),
  },
])
</script>
