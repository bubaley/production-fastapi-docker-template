# Template modernization roadmap

Approved plan for bringing the template to a stable, agent-friendly baseline. Each stage lands as its own commit series on `modernize/template`. When a stage is done, mark it here and move durable rules into the concept docs — this file describes work in progress, not conventions.

## Decisions

| Topic | Decision |
|---|---|
| Rendering | Hybrid. App routes (`/home/**`, `/settings/**`, `/auth`) render client-only via `routeRules` `ssr: false`; public pages use SSR or prerender with SEO/OG meta. Nitro stays for rendering only. |
| Auth | FastAPI owns auth completely: login/refresh/logout/me set and rotate HttpOnly cookies; the browser never sees tokens. Nitro forwards the request cookie to FastAPI during SSR. The Nitro auth proxy (`frontend/modules/base-auth`) is removed. CSRF: `SameSite=Lax` + Origin check on unsafe methods. `Authorization: Token` API tokens stay for integrations. |
| Data layer | OpenAPI-generated client (`@hey-api/openapi-ts`) + Pinia Colada (`useQuery` / `useMutation`). `appRepo`, hand-written codecs and `useRepoData` are removed after migration. |
| Frontend tooling | Vite+ (`vp fmt`, `vp lint`, `vp test`) for TS/script/format/tests; ESLint kept only for `*.vue` templates (`eslint-plugin-vue` + `eslint-plugin-oxlint`). Prettier removed. `nuxt dev` / `nuxt build` unchanged. TypeScript stays on 6.x (vue-tsc does not support 7). |
| Container | One image. s6-overlay: oneshot `migrate`, then longruns `backend`, `taskiq`, `frontend`, `caddy`; the container exits when a critical service dies. |
| Release | Version bump directly in `main`: after the CI gate passes on push to `main`, the same workflow computes the next version from conventional commits, commits `chore(release): vX.Y.Z [skip ci]` (only version files + `CHANGELOG.md`), tags, publishes the image, deploys. `deps`/`build` commits also release. |
| Registry | Yandex Container Registry. Attestations (SBOM, provenance) go to GHCR if YCR rejects them. |
| Forks | Git upstream + ownership map (`docs/template-ownership.md`, `.template-version`) + `/sync-template` skill now; copier later. |

## Stages

1. **Hygiene and critical fixes** — tenant scope fails closed; `OrganizationUser` update schema; bcrypt off the event loop; password pepper separated from `SECRET_KEY` with legacy-hash fallback; PyJWT instead of python-jose; one error envelope; dead code removed on both sides; doc drift fixed; `CLAUDE.md`; shadcn migration plan archived.
2. **Toolchain** — Vite+ hybrid lint/format/test; `knip`; architecture guard script; Makefile `check-backend`, `check-frontend`, `check` as the CI source of truth; pinned `packageManager`, `.python-version`, `.nvmrc`, `.editorconfig`; one reformat-only commit.
3. **Container and CI/CD** — `.dockerignore` allowlist; Node and Caddy from official images; pnpm cache; HEALTHCHECK + `/ready`; s6-overlay; Caddy fixes (static `/_nuxt/*`, forwarded headers, security headers, zstd); compose dev/prod split; single `ci.yaml` (changes → backend/frontend/image → gate → release → publish → deploy); Renovate/Dependabot, gitleaks, CODEOWNERS, PR template, PR-title check.
4. **Design system** — one `theme.css` with semantic shadcn tokens, status tones, palettes via `data-palette`; SCSS and `sass` removed; `components.json` + shadcn-vue CLI; missing primitives; one `AppButton` vocabulary; one date library (`@internationalized/date`), one icon set (`@lucide/vue`), self-hosted Inter; `/ui` showcase with variant matrices and theme/palette switch.
5. **API contract and data layer** — fix duplicate PUT/PATCH operationIds in `fastapi-ronin`; security schemes, error responses and short operationIds in OpenAPI; `make gen-client`; Pinia Colada; auth moved to FastAPI cookies; hybrid `routeRules`; 401 interceptor; repo auto-registration.
6. **Backend hardening** — `is_active`, `token_version`, refresh rotation, cookie path; login rate limit, email normalisation; request id, structured logs, optional OTel; websocket fan-out via Redis pub/sub; taskiq stream broker with result TTL; S3 service fixes; test factories and `auth_headers`; dependency updates.
7. **Agent tooling and forks** — `manage.py new-domain` + `/new-domain` skill, model/router auto-discovery; `/verify`, `design-system`, `add-shadcn-component` skills; hooks (block migrations, format on edit); `make init name=…`; `product.md` split into `template-core.md` + `product.md`; ownership map and `/sync-template`.

Order: 1 → 2 → (3, 4, 6 in parallel) → 5 → 7.

## Status

| Stage | Status |
|---|---|
| 1 | done |
| 2 | done |
| 3 | done |
| 4 | done |
| 5 | in progress |
| 6 | done |
| 7 | pending |

## Known follow-ups

- Stage 2: Oxlint runs without type-aware rules (tsgolint cannot resolve types exported from `.vue` files). `nuxt dev` prints `NUXT_B5004` for the Vite+ `vite.config.ts` (expected; Nuxt ignores the file).
- Stage 5: the refresh cookie path is `/api/v1/auth`; the Nitro auth proxy cannot see it, so session refresh in Nuxt is broken until the proxy is removed. Shorten the access-token lifetime (24h → ~15 min) once the 401 interceptor exists.
- Stage 3: none of the workflows have run on GitHub yet; registry/deploy variables and secrets are listed in [deployment.md](deployment.md).
- Stage 5: adding a member from the organization page uses the organization in the header (`Organization-Key`), not the organization being viewed. Fix with the new data layer.
- Optional data migration: lowercase existing `user.email` values so login can drop `iexact`.
