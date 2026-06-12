import { cloneDeep } from 'lodash-es'
import type { ResponseType } from 'ofetch'

export const createAppRepo = <T extends AppModel>(config: AppRepoConfig<T>) => {
  return () => {
    const api = new AppApi({
      resource: config.resource,
      client: config.apiClient,
    })
    const _codec = config.codec
    const _paginationCodec = config.paginationCodec

    // --- STATE ---
    const item: Ref<T | null> = ref(null)
    const items: Ref<T[]> = ref([])
    const loading: Ref<LoadingState> = ref({
      create: false,
      update: false,
      delete: false,
      list: false,
      retrieve: false,
      action: false,
    })
    const pagination: Ref<AppPagination> = ref(_paginationCodec.decode({}))

    // --- COMPUTED ---
    const isLoading = computed(() => Object.values(loading.value).some(Boolean))

    // --- HELPERS ---
    const resetStore = () => {
      item.value = null
      // items.value = []
      items.value = []
      pagination.value = _paginationCodec.decode({})
      Object.keys(loading.value).forEach((k) => (loading.value[k as keyof LoadingState] = false))
    }

    const resetPagination = () => {
      pagination.value = _paginationCodec.decode({})
    }

    const withLoading = async <R>(key: keyof LoadingState, fn: () => Promise<R>): Promise<R> => {
      loading.value[key] = true
      try {
        return await fn()
      } finally {
        loading.value[key] = false
      }
    }

    const handleError = (error: unknown, onError?: RepoOnError) => {
      if (!onError) throw error
      const status_code = (error as any)?.status
      const message = error instanceof Error ? error.message : String(error)
      onError({ status_code, message })
    }

    // --- GENERIC REQUEST WRAPPER ---
    const _request = async <R>(
      key: keyof LoadingState,
      sendConfig: AppApiSendConfig,
      parseFn?: (response: any) => R,
      storeFn?: (parsed: R) => void,
      onError?: RepoOnError,
    ): Promise<R | undefined> => {
      return withLoading(key, async () => {
        try {
          const response = await api.send(sendConfig)
          const parsed = parseFn ? parseFn(response) : (response as R)
          if (storeFn) storeFn(parsed)
          return parsed
        } catch (error) {
          handleError(error, onError)
        }
      })
    }

    // --- CRUD METHODS ---
    const list = (params: Record<string, unknown> = {}, options: RepoListConfig = {}, onError?: RepoOnError) =>
      _request<{ items: T[]; pagination: AppPagination }>(
        'list',
        {
          method: 'get',
          params: { ...cloneDeep(params), ..._paginationCodec.encode(options.pagination || pagination.value) },
        },
        (raw) => {
          if (config.parseManyResponse) {
            return config.parseManyResponse(raw, 'list')
          }
          const resultsKey = config.manyDataKey || 'data'
          const { [resultsKey]: results, ...paginationData } = raw as AppPaginatedResponse<T>
          const _items = (results as any[]).map((v) => _codec.decode(v))
          return {
            items: _items,
            loaded: _items,
            pagination: _paginationCodec.decode(paginationData),
          }
        },
        (parsed) => {
          if (options.storeInRepo !== false) {
            pagination.value = parsed.pagination
            items.value = options.mode === 'append' ? [...items.value, ...parsed.items] : parsed.items
            parsed.items = items.value // #TODO: doubtfully
          }
        },
        onError,
      )

    const retrieve = (id: string | number, params?: Record<string, unknown>, onError?: RepoOnError) =>
      _request<T>(
        'retrieve',
        { method: 'get', id, params },
        (raw) => (config.parseResponse ? config.parseResponse(raw, 'retrieve') : _codec.decode(raw)),
        (parsed) => (item.value = parsed),
        onError,
      )

    const create = (object: T, onError?: RepoOnError) =>
      _request<T>(
        'create',
        { method: 'post', data: _codec.encode(object) },
        (raw) => (config.parseResponse ? config.parseResponse(raw, 'create') : _codec.decode(raw)),
        (parsed) => (item.value = parsed),
        onError,
      )

    const update = (object: T, onError?: RepoOnError) =>
      _request<T>(
        'update',
        { method: 'put', id: object.id, data: _codec.encode(object) },
        (raw) => (config.parseResponse ? config.parseResponse(raw, 'update') : _codec.decode(raw)),
        (parsed) => (item.value = parsed),
        onError,
      )

    const updateOrCreate = (object: T, onError?: RepoOnError): { create: boolean; promise: Promise<T | undefined> } => {
      const promise = object.id ? update(object, onError) : create(object, onError)
      return {
        create: !!object.id,
        promise,
      }
    }

    const destroy = (object: T, onError?: RepoOnError) =>
      _request<any>(
        'delete',
        { method: 'delete', id: object.id },
        () => undefined,
        () => {},
        onError,
      )

    // --- PUBLIC API ---
    const state = {
      item,
      items,
      loading,
      pagination,
      isLoading,
    }

    const actions = {
      resetStore,
      resetPagination,
      list,
      retrieve,
      create,
      update,
      updateOrCreate,
      delete: destroy,
      send: <R>(data: AppApiSendConfig) => api.send<R>(data),
      sendRaw: <R, E extends ResponseType = 'json'>(data: AppApiSendConfigRaw<E>) => api.sendRaw<R, E>(data),
      encode: _codec.encode,
      decode: _codec.decode,
    }

    return { state, actions }
  }
}
