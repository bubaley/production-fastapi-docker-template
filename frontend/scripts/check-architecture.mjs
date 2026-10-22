// Guards the one-way UI layering: shared/ui/shadcn -> shared/ui/app -> shared/ui/template -> features.
// Only explicit imports are checked; Nuxt auto-imports are covered by the `components` / `imports.dirs` config.
import fs from 'node:fs'
import path from 'node:path'
import { parse } from 'vue/compiler-sfc'

const root = path.resolve(import.meta.dirname, '..')
const appDir = path.join(root, 'app')

// Existing violations kept until the code is moved. Remove an entry once it is fixed; stale entries fail the check.
const KNOWN_VIOLATIONS = new Set([])

const RULES = [
  {
    message: 'features must use App* wrappers, not reka-ui or shared/ui/shadcn',
    test: (from, to, spec) =>
      from.startsWith('features/') &&
      (spec === 'reka-ui' || spec.startsWith('reka-ui/') || to?.startsWith('shared/ui/shadcn/')),
  },
  {
    message: 'shared must not depend on features',
    test: (from, to) => from.startsWith('shared/') && to?.startsWith('features/'),
  },
  {
    message: 'shared/ui/shadcn must not depend on shared/ui/app or shared/ui/template',
    test: (from, to) =>
      from.startsWith('shared/ui/shadcn/') &&
      (to?.startsWith('shared/ui/app/') || to?.startsWith('shared/ui/template/')),
  },
]

const walk = (dir) =>
  fs
    .readdirSync(dir, { withFileTypes: true })
    .flatMap((entry) => (entry.isDirectory() ? walk(path.join(dir, entry.name)) : [path.join(dir, entry.name)]))

const toPosix = (value) => value.split(path.sep).join('/')

// Returns the target relative to app/ (without extension resolution), or null for packages and files outside app/.
const resolveTarget = (file, spec) => {
  const clean = spec.split('?')[0]
  let absolute = null
  if (clean.startsWith('.')) absolute = path.resolve(path.dirname(file), clean)
  else if (/^[~@]\//.test(clean)) absolute = path.join(appDir, clean.slice(2))
  else if (/^(?:~~|@@)\//.test(clean)) absolute = path.join(root, clean.slice(3))
  if (!absolute) return null
  const relative = toPosix(path.relative(appDir, absolute))
  return relative.startsWith('..') ? null : relative
}

const scriptOf = (file, source) => {
  if (!file.endsWith('.vue')) return source
  const { descriptor } = parse(source, { filename: file })
  return [descriptor.script?.content, descriptor.scriptSetup?.content].filter(Boolean).join('\n')
}

const importPattern = /\b(?:from\s*|import\s*\(?\s*|export\s*\*\s*from\s*)(['"])([^'"\n]+)\1/g

const files = walk(appDir).filter((file) => /\.(?:vue|ts|js|mjs)$/.test(file))
const failures = []
const seenKnown = new Set()

for (const file of files) {
  const from = toPosix(path.relative(appDir, file))
  const code = scriptOf(file, fs.readFileSync(file, 'utf8'))
  for (const match of code.matchAll(importPattern)) {
    const spec = match[2]
    const to = resolveTarget(file, spec)
    for (const rule of RULES) {
      if (!rule.test(from, to, spec)) continue
      const key = `${from} -> ${to ?? spec}`
      if (KNOWN_VIOLATIONS.has(key)) seenKnown.add(key)
      else failures.push(`${from}: ${rule.message} (${spec})`)
    }
  }
}

for (const key of KNOWN_VIOLATIONS)
  if (!seenKnown.has(key)) failures.push(`Stale KNOWN_VIOLATIONS entry, remove it: ${key}`)

if (failures.length) {
  console.error([...new Set(failures)].join('\n'))
  process.exitCode = 1
} else {
  console.log(`Architecture checks passed (${files.length} files, ${KNOWN_VIOLATIONS.size} known violations).`)
}
