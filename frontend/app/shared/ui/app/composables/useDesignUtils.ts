import type { RadiusToken, SizeToken } from '../../template/types/template-ui-tokens'

export const useDesignUtils = () => {
  const getRadiusBySize = (size: SizeToken): RadiusToken => {
    const values: Partial<Record<SizeToken, RadiusToken>> = { xs: 'sm', sm: 'sm', md: 'md' }
    return values[size] ?? 'md'
  }

  return { getRadiusBySize }
}
