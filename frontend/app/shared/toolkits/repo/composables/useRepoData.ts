export interface UseRepoDataProps<T> {
  repo?: AppRepo<T extends AppModel ? T : never>
  items?: T[]
  searchParam?: string
  debounce?: number
  onlyClientSearch?: boolean
  filterFields?: (keyof T)[]
  filter?: boolean
  extraParams?: Record<string, any>
  autoLoad?: boolean
  storeInRepo?: boolean
  itemLabel?: string | ((v: T) => string)
  itemValue?: string | ((v: T) => string)
}

export const useRepoData = <T>(params: Omit<UseRepoDataProps<T>, 'items'> & { items?: Ref<T[] | undefined> }) => {
  const {
    repo,
    items,
    debounce,
    onlyClientSearch = false,
    filterFields = [],
    autoLoad = true,
    storeInRepo = false,
    searchParam = 'search',
    extraParams = {},
  } = params
  const itemLabel = params.itemLabel
  const itemValue = params.itemValue

  const search = ref('')

  const computedDebounce = computed(() => {
    return repo && !onlyClientSearch ? (debounce ?? 400) : 0
  })

  const getItemLabel = (item?: T | null) => {
    if (!item) return null
    if (typeof itemLabel === 'function') return itemLabel(item)
    return itemLabel ? (item as any)[itemLabel as keyof T] : item
  }

  const getItemValue = (item?: T | null) => {
    if (!item) return null
    if (typeof itemValue === 'function') return itemValue(item)
    return itemValue ? (item as any)[itemValue as keyof T] : item
  }

  // ?????
  const _getFieldValue = (item: T, field: keyof T | string | ((v: T) => string)): string => {
    if (!item) return ''
    if (typeof field === 'function') return field(item)
    return String((item as any)[field] || '')
  }

  const clientFilter = (items: T[], searchTerm: string): T[] => {
    if (!searchTerm.trim()) return items as T[]
    const fieldsToSearch = filterFields.length > 0 ? filterFields : [itemLabel as keyof T]
    return filterBySearch<T>(searchTerm, items, (item) => {
      // Combine all searchable fields into one string
      return fieldsToSearch
        .map((field) => _getFieldValue(item, field))
        .join(' ')
        .toLowerCase()
    })
  }

  const _loadItems = async (params: Record<string, any> = {}, config: RepoListConfig = {}) => {
    if (!repo) return items?.value || []
    const searchParams = search.value ? { [searchParam]: search.value } : {}
    const result = await repo.list({ ...searchParams, ...params, ...extraParams }, { storeInRepo, ...config })
    return result?.items || []
  }

  const loadItems = async (params: Record<string, any> = {}, config: RepoListConfig = {}) => {
    loadItemsState.data.value = await _loadItems(params, config)
  }

  const loadItemsState = useActionState<T[]>(
    async () => {
      if (repo && !onlyClientSearch) {
        return await _loadItems()
      } else {
        return clientFilter(items?.value || [], search.value)
      }
    },
    { debounce: computedDebounce.value },
  )

  const itemsComputed = computed<T[]>(() => {
    return (loadItemsState.data.value || []) as T[]
  })

  watch(search, () => {
    void loadItemsState.execute()
  })

  watch(
    () => items?.value,
    (v) => {
      _setInitialItems(v || [])
    },
  )

  const _setInitialItems = (items: T[]) => {
    loadItemsState.data.value = items
  }

  onMounted(async () => {
    if (items?.value?.length) {
      _setInitialItems(items?.value)
    }
    if (repo && storeInRepo) {
      _setInitialItems(repo.items || [])
    }
    if (autoLoad && repo) {
      _setInitialItems((await _loadItems()) || [])
    }
  })

  return {
    // Data
    items: itemsComputed,
    search,
    loadItemsState,

    // Computed properties
    debounce: computedDebounce,

    // Methods
    loadItems,
    getItemLabel,
    getItemValue,
    clientFilter,

    // Default properties
    itemLabel,
    itemValue,
  }
}
