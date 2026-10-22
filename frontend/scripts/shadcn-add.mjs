// Adds shadcn-vue primitives into app/shared/ui/shadcn/<name>/ and normalizes them to project conventions.
// Usage: pnpm ui:add tooltip badge
// The new-york-v4 registry currently imports `cn` from a package named "cn" and lists it as a dependency;
// this script rewrites that import to `~/shared/lib/utils`, uninstalls the stray package and formats the output.
import { execFileSync } from 'node:child_process'
import fs from 'node:fs'
import path from 'node:path'

const CLI_VERSION = '2.8.2'
const root = path.resolve(import.meta.dirname, '..')
const shadcnDir = path.join(root, 'app/shared/ui/shadcn')
const names = process.argv.slice(2)

if (!names.length) {
  console.error('Usage: pnpm ui:add <component> [...components]')
  process.exit(1)
}

const run = (command, args) => execFileSync(command, args, { cwd: root, stdio: 'inherit' })

run('pnpm', ['dlx', `shadcn-vue@${CLI_VERSION}`, 'add', ...names, '--yes'])

const walk = (dir) =>
  fs
    .readdirSync(dir, { withFileTypes: true })
    .flatMap((entry) => (entry.isDirectory() ? walk(path.join(dir, entry.name)) : [path.join(dir, entry.name)]))

for (const file of walk(shadcnDir).filter((item) => /\.(vue|ts)$/.test(item))) {
  const source = fs.readFileSync(file, 'utf8')
  const next = source
    .replace(/from (['"])cn\1/g, "from '~/shared/lib/utils'")
    .replace(/(['"])@\/shared\//g, '$1~/shared/')
  if (next !== source) fs.writeFileSync(file, next)
}

const pkg = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8'))
if (pkg.dependencies?.cn || pkg.devDependencies?.cn) run('pnpm', ['remove', 'cn'])

run('pnpm', ['exec', 'vp', 'fmt', 'app/shared/ui/shadcn'])
console.log(
  '\nReview the generated files: use theme tokens (see docs/frontend-concept.md), then wrap them in shared/ui/app.',
)
