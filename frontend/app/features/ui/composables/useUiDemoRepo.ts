import type { AppRepo } from '~/shared/toolkits/repo/types'
import { createCodec } from '~/shared/toolkits/repo/appModel'
import { paginationFromServer } from '~/shared/toolkits/repo/appPagination'

export interface UiDemoProject {
  id: string | null
  name: string
  owner: string
  status: string
}
export const uiDemoCodec = createCodec<UiDemoProject>({
  decode: (raw: Partial<UiDemoProject>) => ({ id: raw.id ?? null, name: raw.name ?? '', owner: raw.owner ?? '', status: raw.status ?? 'In progress' }),
  encode: item => ({ name: item.name, owner: item.owner, status: item.status }),
})
const initial = [
  { id: '1', name: 'Product launch', owner: 'Anna Smith', status: 'In progress' },
  { id: '2', name: 'Component library', owner: 'Mark Wilson', status: 'Success' },
  { id: '3', name: 'Feedback', owner: 'Elena Parker', status: 'Planned' },
]

// This repository is deliberately local: the catalogue never calls a product API.
export function useUiDemoRepo() {
  const repo: AppRepo<UiDemoProject> = reactive({
    item: null,
    items: initial.map(item => uiDemoCodec.decode(item)),
    loading: { create: false, update: false, delete: false, list: false, retrieve: false, action: false },
    pagination: paginationFromServer({ total: initial.length, pages: 1 }),
    isLoading: false,
    resetStore: () => { repo.items = initial.map(item => uiDemoCodec.decode(item)); repo.item = null },
    resetPagination: () => { repo.pagination = paginationFromServer() },
    list: async (params = {}, options = {}) => {
      const search = String(params.search ?? '').toLocaleLowerCase()
      const items = repo.items.filter(item => `${item.name} ${item.owner}`.toLocaleLowerCase().includes(search))
      const page = options.pagination?.page ?? 1
      const size = options.pagination?.size ?? 50
      return { items: items.slice((page - 1) * size, page * size).map(item => uiDemoCodec.decode(item)), pagination: paginationFromServer({ page, size, total: items.length, pages: Math.ceil(items.length / size) }) }
    },
    retrieve: async id => { repo.item = uiDemoCodec.decode(repo.items.find(item => item.id === String(id)) ?? {}); return repo.item },
    create: async item => {
      const saved = uiDemoCodec.decode({ ...uiDemoCodec.encode(item), id: `demo-${Date.now()}` })
      repo.items = [...repo.items, saved]
      return saved
    },
    update: async item => {
      const saved = uiDemoCodec.decode({ ...uiDemoCodec.encode(item), id: item.id })
      repo.items = repo.items.map(current => current.id === saved.id ? saved : current)
      return saved
    },
    delete: async item => { repo.items = repo.items.filter(current => current.id !== item.id) },
    send: async () => undefined,
    encode: uiDemoCodec.encode,
    decode: uiDemoCodec.decode,
  })
  return repo
}
