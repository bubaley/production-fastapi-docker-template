---
name: sync-template
description: Pull improvements from the upstream FastAPI + Nuxt template into a product created from it, path by path according to the ownership map. Use when the user asks to sync, update or upgrade from the template, pull template changes, or runs /sync-template in a fork.
---

# Sync template

Ownership and conflict rules: [docs/template-ownership.md](../../../docs/template-ownership.md). Never touch product-owned paths; never copy template migrations.

**0. Preconditions.** Clean tree (`git status`), `make check` green, `.template-version` has `repository` and `commit` (empty commit → the product was not created with `make init`: ask the user which template commit or version it started from and write it first). Work on a branch: `git switch -c chore/template-sync`.

**1. Fetch** (template tags go to their own namespace so the fork's release job never sees them):
```bash
git remote get-url template || git remote add template <repository from .template-version>
git fetch --no-tags template main '+refs/tags/v*:refs/template-tags/v*'
```

**2. Base and target.** `BASE` = `commit` from `.template-version` if `git cat-file -e <commit>^{commit}` succeeds, else `refs/template-tags/v<version>`. `TARGET` = `template/main` (or a tag the user names). Nothing to do if `git diff --quiet BASE TARGET`.

**3. Plan.** `git diff --name-status BASE TARGET` → classify every path with the ownership table (first matching row). Show the user the plan grouped by area (backend kernel, frontend kit, docs, tooling, infra) with counts per owner class before changing anything.

**4. Apply, one area at a time** (commit or at least checkpoint between areas):
- *template*, unchanged in the fork (`git diff --quiet BASE HEAD -- <path>`, or the path is absent in both): `git checkout TARGET -- <path>`; deleted upstream → `git rm <path>`.
- *template* changed in the fork, and every *shared* path: 3-way merge — `git show HEAD:<p> > /tmp/ours`, `git show BASE:<p> > /tmp/base`, `git show TARGET:<p> > /tmp/theirs`, `git merge-file /tmp/ours /tmp/base /tmp/theirs`, copy back, resolve markers by the rules (product values win, template structure wins). Local deviations that must stay → note them for `docs/product.md` "Changes to template behavior".
- *product*: skip; if the template change requires a product edit (renamed API, new required field), list it as a follow-up.
- *generated*: skip now, regenerate in step 5.
- `backend/migrations/**`: never copy. If kernel models changed (`git diff BASE TARGET -- 'backend/app/domains/*/models.py' backend/app/core`), the fork needs its own migration.

**5. Regenerate and verify.**
- Manifests changed → `cd backend && uv lock`, `pnpm --dir frontend install`.
- `make gen-client`, `make lint`, `make check` (`PYTEST_ARGS=--sqlite` while a kernel migration is pending).
- Models changed → tell the user to run `make mm` then `make m` (do not run them).
- UI kit changed → `design-system` skill visual review of `/ui` and product screens.

**6. Record.** Rewrite `.template-version`: `version=` from `git show TARGET:version.json`, `commit=$(git rev-parse TARGET)`, keep `repository`. Commit: `chore(template): sync to v<version> (<sha7>)`; use `feat(template)`/`fix(template)` instead when the sync brings user-visible changes, so the release job bumps.

**7. Summarize** for the user: base → target, files taken / merged / skipped (product) / regenerated, conflicts and how they were resolved, local deviations recorded, migration needed (yes/no), follow-ups.
