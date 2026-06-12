<template>
  <AppListTemplate
    title="Организации"
    detail-route-name="settings-organizations-id"
    :repo="useRepo('organization')"
    description="Управление организациями"
  >
    <Column
      field="name"
      header="Наименование"
    />
    <Column
      field="key"
      header="Ключ"
    />
  </AppListTemplate>
</template>

<script setup lang="ts"></script>

<style scoped lang="scss"></style>
