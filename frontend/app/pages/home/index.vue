<template>
  <div class="flex flex-col gap-4 max-w-2xl">
    <AppSection
      flat
      title="Здравствуй человек!"
      description="FastAPI + Nuxt шаблон для быстрого старта проекта"
    >
      <AppBlock
        color="info"
        class="py-3 px-5"
      >
        Здесь находится шаблон. Если вы начинаете новый проект с него, вам не нужно изобретать велосипед заново.
        Возьмите scaffold, добавьте свои специфические детали — и вы сделали. Это экономит много времени.
      </AppBlock>
      <div class="flex flex-wrap gap-3">
        <AppButton
          label="Настройки"
          icon="lucide:settings"
          @click="navigateTo({ name: 'settings-organizations' })"
        />
        <AppButton
          label="Переключить организацию"
          severity="secondary"
          icon="lucide:building-2"
          @click="navigateTo({ name: 'home-setup' })"
        />
      </div>
    </AppSection>
  </div>
</template>

<script setup lang="ts"></script>
