import type { ApiClient } from './client'

/** A row the API returns: every resource has a UUID `id`. */
export type ResourceItem = { id: string }
/** The editable copy a detail form binds to; no `id` (or `null`) means "not created yet". */
export type ResourceForm = { id?: string | null }
export type ListQuery = Record<string, unknown>

/** `<ReadSchema>Page` from the API. */
export type Page<T> = { data: T[]; meta?: { page?: number; page_size?: number; has_next?: boolean } }

// Optional members keep the generated functions assignable (their options are all optional but `path`/`body`).
type Call = { client?: ApiClient; throwOnError?: true; signal?: AbortSignal }
type ById = { path: { item_id: string } }
type Result<T> = Promise<{ data: T }>

/**
 * Generated SDK functions of one resource (`organizationsList`, `organizationsRetrieve`, …). Method syntax keeps
 * parameters bivariant, so the generated functions with their exact query/body types fit as they are.
 */
export interface ResourceSdk<TItem, TCreate, TUpdate> {
  list?(options: Call & { query?: ListQuery }): Result<Page<TItem>>
  retrieve?(options: Call & ById): Result<TItem>
  create?(options: Call & { body: TCreate }): Result<TItem>
  update?(options: Call & ById & { body: TUpdate }): Result<TItem>
  destroy?(options: Call & ById): Promise<unknown>
}

/**
 * Everything the list/detail templates need to know about one API resource. Define one per entity next to the
 * feature (`features/<name>/resources/<entity>.ts`) with `defineResource`.
 */
export interface Resource<
  TItem extends ResourceItem = ResourceItem,
  TForm extends ResourceForm = ResourceForm,
  TCreate = unknown,
  TUpdate = unknown,
> {
  /** Query-key root, the plural resource name: `['organizations', …]`. */
  key: string
  sdk: ResourceSdk<TItem, TCreate, TUpdate>
  /** Form state for an existing item, or a new record when called without one. */
  toForm: (item?: Partial<TItem>) => TForm
  toCreate?: (form: TForm) => TCreate
  toUpdate?: (form: TForm) => TUpdate
  /** Other query-key roots a successful mutation makes stale, e.g. `['session']`. */
  invalidates?: string[]
}

/** Request body type of a generated SDK function (`body` of its options). */
type BodyOf<F> = F extends (options: infer O) => unknown ? (O extends { body: infer B } ? B : never) : never

/**
 * Typed resource descriptor. `TItem` comes from `toForm`'s parameter, the create/update body types from the
 * generated SDK functions, so `toCreate`/`toUpdate` must return exactly what the API accepts.
 */
export const defineResource = <
  TItem extends ResourceItem,
  TForm extends ResourceForm,
  TSdk extends ResourceSdk<TItem, any, any>,
>(resource: {
  key: string
  sdk: TSdk
  toForm: (item?: Partial<TItem>) => TForm
  toCreate?: (form: TForm) => BodyOf<TSdk['create']>
  toUpdate?: (form: TForm) => BodyOf<TSdk['update']>
  invalidates?: string[]
}) => resource as Resource<TItem, TForm, BodyOf<TSdk['create']>, BodyOf<TSdk['update']>>

/**
 * Query keys. Lists and details share the resource root, so `invalidateQueries({ key: [resource.key] })`
 * reaches all of them; `[key, 'list', params]` is the infinite list, `[key, id]` one record.
 */
export const resourceKeys = (resource: Pick<Resource, 'key'>) => ({
  all: [resource.key] as const,
  lists: [resource.key, 'list'] as const,
  list: (params: ListQuery) => [resource.key, 'list', params] as const,
  detail: (id: string) => [resource.key, id] as const,
})

const missing = (resource: Pick<Resource, 'key'>, operation: string): never => {
  throw new Error(`Resource "${resource.key}" has no ${operation}`)
}

export const DEFAULT_PAGE_SIZE = 50

/** One page of a list: `{ items, hasNext }`. An empty page ends pagination whatever `has_next` says. */
export const fetchPage = async <TItem extends ResourceItem>(
  resource: Resource<TItem, any, any, any>,
  client: ApiClient,
  query: ListQuery,
  page: number,
  pageSize = DEFAULT_PAGE_SIZE,
  signal?: AbortSignal,
) => {
  const list = resource.sdk.list ?? missing(resource, 'list')
  const { data } = await list({ client, throwOnError: true, signal, query: { ...query, page, page_size: pageSize } })
  const items = data.data ?? []
  return { items, hasNext: items.length > 0 && Boolean(data.meta?.has_next) }
}

export const fetchItem = async <TItem extends ResourceItem>(
  resource: Resource<TItem, any, any, any>,
  client: ApiClient,
  id: string,
  signal?: AbortSignal,
) => {
  const retrieve = resource.sdk.retrieve ?? missing(resource, 'retrieve')
  return (await retrieve({ client, throwOnError: true, signal, path: { item_id: id } })).data
}

/** Create or update from the form; resolves to the saved item from the API. */
export const saveItem = async <TItem extends ResourceItem, TForm extends ResourceForm, TCreate, TUpdate>(
  resource: Resource<TItem, TForm, TCreate, TUpdate>,
  client: ApiClient,
  form: TForm,
) => {
  if (form.id) {
    const update = resource.sdk.update ?? missing(resource, 'update')
    const body = resource.toUpdate ? resource.toUpdate(form) : (form as unknown as TUpdate)
    return {
      item: (await update({ client, throwOnError: true, path: { item_id: form.id }, body })).data,
      created: false,
    }
  }
  const create = resource.sdk.create ?? missing(resource, 'create')
  const body = resource.toCreate ? resource.toCreate(form) : (form as unknown as TCreate)
  return { item: (await create({ client, throwOnError: true, body })).data, created: true }
}

export const destroyItem = async (resource: Resource<any, any, any, any>, client: ApiClient, id: string) => {
  const destroy = resource.sdk.destroy ?? missing(resource, 'destroy')
  await destroy({ client, throwOnError: true, path: { item_id: id } })
}

/** Options source for `AppSelect` and filter fields: plain page requests, the select keeps its own pagination. */
export const resourceSource = <TItem extends ResourceItem>(
  resource: Resource<TItem, any, any, any>,
  client: ApiClient,
) => ({
  list: (query: ListQuery, { page, size }: { page: number; size: number }) =>
    fetchPage(resource, client, query, page, size),
  retrieve: (id: string) => fetchItem(resource, client, id),
})
