import type { AppPageShellProps } from '../../app/AppPage.vue'
import type { AppSectionProps } from '../../app/AppSection.vue'

type SectionBindSource = AppSectionProps &
  AppPageShellProps & {
    hideHeader?: boolean
    hideBackButton?: boolean
  }

type UseSectionBindOptions = {
  resolveBackAction?: () => (() => void) | undefined
}

/** Props for the template root: AppSectionProps, plus the page shell options when the root is AppPageView. */
export const useSectionBind = (props: SectionBindSource, options: UseSectionBindOptions = {}) => {
  return computed((): AppSectionProps & AppPageShellProps => ({
    ...(props.templateVariant === 'page' && {
      divided: props.divided,
      maxWidth: props.maxWidth,
      align: props.align,
      sticky: props.sticky,
    }),
    title: props.hideHeader ? undefined : props.title,
    description: props.description,
    templateVariant: props.templateVariant,
    titleSize: props.titleSize,
    flat: undefined,
    display: props.display,
    backAction: props.hideBackButton ? undefined : (options.resolveBackAction?.() ?? props.backAction),
  }))
}
