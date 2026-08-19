# Frontend concept

How to add and grow a feature. Folder roles: [architecture.md](architecture.md). Full working example: `frontend/app/features/organization/` (`user` for tokens/nested lists, `/home/ui` for primitives).

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

Keep `composables/useProject.ts` (or `useOrganization.ts`) at feature root when many screens share it. Same pattern in the kit: `shared/ui/app/smartDatePicker/` (Vue files + `composables/`).

Existing reference: `OrganizationListView` / `OrganizationDetailView` + `OrganizationPicker.vue` + `OrganizationMembersList.vue` (members list can move into `components/member-list/` when it grows).

---

## Templates

Build screens from `shared/ui/app/` and `shared/ui/template/`. Extend those primitives; do not fork a one-off table.

| Component | Role |
|---|---|
| `AppSection` | Title + `description` (not `subtitle`) + optional `backAction` |
| `AppListTemplate` | List page or nested list: search, pagination, create, detail as route or modal |
| `AppDetailTemplate` | Form + save/delete (`AppDetailActions`) |
| `AppTemplateActions` | **Two or more buttons in a row.** Do not put several `AppButton`s side by side |
| `AppTabs` / `AppTabPanel` | Sections on a screen. `v-model` is the active tab `value`. `query-key` writes it to the URL. Live: `/home/ui` |
| `AppMenu` | Overflow, context menu, or custom overlay (`:actions`, `label` for heading). Live: `/home/ui` → Overlays |
| `AppModal` | Custom dialog: `v-model`, `title`, `subtitle`, `width`. Do not use PrimeVue `Dialog` directly |
| `AppConfirmModal` | Confirm/Decline dialog: `:confirm` / `:decline`. Built on `AppModal` + `AppTemplateActions`. Live: `/home/ui` → Overlays |
| `AppColumn` / `AppSelect` | Formatted column; repo-backed select (`:repo="useRepo('user')"`) |

`templateVariant`: `page` \| `section` \| `flat-section`.

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
  title="Projects"
  detail-route-name="settings-projects-id"
  :repo="useRepo('project')"
  filter
>
  <Column field="name" header="Name" />
</AppListTemplate>
```

**List owned by a parent, detail in a modal**

```vue
<AppListTemplate
  title="Projects"
  detail-mode="modal"
  template-variant="section"
  :extra-params="{ parent_id: props.parentId }"
  :build-new-item="() => projectCodec.decode({ parent_id: props.parentId })"
  :repo="useRepo('project')"
>
  <AppColumn header="Name" :format="(row) => row.name || '—'" />
  <template #detail-modal="{ detailItem }">
    <AppInput v-model="detailItem.name" label="Name" />
  </template>
</AppListTemplate>
```

**Detail page**

```vue
<AppDetailTemplate
  :build-new-item="() => projectCodec.decode({ organization_id: organizationId })"
  title="Project"
  :repo="useRepo('project')"
  :back-action="() => navigateTo({ name: 'settings-projects' })"
>
  <template #default="{ item }">
    <AppInput v-model="item.name" label="Name" />
  </template>
</AppDetailTemplate>
```

See `features/organization/views/` and `features/user/views/`. Props worth knowing: `mode` (`page` \| `inline`), `actions-props`, `hide-back-button` (modals).

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

A **row** of buttons → `AppTemplateActions` (`action`, optional `successNotification`). It already handles per-button loading. A **single** click or modal → `useActionState`: bind `:loading="state.loading.value"` and `@click="state.execute"`. Do not add a parallel `ref` + `try/finally`. Overflow / right-click → `AppMenu`. Live: `/home/ui` (Layout + Overlays).

```ts
const saveState = useActionState(async () => {}, { successNotification: 'Сохранено' })
```

Feature label maps: a composable like `composables/useProjectLabels.ts` (`LabelConfig` + `getXxx()`), not ad hoc `Record<string, string>` in every component.
