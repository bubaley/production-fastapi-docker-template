<template>
  <AppPageView
    title="Главная"
    description="Организации, настройки и возможности шаблона страницы"
  >
    <template #title>Главная</template>
    <template #prefix>
      <AppIcon
        :icon="House"
        tone="muted"
      />
    </template>
    <template #actions>
      <AppTemplateActions
        class="flex-wrap justify-end"
        size="sm"
        :actions="actions"
      />
    </template>
    <template #subheader>
      <div class="flex flex-wrap items-center justify-between gap-2 pb-3">
        <span class="text-sm text-muted-foreground">Зона под шапкой: контекст и навигация</span>
        <AppTextButton
          label="Открыть организации"
          @click="navigateTo({ name: 'settings-organizations' })"
        />
      </div>
    </template>
    <template #controls>
      <div class="flex flex-wrap items-center justify-between gap-3 py-3">
        <AppInput
          v-model="search"
          :icon="Search"
          placeholder="Найти возможность страницы"
          class="w-full sm:max-w-xs"
        />
        <label class="flex items-center gap-2 text-sm"
          ><AppSwitch
            v-model="showExamples"
            aria-label="Показать примеры"
          />Показать примеры</label
        >
      </div>
    </template>

    <div class="flex flex-col gap-6">
      <AppSection
        title="Как устроена страница"
        description="Шапка, обе панели и нижняя зона остаются на месте. Прокручивается только содержимое между ними."
      >
        <div
          v-if="visibleFeatures.length"
          class="grid gap-4 md:grid-cols-2"
        >
          <AppCard
            v-for="feature in visibleFeatures"
            :key="feature.title"
          >
            <AppSection
              :title="feature.title"
              :description="feature.description"
              title-size="md"
            >
              <p
                v-if="showExamples"
                class="text-sm text-muted-foreground"
              >
                {{ feature.example }}
              </p>
            </AppSection>
          </AppCard>
        </div>
        <p
          v-else
          class="py-6 text-sm text-muted-foreground"
        >
          Ничего не найдено
        </p>
      </AppSection>
      <AppSection
        v-if="showExamples"
        title="Проверка прокрутки"
        description="Прокрутите примеры вниз: действия в шапке, поиск и нижняя панель останутся доступными."
      >
        <AppCard
          v-for="index in 8"
          :key="index"
          variant="muted"
        >
          <p class="font-medium">Пример содержимого {{ index }}</p>
          <p class="mt-2 text-sm text-muted-foreground">
            Здесь могут находиться списки, формы, карточки и другие разделы приложения.
          </p>
        </AppCard>
      </AppSection>
    </div>

    <template #footer>
      <div class="flex flex-wrap items-center justify-between gap-2 text-sm text-muted-foreground">
        <span>Нижняя зона страницы · Найдено возможностей: {{ visibleFeatures.length }}</span>
        <AppTextButton
          label="Сбросить пример"
          @click="resetExample"
        />
      </div>
    </template>
  </AppPageView>
</template>

<script setup lang="ts">
import { Building2, House, Palette, Search, Settings } from '@lucide/vue'
const search = ref('')
const showExamples = ref(true)
const resetExample = () => {
  search.value = ''
  showExamples.value = true
}
const features = [
  {
    title: 'Шапка и заголовок',
    description: 'Единый заголовок страницы с описанием и иконкой.',
    example:
      'Слоты prefix, title и title-append дополняют заголовок. Слот header заменяет шапку целиком; backAction добавляет возврат.',
  },
  {
    title: 'Действия страницы',
    description: 'Основные действия доступны справа в шапке.',
    example: 'Слот actions содержит переходы в настройки, смену организации и каталог компонентов.',
  },
  {
    title: 'Панель под шапкой',
    description: 'Контекст и дополнительная навигация располагаются перед разделителем.',
    example: 'Слот subheader показывает ссылку на организации. Прежнее имя subtitle тоже поддерживается.',
  },
  {
    title: 'Панель под разделителем',
    description: 'Поиск, фильтры и переключатели находятся над прокручиваемым содержимым.',
    example: 'Слот controls содержит работающий поиск по возможностям и переключатель примеров.',
  },
  {
    title: 'Основное содержимое',
    description: 'Списки, формы и карточки прокручиваются внутри страницы.',
    example: 'Основной слот default принимает любые разделы. contentClass позволяет настроить отступы.',
  },
  {
    title: 'Нижняя зона',
    description: 'Итоги и дополнительные действия доступны внизу страницы.',
    example: 'Слот footer показывает число найденных возможностей и действие сброса.',
  },
]
const visibleFeatures = computed(() => {
  const term = search.value.trim().toLocaleLowerCase('ru')
  return features.filter((feature) =>
    `${feature.title} ${feature.description} ${feature.example}`.toLocaleLowerCase('ru').includes(term),
  )
})
const actions: AppTemplateAction[] = [
  {
    label: 'Настройки',
    icon: Settings,
    variant: 'secondary',
    action: async () => {
      await navigateTo({ name: 'settings-profile' })
    },
  },
  {
    label: 'Сменить организацию',
    icon: Building2,
    variant: 'outline',
    action: async () => {
      await navigateTo({ name: 'home-setup' })
    },
  },
  {
    label: 'Компоненты интерфейса',
    icon: Palette,
    variant: 'outline',
    action: async () => {
      await navigateTo({ name: 'ui' })
    },
  },
]
</script>
