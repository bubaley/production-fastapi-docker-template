# Frontend concept

How to add and grow a feature. Folder roles: [architecture.md](architecture.md). Full working example: `frontend/app/features/organization/` (`user` for tokens/nested lists, `/ui` for primitives).

A feature is `frontend/app/features/<name>/` with `models/`, `repos/`, `views/`. Add `components/` and `composables/` as soon as a view would otherwise mix unrelated UI or logic.

Pages stay thin. Views talk to data only through `useRepo('key')` — never `useFetch` for API resources. `$api` is already configured (`baseURL: /api/v1`, org header). `useOrganization()` is auto-imported (`organizationId`).

---

## Models — one entity, one file, type + codec

`models/project.ts` holds **only** `Project`: the interface and `projectCodec`. Another entity (`ProjectMember`) gets `models/projectMember.ts`, not a second model in the same file.

```typescript
type ProjectRaw = DeepPartial<Project>

export interface Project {
  id: string | null
  organization_id: string | null
  created_at: string | null
  updated_at: string | null
  name: string
}

export const projectCodec = createCodec<Project>({
  decode: (raw: ProjectRaw) => ({
    id: raw.id || null,
    organization_id: raw.organization_id || null,
    created_at: raw.created_at || null,
    updated_at: raw.updated_at || null,
    name: raw.name ?? '',
  }),
  encode: (data) => ({
    organization_id: data.organization_id || null,
    name: data.name || null,
  }),
})
```

- `id` is `string | null` (UUID from the API)
- `decode` — response → typed object, every field defaulted
- `encode` — typed object → payload; writable fields only (no `id` / `created_at` / `updated_at`)
- `createCodec`, `DeepPartial` are auto-imported from `shared/toolkits/repo/`

See `features/organization/models/organization.ts` and `organizationUser.ts`.

---

## Repo

`resource` is the backend URL prefix (kebab-case, plural). Register the store in `shared/composables/useRepo.ts`, then use `useRepo('project')` in views — do not import the store directly from screens.

```typescript
import { projectCodec } from '../models/project'

export const useProjectRepo = defineStore('projectRepo', () => {
  const config = getRepoConfig({ resource: 'projects', codec: projectCodec })
  const { state, actions } = createAppRepo(config)()
  return { ...state, ...actions }
})
```

See `features/organization/repos/organizationRepo.ts`. Extra state on a repo is fine when it is still *that* resource (`organization` current-org ref).

---

## Views vs components (decompose)

| Layer | Role |
|---|---|
| `views/` | One screen or a large reusable section (list page, detail page) |
| `components/Foo.vue` | One widget used by a view |
| `components/<cluster>/` | Several files that only make sense together |
| `composables/useX.ts` | Logic used by **multiple** views in the feature |

Split when a view starts mixing list + picker + modal + unrelated helpers. Do not wait for a 400-line file.

**Cluster folder** — parent list + row actions + a composable that only they need:

```
features/project/components/member-list/
  ProjectMembersList.vue
  MemberRoleSelect.vue
  useMemberList.ts
```

Keep `composables/useProject.ts` (or `useOrganization.ts`) at feature root when many screens share it. Same pattern in the kit: `shared/ui/app/date-picker/` (Vue files + `composables/`).

Existing reference: `OrganizationListView` / `OrganizationDetailView` + `OrganizationPicker.vue` + `OrganizationMembersList.vue` (members list can move into `components/member-list/` when it grows).

---

## Templates

Build screens from `shared/ui/app/` and `shared/ui/template/`. Extend those primitives; do not fork a one-off table.

| Component | Role |
|---|---|
| `AppPageView` / `PageHeader` | Page composition: one `h1`, actions and description, bounded scrolling content; optional controls and footer |
| `AppSection` | Structural grouping with title, `description` and optional actions/back action; no colored surface |
| `AppCard` | Visual surface: `variant` = `default`, `outlined`, `muted`, `elevated`; `color` = `neutral`, `primary`, `success`, `info`, `warning`, `danger` (`destructive` alias); independent `outlined` / `elevated`, padding and interactive state |
| `AppListTemplate` | List page or nested list: search, pagination, create, detail as route or modal |
| `AppDetailTemplate` | Form + save/delete (`AppDetailActions`) |
| `AppTemplateActions` | **Two or more buttons in a row.** Do not put several `AppButton`s side by side |
| `AppTabs` / `AppTabPanel` | Sections on a screen. `v-model` is the active tab `value`. `query-key` writes it to the URL. Live: `/ui` |
| `AppMenu` | Overflow, context menu, or custom overlay (`:actions`, `label` for heading). Live: `/ui` → Overlays |
| `AppModal` | Custom modal: `v-model`, `title`, `description` (`subtitle` compatibility), `width`. App-level overlay names use `Modal` |
| `AppConfirmModal` | Confirm/Decline modal: `:confirm` / `:decline`. Built on `AppModal` + `AppTemplateActions`. Live: `/ui` → Overlays |
| `AppTable` / `AppColumn` | Table with declarative `field`, `header`, `format` and scoped `#body`; retained by `AppListTemplate` |
| `AppSelect` | Single/multiple selection, search and pagination; repo-backed via `:repo="useRepo('user')"` |
| `AppFilterToolbar` | Tasker IssueViewToolbar filter bar: search, fixed fields, compact conditions added through **+**, quick/actions slots |
| `AppFilters` | Internal condition editor; toolbar uses `inline` mode. Specification and `v-model` are shared; feature owns query mapping |

`templateVariant`: `page` | `section` | `flat-section`. Page templates use `AppPageView`; both nested variants use structural `AppSection`. Do not wrap a page template in another page heading. Use `AppCard` when a nested block needs visual emphasis; `AppBlock` is removed.

```vue
<AppTabs
  v-model="tab"
  query-key="tab"
  :tabs="[
    { label: 'Список', value: 'list' },
    { label: 'Карта', value: 'map' },
  ]"
>
  <AppTabPanel tab-value="list">…</AppTabPanel>
  <AppTabPanel tab-value="map">…</AppTabPanel>
</AppTabs>
```

```vue
<AppModal v-model="open" title="Фильтры">
  …
</AppModal>

<AppConfirmModal
  v-model="confirmOpen"
  title="Удалить?"
  :confirm="remove"
/>
```

**List, navigate to detail**

```vue
<AppListTemplate
  title="Проекты"
  detail-route-name="settings-projects-id"
  :repo="useRepo('project')"
  filter
>
  <AppColumn field="name" header="Название" />
</AppListTemplate>
```

**List owned by a parent, detail in a modal**

```vue
<AppListTemplate
  title="Проекты"
  detail-mode="modal"
  template-variant="section"
  :extra-params="{ parent_id: props.parentId }"
  :build-new-item="() => projectCodec.decode({ parent_id: props.parentId })"
  :repo="useRepo('project')"
>
  <AppColumn header="Название" :format="(row) => row.name || '—'" />
  <template #detail-modal="{ detailItem }">
    <AppInput v-model="detailItem.name" label="Название" />
  </template>
</AppListTemplate>
```

**Detail page**

```vue
<AppDetailTemplate
  :build-new-item="() => projectCodec.decode({ organization_id: organizationId })"
  title="Проект"
  :repo="useRepo('project')"
  :back-action="() => navigateTo({ name: 'settings-projects' })"
>
  <template #default="{ item }">
    <AppInput v-model="item.name" label="Название" />
  </template>
</AppDetailTemplate>
```

See `features/organization/views/` and `features/user/views/`. Props worth knowing: `mode` (`page` \| `inline`), `actions-props`, `hide-back-button` (modals).

---

## UI foundations and query state

Detail pages also own their local record state. `useTemplateDetail` calls
`retrieve(id, params, onError, { storeInRepo: false })`, accepts only the current
route request, and invalidates requests when the component is disposed or the
repo is reset. `AppDetailTemplate` shows loading, a Russian error message and a
retry action instead of an empty form when retrieval fails. Successful saves
replace the local record with the server response.

Business repos expose a `revision` that increases on `resetStore()`. Responses
started before a reset cannot repopulate repo state or trigger response parsing
side effects. Lists, selects and details clear their local state on that revision.
The user-context plugin watches the authenticated user identity and resets all
business repos and the organization setup when the user logs out or changes.
Setup restoration and auth requests also ignore responses from a previous
context. Logout failures keep the current screen and show an error.

Token codecs include `user_id` only when creating a token; edits encode its
name without ownership fields. The backend rejects ownership fields on updates.

Use Vite 8 consistently for Nuxt, Tailwind and the test runner. The direct Vite
development dependency and Vitest 4 prevent Vite 7 types from being used to
validate the Nuxt Vite 8 plugin configuration. Run `pnpm typecheck` separately
from `pnpm build`; the production build does not enable TypeScript checks.

`shared/ui/shadcn/` contains the local shadcn/Reka primitives. Product views consume `App*` wrappers from `shared/ui/app/`, which share Tasker sizes (`types/control.ts`) and semantic CSS tokens in `assets/styles/tailwind.css`. Use those tokens for both themes rather than hard-coded colors. The catalogue at `/ui` is public with static examples; `/home/ui` is a compatibility redirect.

`AppListTemplate` keeps the repo/codec API and route/modal detail behavior. `useRepoData` owns **local** items, search, pagination, loading and error state. Query requests use `storeInRepo: false`, ignore obsolete responses, and reset pagination when search or reactive `extraParams` changes. Optional `storeInRepo` publishes the accepted result to the repo; a picker or nested list must not read another consumer's pagination/loading state. Pass reactive parameters as a getter when calling the composable. `AppSelect` likewise keeps its own query state and selected-item hydration.

`AppTable` keeps its header visible for empty, loading and error states. A body slot receives `{ data, item, index }`; buttons and links inside a row do not activate row navigation. Existing `AppColumn` formatting remains available:

```vue
<AppColumn field="name" header="Название" />
<AppColumn header="Описание" :format="(row) => row.description || '—'" />
<AppColumn header="Действия">
  <template #body="{ data }">
    <AppButton label="Изменить" @click="edit(data)" />
  </template>
</AppColumn>
```

`AppListTemplate` accepts `filterSpec` (`ViewFilterSpec`) describing field labels, kinds and supported lookups, `fixedFields` (`ViewFixedField[]`) for permanently displayed controls, and `availableFilters` (field-name array) for the add-filter menu. Omit `availableFilters` to offer all fields; pass `[]` to offer none. Fixed controls remain visible independently of that menu. `v-model:filters` optionally controls the `ViewFilters` record. Conditions automatically join the repo query and reset pagination; reactive `extraParams` take precedence to preserve page scope. The toolbar remains outside the page scroll area. Existing `#filters` and `#search-actions` slots work alongside the declarative filters. Backend endpoints must explicitly support each offered field/lookup.

```vue
<AppListTemplate
  :repo="useRepo('organization')"
  search-param="name"
  :filter-spec="{ fields: [{ field: 'key', label: 'Ключ', kind: 'text', lookups: ['icontains', 'exact'] }] }"
  :fixed-fields="[{ field: 'key', mode: 'single' }]"
  :available-filters="['key']"
/>
```

This example keeps an exact-key input visible and offers a contains-key condition through the add menu. Both conditions combine with name search. `AppFilters` and `AppFilterToolbar` in `shared/ui/app/filters/` also remain available independently.

---

## Wiring

**Page** — `pages/settings/projects/index.vue` / `[id].vue`:

```vue
<template><ProjectListView /></template>
<script setup lang="ts">
import ProjectListView from '~/features/project/views/ProjectListView.vue'
</script>
```

**Drawer** — `layouts/settings.vue` `navigationSections`:

```typescript
{ to: { name: 'settings-projects' }, label: 'Проекты', icon: 'lucide:folder' }
```

**Repo registry** — `shared/composables/useRepo.ts`: `project: useProjectRepo`.

Route names follow the file path: `settings/projects/[id].vue` → `settings-projects-id`.

---

## Async actions and labels

A **row** of buttons → `AppTemplateActions` (`action`, optional `successNotification`). It already handles per-button loading. A **single** click or modal → `useActionState`: bind `:loading="state.loading.value"` and `@click="state.execute"`. Do not add a parallel `ref` + `try/finally`. Overflow / right-click → `AppMenu`. Live: `/ui` (Layout + Overlays).

```ts
const saveState = useActionState(async () => {}, { successNotification: 'Сохранено' })
```

Feature label maps: a composable like `composables/useProjectLabels.ts` (`LabelConfig` + `getXxx()`), not ad hoc `Record<string, string>` in every component.


## Notifications and checks

Use `useToast()` with `toast.default` for ordinary confirmations, matching Tasker. `useNotify` is removed. `AppToaster` is mounted once at application level; errors can use `toast.error`.

```ts
const toast = useToast()
toast.default('Сохранено')
toast.error('Не удалось сохранить', { description: 'Попробуйте ещё раз' })
```

`useActionState` and template actions retain their loading and notification contracts. Avoid sending a second toast when the action helper already handles it.

From `frontend/`, run `pnpm test`, `pnpm typecheck` and `pnpm build`; run `make lint` from the repository root. UI acceptance also needs browser inspection of the catalogue and affected screens at desktop/mobile widths in both themes, with empty/loading/error states, keyboard focus and nested popovers in modals.

## Button and table variants

`AppButton` defaults to `variant="default"`. The colored button is `primary`.
Choose by the action role:

| Variant | Scenario |
|---|---|
| `default` | Main action of the current form/block: save, create, continue; normally one per action group |
| `secondary` | Filled neutral button, as in Tasker: companion action (cancel, back). Uses `--ds-surface-raised`; no visible border |
| `outline` | Transparent button with a border: filters, export, column settings |
| `ghost` | Compact row/menu actions or a lower-priority third action |
| `destructive` | Final confirmation of deletion or another destructive operation |
| `primary` | Explicit brand-colored accent when the scenario needs it; not the default |

`AppTable` defaults to `variant="default"`: transparent header, no outer border or
rounded corners; row separators remain. `variant="outline"` adds the border,
rounded corners and tinted header. `AppList` and `AppListTemplate` forward
`table-variant="outline"` when the framed style is needed. The catalog `/ui` shows
both variants with the same data and loading/empty/error states.

### Filter toolbar

Use `AppFilterToolbar` for the IssueToolbar pattern, not a standalone vertical
`AppFilters`. It ports Tasker `ViewFilterToolbar`: `v-model` holds conditions,
`v-model:search` holds search text, `spec` supplies fields and current repo adapters.
`fixedFields` pins single/multiple/optional controls; their keys are excluded from
repeated dynamic conditions. `visibleFields` / `hiddenFields` restrict available fields.
Slots `primary`, `fixed-<field>`, `quick`, `actions` supply feature-specific tools.
`wrap` wraps conditions on narrow screens; `alwaysShowAdd` keeps the plus visible.
Tasker's issue-specific pickers and display-settings menu are not part of this generic
filter bar; a feature can provide them through the slots. Existing repo + codec stays intact.

### Semantic colors

Follow shadcn tokens: `primary` is brand/main emphasis; `accent` is an interactive
hover/focus/active surface, not a status color. `danger` maps to `destructive`;
`success`/`positive`, `info` and `warning` extend the semantic palette.
Colored AppCards use one semantic color for both their tinted surface and border.
AppDataLabel/AppLabel use the same mapping for icons and values; `soft` adds a
matching tint, `outline` adds a matching border. Field captions remain muted.
The `/ui` catalog has directly authored English copy and displays actual prop names.

### Typography and appearance pickers

The sans stack is -apple-system, BlinkMacSystemFont, Inter, Segoe UI, Helvetica Neue,
Arial, sans-serif (also used by Tailwind font-sans). AppTitle renders the `as` heading
tag and maps sm/md/lg/xl to text-sm/text-base/text-xl/text-3xl. PageHeader defaults
to h1/xl; AppSection defaults to h2/lg. Both honor titleSize through AppTitle.
AppAppearancePicker defaults to the full, dynamically imported Lucide catalog;
custom loadIcons/currentIcon/normalizeIcon props remain supported. The grid is
virtualized and searchable by icon name. AppColorPicker maps vue-color variables
to application theme tokens, including portalled popovers. Emoji selection is removed.

AppDrawer slides in (200ms) and out (300ms) from its `side` and uses only the inner edge border (right for left drawers, left for right drawers). Modal headers use the shared header gap between title and description. Motion respects reduced-motion preferences.

Overlay drawers participate in the same opening-order stack as modals, menus and
pickers. A surface opened inside a drawer appears above it; interacting with that
surface keeps the drawer open. Inline drawers do not reserve an overlay layer.
The Overlays catalogue demonstrates a date picker and a modal opened from a drawer.

### Page regions and automatic list pagination

`AppPageView` follows Tasker's `AppPage` layout: `header` (custom whole header),
`subheader` (below the header, before the divider), `controls` (after the divider),
`default` (scrolling body), and `footer` (fixed bottom region). The standard
`PageHeader` accepts `prefix`, `title`, `title-append`, and `actions`; AppPageView
forwards these slots. `subtitle` remains an alias for `subheader`, with subheader
winning when both are supplied. Description appears once in the standard header.
`titleSize`, `backAction` and `contentClass` configure the heading, return action
and body spacing. HomeView is a working Russian example with search, actions,
example visibility and reset; pages/home/index.vue remains a thin wrapper.

`AppListTemplate` enables `infiniteScroll` by default for server-backed queries.
The existing `AppInfiniteScroll` observes a sentinel within the visible scroll
area and appends the next confirmed page. It waits during loading, stops at the
last page or error, and offers a manual retry. A configured `scrollHeight` bounds
the list and its sentinel together. Local/onlyClientSearch lists do not request
more pages. Set `:infinite-scroll="false"` for manual “Показать ещё” pagination.
Organization list/setup pass `search-param="name"` to match their backend filter. Keep search
and filter resets in `useRepoData`; do not add another observer in feature views.

### Fixed list tools, table edges and profile layout

Page-mode `AppListTemplate` puts search, `search-actions` and `filters` in
AppPageView's fixed `controls` region. `AppListToolbar` owns their shared layout;
AppList hides its inline toolbar in page mode to avoid duplicate controls. Nested
lists keep the same toolbar inside their section, sticky within its scroll area.
Search/query/pagination state remains owned by useRepoData.

Page table lists default to `tableBleed=true`: `-mx-3 md:-mx-4` compensates for the
standard AppPageView body padding and places the table against the page edges.
Set `:table-bleed="false"` to retain the body gutters. List mode and section/flat-section
variants keep their own spacing. Controls retain their separate page gutters.

AppButton accepts `textVariant` (`base` by default, or `muted`). Base preserves the
button variant's existing text color. Muted uses `text-muted-foreground` until hover
or keyboard focus, when the variant's normal text color returns, including the
inverted text of default/primary/destructive buttons. AppTemplateActions forwards
this prop through its actions. The UI catalogue shows both text variants.

The profile route is a thin wrapper for `UserProfileView`, which uses AppPageView
for the heading, description, body padding and scrolling content. The header product
name uses muted text at rest and foreground on hover. Home has no example badge.
