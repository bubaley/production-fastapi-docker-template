# План перехода с PrimeVue на shadcn-vue

Статус: реализация утверждена и выполнена; результаты проверки ниже. Дата: 2026-09-27.

Архивный документ. Действующие правила UI — в [frontend-concept.md](../frontend-concept.md).

## Цель и границы

Сохранить быстрый запуск новых проектов, Nuxt, feature/repo/codec архитектуру,
AppListTemplate, AppDetailTemplate и сценарии из product.md. Перенести из локального
Tasker универсальный UI, размеры, типографику и поведение на shadcn-vue/Reka UI.
Источник: `/Users/bubaley/dev/projects/tasker/tasker.frontend/src/shared/ui/`.
Состав фиксируется по текущим исходникам Tasker, а не по старым описаниям.

AppPageView реализован как единая композиция AppPage и PageHeader на основе
каркаса Tasker: компонент с точным именем AppPageView в локальном источнике не найден.
Сохранены repo + codec, list/detail templates и декларативный AppColumn.
AppBlock удалён: AppSection задаёт структуру, AppCard — визуальное выделение.
Публичный API окон называется Modal, уведомления используют useToast/ toast.default.
Перенесён универсальный конструктор фильтров с добавлением условия через «+».

Ниже сохранён исходный аудит и порядок миграции; актуальные контракты описаны
в frontend-concept.md, архитектура — в architecture.md.

## Что обнаружено

- PrimeVue используется в App-компонентах, Nuxt auto-import, CSS, типах и напрямую
  в feature-компонентах. Удаления импортов недостаточно: есть `<Column>`,
  `<DataTable>`, `<Toast>` и useToast от PrimeVue.
- AppColumn наследует ColumnProps PrimeVue; AppList разбирает VNode колонок.
  Tasker AppTable принимает columns и cell-слоты. Это разные контракты.
- Tasker AppSelect объединяет single/multiple, field/inline, локальный и remote
  поиск; его источник хранит локальные результаты, отбрасывает устаревшие ответы,
  поддерживает повтор запроса и догрузку.
- SelectRepo Tasker использует dontSetToItems/page/pageSize. Шаблон использует
  storeInRepo/pagination, а list может вернуть undefined. Нужна явная адаптация.
- AppListTemplate берёт pagination/loading из общего repo, хотя результаты могут
  быть локальными. Проверить одновременную работу списка и picker на одном repo.
- Tasker — Vite SPA, шаблон — Nuxt. Потребуется адаптация alias src, импортов,
  регистрации компонентов, browser-only кода, темы и SSR/hydration.
- В Tasker документация и код не везде буквально совпадают: PageHeader сейчас
  использует text-lg, AppTable — 13px/12px. За визуальный эталон брать реальные
  компоненты и каталог, затем закрепить измеренные значения в общих токенах.

## Карта переноса

| Источник в Tasker | Использование в шаблоне | Способ переноса |
|---|---|---|
| shadcn/*, cn, types/control.ts, CSS tokens | Основа всех App-компонентов | Перенос нужных примитивов и зависимостей; единые размеры, радиусы, focus и цвета |
| AppButton, AppIcon | Все действия, загрузка, иконки | Адаптация текущих action-контрактов и строковых иконок; один публичный AppIcon |
| AppField, AppInput, AppTextarea, AppNumberInput | Формы входа, профиля, организаций, пользователей; числовые поля новых проектов | Постоянные label/hint/error, доступные связи; замена AppFloatLabel |
| AppCheckbox, AppSwitch, AppRadio | Булевы поля, настройки, взаимоисключающий выбор | Убрать прямой PrimeVue Checkbox из UserDetailView |
| AppSelect + select/*, AppClearButton | Организации, пользователи, фильтры; single/multiple | Адаптер repo; AppMultiSelect свести к тому же движку |
| AppDatePicker + date-picker/*, AppCalendar, AppDateRangePicker, AppDateRangeFilter | Даты, дата-время, диапазоны и фильтры | Единый механизм вместо текущих DatePicker/SmartDatePicker; сохранить полезные быстрые варианты |
| AppDateLabel, AppDateRangeLabel | Даты в строках, карточках, выбранных диапазонах | Согласовать string/Date, null и часовые пояса |
| AppMenu, AppModal, AppDrawer, useOverlayStack | Меню действий, формы, вложенные popover, мобильные панели | Перенести стек, focus, Escape и возврат фокуса; согласовать props/слоты |
| AppConfirmDialog, AppUnsavedChangesDialog | Удаление, отказ от несохранённой формы | Использовать внутри текущего AppConfirmModal/DetailTemplate; без второго стека диалогов |
| AppTable | Табличный режим AppListTemplate, участники, токены | Renderer под текущим AppList; собственный типизированный AppColumn с field/header/format/body |
| AppPaginationControl, AppInfiniteScroll, AppLoadingIndicator, AppEmptyData | Страницы и догрузка списков, ожидание и пустые выборки | Сохранить API пагинации шаблона; заголовки таблицы видны во всех состояниях |
| AppTabs | Вкладки страниц и карточек | Сохранить query-key и AppTabPanel API шаблона |
| AppDataLabel, AppTitle, AppCard, AppListHeading | Метки значений, карточки, заголовки групп | Адаптировать существующие LabelConfig; AppSection для структуры, AppCard для оформления |
| AppSettingRow, AppSettingsPage, AppSettingsSection | Настройки профиля и организаций | Перенести общую композицию, без preferences API Tasker |
| AppToaster + toast helper | Успех/ошибки операций | Sonner через useToast и useActionState; убрать PrimeVue ToastService |
| AppPage, AppLayout, PageHeader, PageBackButton, AppWorkspaceTemplate | Каркас страницы, один заголовок, toolbar, footer и управляемый scroll | Основа обязательного переноса AppPageView после уточнения; вложенным секциям не добавлять h1 и второй scroll |
| AppColorPicker, AppAppearancePicker, AppEmojiPicker | Универсальные поля цвета и оформления | Предлагаются в полном наборе; ленивые тяжёлые части и рабочие примеры в каталоге |
| AppCircularProgress, AppLightbox | Прогресс и просмотр изображений | Перенос/сведение с существующим lightbox, без второй параллельной реализации |

AppAvatar и другие уже полезные компоненты шаблона остаются, с новыми токенами.
AppListTemplate, AppDetailTemplate, AppDetailActions, AppTemplateActions,
useActionState и repo toolkit остаются владельцами своих сценариев.

## Архитектура результата

`shared/ui/shadcn` → `shared/ui/app` → `shared/ui/template` → `features`.

Примитивы не знают репозиториев и маршрутов. Features используют App API.
AppListTemplate управляет CRUD/поиском/пагинацией; AppTable только отображает.
AppColumn сохраняет удобное описание колонок без наследования PrimeVue типов.
Каркас страницы отвечает за геометрию; вложенные list/detail остаются секциями.

Улучшения в рамках переноса:

- Один источник размеров button/input/select, единственная система семантических цветов.
- Single/multiple select на одном движке; выбранная подпись сохраняется вне текущей страницы результатов.
- Изолированные результаты, loading/error/pagination у независимых запросов;
  защита от гонок при поиске и смене организации. Расширять имеющийся toolkit.
- Таблица сохраняет шапку при loading/empty/error; действия внутри строки
  не открывают карточку; горизонтальный overflow локализован.
- Один заголовок страницы; корректная высота и scroll при вложенных шаблонах.
- Внятные состояния ошибок, клавиатурная навигация, aria и возврат фокуса.

Не переносить без отдельного согласования BlockNote/React/Mantine, ECharts,
Vue Flow, Гант, task-specific labels/pickers, публикации, права и API Tasker.
Каркас/навигация шаблона сохраняет его организации и настройки.

## Порядок реализации

1. Уточнить AppPageView, темы и ширину набора. Зафиксировать исходный Tasker commit
   и локальные изменения, снять референсы каталога и основных экранов обоих проектов.
2. Подключить фундамент: shadcn/Reka, Tailwind tokens, cn, control types,
   Nuxt aliases/registration и тему. Примитивы импортировать явно либо с отдельным
   префиксом; не создавать коллизии Nuxt auto-import. Не копировать весь package.json.
3. Перенести базовые контролы, AppField, меню, модалки, уведомления. Сразу добавить
   их варианты и состояния в `/ui`.
4. Перенести Select и DatePicker со вспомогательными модулями; адаптировать repo
   и значения. Покрыть тестами поиск/гонки/пагинацию, single/multiple и даты.
5. Перенести согласованный AppPageView/каркас. Встроить AppTable в AppList,
   сохранить list/detail/action templates, route/modal, page/section/flat-section,
   inline detail, extraParams/buildNewItem и обновление строк после сохранения.
6. Перевести все текущие экраны: auth, setup, home, организации/участники,
   пользователи, профиль, токены, каталог; навигацию, профильное меню и темы.
7. Удалить primevue, @primevue/nuxt-module, @primeuix/themes,
   tailwindcss-primeui, preset, старые CSS и auto-import обращения. Обновить lockfile.
8. Выполнить проверки ниже; обновить architecture.md, frontend-concept.md,
   README.md и product.md по фактическим изменениям. При добавлении отдельного
   UI-стандарта — добавить ссылку на него в AGENTS.md. Переиндексировать граф.

## Приёмка и визуальная проверка

Выполнить `make lint`, `pnpm --dir frontend exec nuxt typecheck`,
`pnpm --dir frontend build`; добавить целевые frontend component/unit tests
для изменяемого сложного поведения (добавлен Vitest test script).
Проверить отсутствие PrimeVue в зависимостях, импортах, типах, Nuxt config,
продуктовых компонентах и активных стилях. Историческое упоминание в этом плане допустимо.

В браузере сравнить с референсом Tasker: каталог, вход, выбор организации,
организации/участники, пользователи, профиль и токены. Использовать тестовые данные.
Проверить desktop 1440px, tablet 768px, mobile 390px, обе согласованные темы.
Проверять не только скриншоты, но и:

- поиск, страницу 2 и возврат назад, догрузку, пустой результат, ошибку и retry;
- создание/редактирование/удаление в route и modal режимах;
- два picker/список на одном repo и смену организации во время запроса;
- меню и выбор даты внутри модалки: clipping, z-index, Escape, Tab, возврат фокуса;
- открытие detail, табы/query, back, длинные названия, loading/disabled;
- изменение темы и перезагрузку, SSR/hydration warnings, console errors;
- отсутствие двойного scroll, наложений и горизонтального скролла всей страницы.

Предоставить скриншоты ключевых экранов, список пройденных сценариев и реальные
ограничения. Миграция завершена только после исправления найденных дефектов.
## Результат проверки

Проверены каталог `/ui`, светлая/тёмная темы, desktop 1440px,
tablet 768px и mobile 390px. Проверены поиск в выборе, добавление фильтра,
Modal с вложенным календарём, Escape, toast и создание записи в AppListTemplate
через демонстрационный repo + codec. Данные каталога локальные и не изменяют API.

Автоматическая проверка пройдена: make lint, frontend typecheck, 27 тестов Vitest
и production build. После исправления SSR дат и подключения просмотрщика изображений
через ClientOnly свежая production-загрузка не добавляет ошибок гидрации.
Для прохождения общего lint исправлена прежняя типизация SchemaListField
через GenericAlias; отдельно проверен encode/decode round trip без базы данных.
Live API сценарии организаций/пользователей требуют отдельной интеграционной
проверки с backend шаблона. Работающий локально на порту 8000 backend относится
к Tasker и для этих проверок не использовался. Миграции базы не запускались.
