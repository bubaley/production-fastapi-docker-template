# Changelog

All notable changes to this project are documented in this file.
It is generated from conventional commits by the release job; do not edit it by hand.

## [0.9.0] - 2026-10-22

### Features
- **auth:** cookie-only sessions with an Origin check for unsafe requests (0650667)
- **api:** stable OpenAPI contract and make openapi (f49a5ff)
- **frontend:** cookie session, generated client and Pinia Colada data layer (2c5383c)
- **frontend:** server-rendered public landing page (6ac4ab0)
- **backend:** auto-discover domain models and routers (48cfb52)
- **tooling:** scaffold a domain with make new-domain (4daf6c4)
- **tooling:** bootstrap a new product with make init (72e7404)
- **tooling:** Claude Code hooks that block migrations and format edits (04c7c0c)
- **tooling:** Claude Code skills and review subagents (863be09)

### Bug fixes
- **organization:** add members to the organization named in the body (8920083)
- **tooling:** ignore here-documents and quoted newlines in the migration hook (3a04bc5)
- **tooling:** point make init next steps at make createsuperuser (32c666a)
- **backend:** build the database pool at startup and shield the readiness probe (7b8361e)

### Build
- **frontend:** generate a typed API client from openapi.json (8dbd191)
## [0.8.0] - 2026-10-22

### Features
- **backend:** make tenant scoping fail closed (b2cc155)
- **auth:** token versioning, refresh rotation and login protection (6b7e9ec)
- **core:** request id, structured logging, /ready and resilient lifespan (5f89136)
- **ws:** Redis pub/sub fan-out, send timeouts and access re-checks; taskiq stream broker (e4f5245)
- **ui:** rebuild /ui showcase with variant, size and tone matrices (e32913d)
- **ui:** single token layer, tones, control sizes and theme switch (edc3fec)
- **db:** migration for auth token lifecycle (82383cf)
- modernize template toolchain, design system, container and backend (#2) (df65861)

### Bug fixes
- **frontend:** derive websocket URL from API or page origin (e066a94)
- **ui:** use Russian copy for theme toggle and empty value (85b325f)
- **auth:** move bcrypt off the event loop and decouple password pepper from SECRET_KEY (a2cb571)
- **organization:** give memberships an explicit update schema (bcad8dc)
- **core:** return one error envelope for every exception (e471204)
- **organization:** keep memberships immutable in the members modal (1f697d8)
- **ui:** use an arrow function for the multi-statement save handler (c97dd6f)
- **s3:** private uuid keys, streaming uploads and presigned URLs (59ad5d0)
- **api:** stable pagination with an id tiebreaker (1a2d76f)
- **ui:** default to the violet palette to keep the original accent (842b609)

### Dependencies
- **deps:** remove unused frontend dependencies (580b0bc)

### Build
- **backend:** replace python-jose with PyJWT and prune dependencies (df72fca)
- **frontend:** adopt Vite+ for lint, format and tests (57cf566)
- pin Python and Node versions and editor defaults (0572cb5)
- **make:** add check targets and read .env safely (f2d64b9)
- **backend:** update dependencies, drop gunicorn, add otel extra (368fa3c)
- **ui:** configure shadcn-vue CLI and add missing primitives (e97b61c)
- **docker:** run one image under s6-overlay with Caddy in front (02544cf)
- **compose:** split production compose from local dev overrides (eeb3e00)
- **docker:** pin base images in FROM lines so Dependabot can update them (a1f8b41)
## [0.7.0] - 2026-10-22

### Features
- **fields:** add dedicated schema list field (10dbb63)
- **template:** migrate UI to shadcn-vue and harden application flows (cd90844)

### Bug fixes
- **ui:** track shared shadcn class helper (4f55e35)
## [0.6.0] - 2026-08-19

### Features
- enhance UI components by adding AppTabs, updating AppMenu and AppPopover, and refactoring tooltip implementation (7a87b99)
- update frontend documentation to include AppModal and AppConfirmModal components with usage examples (3ba52ed)
## [0.5.0] - 2026-08-19

### Features
- add AGENTS.md for agent instructions, update README and architecture documentation, and refactor Docker container names for consistency (87c258d)

### Bug fixes
- add production migration step to Makefile and update lint-backend command (1849900)
- update environment configuration, Docker setup, and dependencies for improved development and production workflow (ff76f81)
## [0.4.0] - 2026-07-08

### Features
- add 'name' field to UserToken model and update related schemas and views (b7d052b)
## [0.3.0] - 2026-07-08

### Features
- implement useListEvents composable and refactor related components (e4e96a1)
## [0.2.0] - 2026-07-08

### Features
- integrate excaptions handling (ea37e95)
- edit work with tokens (9ba53b7)

### Bug fixes
- upgrade packages, integrate ty (12df3a1)
- integrate migrations and keepdb for tests (7ef80a2)
- bugs in frontend (59e3e06)
- change settings (a74309c)
## [0.1.0] - 2026-06-14

### Features
- refactor components, add example configuration files for VSCode and update dependencies, add ui view (47af0de)
## [0.0.1] - 2026-06-12

### Bug fixes
- fix errors, format components (96c8415)
