<template>
  <Toast ref="toastRef">
    <template #container="{ message }">
      <div class="relative">
        <div class="pr-10 pt-2 pb-2 px-3">
          <div>
            {{ message.summary }}
          </div>
          <div class="text-sm opacity-70 mt-0.5">{{ message.detail }}</div>
        </div>
        <Button
          :severity="message.severity"
          size="small"
          variant="text"
          rounded
          class="!absolute !top-1 !right-0.5"
          :pt="{
            root: '!p-0 !h-[28px] !w-[28px]',
            icon: '!text-sm opacity-80',
          }"
          icon="pi pi-times"
          @click="notify.remove(message)"
        />
      </div>
    </template>
  </Toast>
</template>

<script setup lang="ts">
const { notify } = useNotify()
</script>
