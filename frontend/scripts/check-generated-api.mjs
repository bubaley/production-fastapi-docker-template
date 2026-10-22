// Fails when app/shared/api/generated differs from what `pnpm gen:api` would write for the current openapi.json.
import { execFileSync } from 'node:child_process'
import { existsSync, readdirSync, readFileSync, rmSync } from 'node:fs'
import { join, relative } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = fileURLToPath(new URL('..', import.meta.url))
const committed = join(root, 'app/shared/api/generated')
const fresh = join(root, '.gen-api-check')

const listFiles = (dir) =>
  existsSync(dir)
    ? readdirSync(dir, { recursive: true, withFileTypes: true })
        .filter((entry) => entry.isFile())
        .map((entry) => relative(dir, join(entry.parentPath, entry.name)))
        .sort()
    : []

rmSync(fresh, { recursive: true, force: true })
try {
  execFileSync('openapi-ts', [], { cwd: root, env: { ...process.env, GEN_API_OUT: fresh }, stdio: 'pipe' })
  const expected = listFiles(fresh)
  const actual = listFiles(committed)
  const stale = [
    ...expected.filter((file) => !actual.includes(file)).map((file) => `missing: ${file}`),
    ...actual.filter((file) => !expected.includes(file)).map((file) => `extra: ${file}`),
    ...expected
      .filter((file) => actual.includes(file))
      .filter((file) => readFileSync(join(fresh, file), 'utf8') !== readFileSync(join(committed, file), 'utf8'))
      .map((file) => `changed: ${file}`),
  ]
  if (stale.length) {
    console.error('The generated API client is stale. Run `pnpm gen:api` (or `make gen-client`) and commit the result:')
    for (const line of stale) console.error(`  ${line}`)
    process.exitCode = 1
  } else {
    console.log('Generated API client is up to date.')
  }
} finally {
  rmSync(fresh, { recursive: true, force: true })
}
