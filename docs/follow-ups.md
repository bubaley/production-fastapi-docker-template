# Follow-ups

Open items after the 2026 modernization ([archive/roadmap-2026.md](archive/roadmap-2026.md)). Template-owned. Remove an item in the change that resolves it.

## Upstream and tooling

- **fastapi-ronin PUT/PATCH workaround.** `split_put_patch_routes` in `backend/app/core/openapi.py` (called in `main.py`) splits ronin's combined PUT/PATCH route so operationIds stay unique. The fix (separate `update`/`partial_update` routes, partial PATCH body) is on ronin branch `fix/split-put-patch-operations`, not released. After upgrading ronin: delete the function and its call, run `make gen-client` (PATCH bodies become `Patched<UpdateSchema>`) and check the resource descriptors still typecheck.
- **Oxlint type-aware rules** are off: tsgolint cannot resolve types exported from `.vue` files. Re-enable when it can.
- `nuxt dev` prints `NUXT_B5004` for the Vite+ `vite.config.ts` — expected (Nuxt ignores the file).

## CI/CD

- None of the workflows has run on GitHub yet. Registry and deploy variables and secrets are listed in [deployment.md](deployment.md#setup-checklist-repository-owner).

## Data

- Optional data migration: lowercase existing `user.email` values so login can drop `iexact`.

## Forks and agent tooling

- **copier** for template updates (decision "Forks": git upstream + ownership map now, copier later). Revisit when several forks exist and `/sync-template` conflicts repeat.
- `/sync-template` has not been exercised on a real fork yet; the first run should confirm the ownership map and the tag fallback for repositories created with "Use this template" (no shared history: `.template-version` `commit` is the fork's first commit, so the sync falls back to tag `v<version>`).
- `make new-domain` generates one `name` field and a settings screen. Field specs (`fields="title:str amount:decimal"`) and non-settings placement are not supported; agents add fields by hand.
