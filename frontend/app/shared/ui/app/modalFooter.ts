import type { InjectionKey } from 'vue'

/**
 * Provided by the AppModal footer. Actions rendered there follow the one dialog layout: stacked full-width with the
 * primary on top on phones, right-aligned buttons of natural width (cancel first) from `sm` up.
 */
export const IN_MODAL_FOOTER: InjectionKey<boolean> = Symbol('in-modal-footer')

/** Provided by AppModal to its body: a form rendered inside (AppDetailTemplate) moves its actions into the footer. */
export const IN_MODAL: InjectionKey<boolean> = Symbol('in-modal')
