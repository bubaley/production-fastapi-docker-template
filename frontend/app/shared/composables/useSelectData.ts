import { useRepoData, type UseRepoDataProps } from '../toolkits/repo/composables/useRepoData'

// props
export interface UseSelectDataProps<T> extends Omit<UseRepoDataProps<T>, 'items' | 'itemLabel'> {
  options?: T[]
  optionLabel?: string | ((v: T) => string)
  optionValue?: string | ((v: T) => string)
  dataKey?: string
  show?: Ref<boolean>
}

// useSelectData
export const useSelectData = <T>(
  params: Omit<UseSelectDataProps<T>, 'options'> & { options?: Ref<T[] | undefined> }
) => {


  // Use base repo data composable
  const repoData = useRepoData<T>({
    ...params,
    items: params.options,
    itemLabel: params.optionLabel,
    itemValue: params.optionValue,
  })

  watch(
    () => params.show?.value,
    (v) => {
      if (v) {
        void repoData.loadItems()
      }
    },
  )

  const getOptionByValue = (value: any): T | undefined => {
    if (repoData.itemValue) {
      return repoData.items.value.find((item) => repoData.getItemValue(item) === value) || undefined
    }
    return value
  }

  const getOptionLabel = (value?: T | null) => {
    return repoData.getItemLabel(value)
  }
  return {
    // Spread all repo data functionality
    ...repoData,

    optionValue: repoData.itemValue,
    optionLabel: repoData.itemLabel,

    // Select-specific methods
    getOptionLabel,
    getOptionByValue,
    // getLabelByValue,
  }
}
