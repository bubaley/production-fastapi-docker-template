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
      </div>
    </template>
  </Toast>
</template>

<script setup lang="ts"></script>
