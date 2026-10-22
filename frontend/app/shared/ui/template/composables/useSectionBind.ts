import type { AppSectionProps } from '../../app/AppSection.vue'

type SectionBindSource = AppSectionProps & {
  hideHeader?: boolean
  hideBackButton?: boolean
}

type UseSectionBindOptions = {
  resolveBackAction?: () => (() => void) | undefined
}

export const useSectionBind = (props: SectionBindSource, options: UseSectionBindOptions = {}) => {
  return computed((): AppSectionProps => ({
    title: props.hideHeader ? undefined : props.title,
    description: props.description,
    templateVariant: props.templateVariant,
    titleSize: props.titleSize,
    flat: undefined,
    display: props.display,
    backAction: props.hideBackButton ? undefined : (options.resolveBackAction?.() ?? props.backAction),
  }))
}
