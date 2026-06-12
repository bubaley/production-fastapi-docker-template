export type AppListEventsConfig<T> = {
  items: MaybeRef<T[]>
  key: keyof T
}

export const useTemplateListEvents = <T>(config: AppListEventsConfig<T>) => {
  const items = computed(() => (isRef(config.items) ? config.items.value : config.items))

  const findListItemIndex = (value: T) => {
    const valueKey = value[config.key]
    return items.value.findIndex((item) => item[config.key] === valueKey)
  }

  const deleteListItem = (value?: T) => {
    if (!value) return
    const index = findListItemIndex(value)
    if (index > -1) {
      items.value.splice(index, 1)
    }
  }

  const updateListItem = (value?: T) => {
    if (!value) return
    const index = findListItemIndex(value)
    if (index > -1) {
      items.value.splice(index, 1, value)
    } else {
      items.value.push(value)
    }
  }

  return {
    findListItemIndex,
    deleteListItem,
    updateListItem,
  }
}
