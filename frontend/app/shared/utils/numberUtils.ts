export const parseNumber = (value?: string | null, decimals: number = 1) => {
  if (!value) return 0
  const number = parseFloat(value)
  return Number(number.toFixed(decimals))
}

export const beautifyNumber = (value?: string | number | null, decimals: number = 2) => {
  if (!value) return 0
  const number = typeof value === 'number' ? value : parseFloat(value)
  const x = Number(number.toFixed(decimals))

  const parts = x.toString().split('.')
  parts[0] = parts[0]?.replace(/\B(?=(\d{3})+(?!\d))/g, ' ') ?? ''
  return parts.join('.')
}
