import { computed, onBeforeUnmount, shallowRef, toValue, watch, type MaybeRefOrGetter } from 'vue'
import type { ViewFilters, ViewFilterSpec } from './types'

/** Resolve restored IDs independently from option search/pagination, with bounded concurrency. */
export function useFilterSelectedItems(spec: MaybeRefOrGetter<ViewFilterSpec>, filters: MaybeRefOrGetter<ViewFilters>) {
  const cache = shallowRef<Record<string, object>>({})
  const pending = new Set<string>()
  const failed = new Set<string>()
  let disposed = false
  let workers = 0
  type Job = { key: string; id: string | number; retrieve: (id: string | number) => Promise<object | undefined> }
  let queue: Job[] = []
  const pump = () => {
    while (!disposed && workers < 4 && queue.length) {
      const job = queue.shift()!
      workers++
      pending.add(job.key)
      void job
        .retrieve(job.id)
        .then((item) => {
          if (!disposed && item) cache.value = { ...cache.value, [job.key]: item }
        })
        .catch(() => {
          failed.add(job.key)
        })
        .finally(() => {
          pending.delete(job.key)
          workers--
          pump()
        })
    }
  }
  const desired = computed(() =>
    Object.entries(toValue(filters)).flatMap(([key, value]) => {
      const [name, lookup] = key.split('__')
      const field = toValue(spec).fields.find((field) => field.field === name)
      if (!field?.repo?.retrieve || lookup === 'isnull') return []
      const repo = field.repo
      return (Array.isArray(value) ? value : [value]).flatMap((id) =>
        (typeof id === 'string' && id !== '') || typeof id === 'number'
          ? [{ key: `${name}:${id}`, id: id as string | number, retrieve: (id: string | number) => repo.retrieve!(id) }]
          : [],
      )
    }),
  )
  watch(
    desired,
    (jobs) => {
      queue = queue.filter((job) => jobs.some((value) => value.key === job.key))
      for (const job of jobs) {
        if (
          cache.value[job.key] ||
          pending.has(job.key) ||
          failed.has(job.key) ||
          queue.some((value) => value.key === job.key)
        )
          continue
        queue.push(job)
      }
      pump()
    },
    { immediate: true },
  )
  onBeforeUnmount(() => {
    disposed = true
    queue = []
  })
  return (field: string) =>
    Object.entries(cache.value)
      .filter(([key]) => key.startsWith(`${field}:`))
      .map(([, item]) => item)
}
