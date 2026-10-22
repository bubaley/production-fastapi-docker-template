import { ref } from 'vue'
import { defineResource } from '~/shared/api/resource'

export type UiDemoProject = { id: string; name: string; owner: string; status: string }
export type UiDemoProjectForm = { id: string | null; name: string; owner: string; status: string }
type UiDemoProjectBody = Omit<UiDemoProject, 'id'>

const initial: UiDemoProject[] = [
  { id: '1', name: 'Product launch', owner: 'Anna Smith', status: 'In progress' },
  { id: '2', name: 'Component library', owner: 'Mark Wilson', status: 'Success' },
  { id: '3', name: 'Feedback', owner: 'Elena Parker', status: 'Planned' },
]

// Deliberately local: the catalogue never calls a product API. The "SDK" below has the shape of the generated
// functions, so the list/detail templates run their real Colada queries and mutations against it.
const projects = ref<UiDemoProject[]>(initial.map((item) => ({ ...item })))
const find = (id: string) => {
  const item = projects.value.find((project) => project.id === id)
  if (!item) throw new Error('Not found')
  return item
}

const uiDemoResource = defineResource({
  key: 'ui-demo-projects',
  sdk: {
    list: async ({ query = {} }) => {
      const search = String(query.search ?? '').toLocaleLowerCase()
      const page = Number(query.page ?? 1)
      const size = Number(query.page_size ?? 50)
      const items = projects.value.filter((item) => `${item.name} ${item.owner}`.toLocaleLowerCase().includes(search))
      return {
        data: {
          data: items.slice((page - 1) * size, page * size),
          meta: { page, page_size: size, has_next: page * size < items.length },
        },
      }
    },
    retrieve: async ({ path }) => ({ data: { ...find(path.item_id) } }),
    create: async ({ body }: { body: UiDemoProjectBody }) => {
      const saved = { ...body, id: `demo-${Date.now()}` }
      projects.value = [...projects.value, saved]
      return { data: saved }
    },
    update: async ({ path, body }: { path: { item_id: string }; body: UiDemoProjectBody }) => {
      const saved = { ...find(path.item_id), ...body }
      projects.value = projects.value.map((item) => (item.id === saved.id ? saved : item))
      return { data: saved }
    },
    destroy: async ({ path }) => {
      projects.value = projects.value.filter((item) => item.id !== path.item_id)
    },
  },
  toForm: (item?: Partial<UiDemoProject>): UiDemoProjectForm => ({
    id: item?.id ?? null,
    name: item?.name ?? '',
    owner: item?.owner ?? '',
    status: item?.status ?? 'In progress',
  }),
  toCreate: ({ name, owner, status }) => ({ name, owner, status }),
  toUpdate: ({ name, owner, status }) => ({ name, owner, status }),
})

export const useUiDemoProjects = () => ({ projects, resource: uiDemoResource })
