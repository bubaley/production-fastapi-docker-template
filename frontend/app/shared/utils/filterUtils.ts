
export const filterBySearch = <T>(
  value: string | null | undefined,
  items: T[] | undefined | null,
  searchFunction: (value: T) => string | any[]
): T[] => {
  if (!value || !items) return items || []
  const words = value.toLowerCase().split(' ')
  return items.filter((v) => {
    let searchValue = searchFunction(v)
    if (Array.isArray(searchValue)) {
      searchValue = searchValue.filter(v => v !== undefined && v !== null).map(v => String(v)).join('')
    }
    const currentValue = searchValue.toLowerCase()
    for (const word of words) {
      if (currentValue.indexOf(word) === -1) return false
    }
    return true
  })
}
