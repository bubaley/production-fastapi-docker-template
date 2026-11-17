import type { SelectSource } from '~/shared/ui/app/select/types'

export type UiPerson = { id: string; name: string }

// Sample options shared by the form demos.
export const uiPeople: UiPerson[] = [
  { id: 'anna', name: 'Anna Smith' },
  { id: 'mark', name: 'Mark Wilson' },
  { id: 'elena', name: 'Elena Parker' },
  { id: 'olga', name: 'Olga Brown' },
  { id: 'ivan', name: 'Ivan Green' },
]

// A server-like source with a visible delay: loaded options stay on screen while it refetches.
export const uiSlowPeopleSource: SelectSource<UiPerson> = {
  async list(query, { page, size }) {
    await new Promise((resolve) => setTimeout(resolve, 1200))
    const search = String(query.search ?? '').toLocaleLowerCase()
    const items = uiPeople.filter((person) => person.name.toLocaleLowerCase().includes(search))
    return { items: items.slice((page - 1) * size, page * size), hasNext: page * size < items.length }
  },
}
