import type { AppSectionProps } from '../../app/AppSection.vue'

type RestoreRepoItemParams<T extends AppModel> = {
  itemId?: string | number | null
  repo: AppRepoStore<T>
  buildNewItem?: () => T
}

type SectionBindSource = AppSectionProps & {
  hideHeader?: boolean
  hideBackButton?: boolean
}

type UseSectionBindOptions = {
  resolveBackAction?: () => (() => void) | undefined
}

export const useSectionBind = (
  props: SectionBindSource,
  options: UseSectionBindOptions = {},
) => {
  return computed((): AppSectionProps => ({
    title: props.hideHeader ? undefined : props.title,
    description: props.description,
    templateVariant: props.templateVariant,
    titleSize: props.titleSize,
    flat: undefined,
    display: props.display,
    backAction: props.hideBackButton
      ? undefined
      : options.resolveBackAction?.() ?? props.backAction,
  }))
}

export const useAppTemplate = () => {
  const restoreRepoItem = async <T extends AppModel>(params: RestoreRepoItemParams<T>): Promise<T> => {
    if (!params.itemId || params.itemId === 'new') {
      if (!params.buildNewItem) {
        throw new Error('buildNewItem is required when itemId is not provided')
      }
      const item = params.buildNewItem()
      params.repo.item = item
      return item
    }

    await params.repo.retrieve(params.itemId)
    if (!params.repo.item) {
      throw new Error('Item not found')
    }
    return params.repo.item
  }

  return { restoreRepoItem }
}
