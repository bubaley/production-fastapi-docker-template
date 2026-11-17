# Image, CI/CD and deployment

How the production image is built, how a commit on `main` becomes a release, and how a release reaches the server. Local development without Docker for the app itself is in [README.md](../README.md).

Two deploy paths, both off until configured: the default **Yandex Container Registry + SSH** ([CI/CD](#cicd), [Releases](#releases)) and the optional **[Docker Hub + Dokploy](#docker-hub-and-dokploy)**. Both registries are targets of the same `publish` job (one build, pushed to each configured registry), so they can run side by side.

## The image

One image runs the whole application. Files: [`Dockerfile`](../Dockerfile), [`docker/rootfs/`](../docker/rootfs) (copied to `/`), [`Caddyfile`](../Caddyfile), [`.dockerignore`](../.dockerignore) (allowlist: only `backend/`, `frontend/`, `docker/` and `Caddyfile` reach the build).

| Stage | What it does |
|---|---|
| `python`, `node`, `caddy`, `uv` | Pinned base images, named once (Dependabot updates these `FROM` lines) |
| `s6` | Downloads s6-overlay (version + SHA-256 pinned per architecture) and verifies it |
| `backend-builder` | `uv sync --locked --no-dev` into `/app/backend/.venv` with a uv cache mount; compiles bytecode |
| `frontend-builder` | `pnpm fetch` from the lockfile, then an offline `pnpm install` and `nuxt build` → `/app/frontend/.output`; pnpm store on a cache mount. Same Debian release as the runtime |
| `runtime` | `python:*-slim-trixie` + Node binary from the official Node image + Caddy binary from the official Caddy image + s6-overlay. No package manager runs here; no curl, make or supervisor. Runs as `app` (uid 1000) |

Build arguments `APP_VERSION` and `GIT_SHA` become environment variables of the same name (the backend reports them) and OCI labels; `BUILD_DATE` sets `org.opencontainers.image.created`.

```bash
make docker-build   # IMAGE=fastapi-nuxt-template:local, APP_VERSION from version.json, GIT_SHA from git
make docker-run     # compose.yaml (PostgreSQL + Redis + IMAGE) as project <COMPOSE_PROJECT_NAME>-smoke; waits for healthy
make docker-stop    # stop it and delete its volumes
```

`make docker-run` reads `.env` like production does; sign in through the container at `http://127.0.0.1:8080` (the browser calls the API on that same origin).

### Processes (s6-overlay)

s6-overlay is PID 1 (`/init`). Services live in `docker/rootfs/etc/s6-overlay/s6-rc.d/`; the `user` bundle (`user-bundles.d/user/contents.d/`) lists them.

| Service | Type | Command | Listens |
|---|---|---|---|
| `migrate` | oneshot | `scripts/migrate`: waits for PostgreSQL (`wait-for-db.py`, `DB_WAIT_TIMEOUT`, default 60 s), then `python -m tortoise migrate` | — |
| `backend` | longrun, after `migrate` | `uvicorn app.main:app --workers $BACKEND_WORKERS --proxy-headers --forwarded-allow-ips 127.0.0.1 --timeout-graceful-shutdown 20` | 127.0.0.1:8000 |
| `taskiq-worker` | longrun, after `migrate` | `taskiq worker app.core.broker:broker --workers $TASKIQ_WORKERS` | — |
| `taskiq-scheduler` | longrun, after `migrate` | `taskiq scheduler app.core.broker:scheduler` (`TASKIQ_SCHEDULER=false` turns it off) | — |
| `frontend` | longrun, after `migrate` | `node .output/server/index.mjs` | 127.0.0.1:3000 |
| `caddy` | longrun, after `migrate` | `caddy run --config /etc/caddy/Caddyfile` | **:8080** (the only exposed port) |

Failure policy — the container exits instead of limping:

- `migrate` fails (database unreachable, broken migration) → `S6_BEHAVIOUR_IF_STAGE2_FAILS=2` stops the container with a non-zero code.
- A longrun exits while it is still wanted up (crash, OOM kill, even a clean exit) → its `finish` script (`scripts/service-finish`) writes the exit code (`128 + signal` for signals) and halts the container. Docker's `restart: unless-stopped` (or the orchestrator) starts a fresh container, which re-runs `migrate`.
- A deliberate stop (`docker stop`, deploy) is not a crash: services get SIGTERM, uvicorn and Caddy drain for up to 20 s (`S6_SERVICES_GRACETIME=25000`), and the container exits 0. Compose gives it `stop_grace_period: 40s`.

All output goes to the container's stdout/stderr (`docker compose logs app`); Caddy access logs are JSON.

### Caddy

| Route | Goes to |
|---|---|
| `/healthz` | `200 ok` from Caddy itself (not logged) |
| `/api/v1/*` | backend; request body limit `API_MAX_BODY_SIZE` (default `25MB`) |
| `/ws/*` | backend (websockets) |
| `/_nuxt/*` | files from `/app/frontend/.output/public`, `Cache-Control: public, max-age=31536000, immutable`, precompressed variants when present |
| everything else | Nuxt (including the Nitro auth routes under `/api/auth/*`) |

Global options: admin API off, automatic HTTPS off (TLS terminates upstream), `trusted_proxies private_ranges` (forwarded headers from the load balancer / host proxy are honoured), 20 s grace period. Every response gets `X-Content-Type-Options`, `Referrer-Policy`, `X-Frame-Options: DENY`, `Permissions-Policy`, `Content-Security-Policy: frame-ancestors 'none'` (unless the app sets its own CSP); `Server`, `Via` and `X-Powered-By` are removed; responses are compressed with zstd or gzip. Set HSTS on the TLS-terminating proxy.

### Health endpoints

| Endpoint | Port | Meaning |
|---|---|---|
| `GET /healthz` | 8080 (public) | Caddy is up |
| `GET /health` | 8000 (internal) | Backend process is alive |
| `GET /ready` | 8000 (internal) | Backend can reach PostgreSQL and Redis (200 / 503) |

The image `HEALTHCHECK` (`/usr/local/bin/healthcheck`, Python stdlib, every 15 s) requires all three layers: Caddy `/healthz` 200, Nuxt answering below 500, backend `/ready` 200 — or `/health` 200 when the backend build has no `/ready` yet. `docker compose up --wait` and the deploy step rely on it.

### Environment

The container reads the same settings as local development (`.env.example`). Production-specific:

| Variable | Default | Purpose |
|---|---|---|
| `APP_IMAGE` | `fastapi-nuxt-template:local` | Image compose runs; the deploy step pins it to `registry/name@sha256:…` in the server's `.env` |
| `APP_ENTRY_PORT` | `127.0.0.1:8080` | Host binding of Caddy's port; keep it on loopback behind a host proxy |
| `REDIS_PASSWORD` | empty | Optional; Redis requires it and compose puts it into `REDIS_URL` / `BROKER_REDIS_URL`. Use URL-safe characters (e.g. `openssl rand -hex 32`) |
| `BACKEND_WORKERS` | `2` | uvicorn worker processes |
| `TASKIQ_WORKERS` | `1` | Taskiq worker processes |
| `TASKIQ_SCHEDULER` | `true` | Run the scheduler in this container; keep exactly one per deployment |
| `RUN_MIGRATIONS` | `true` | `false` skips the `migrate` oneshot (run migrations elsewhere) |
| `DB_WAIT_TIMEOUT` | `60` | Seconds `migrate` waits for PostgreSQL |
| `API_MAX_BODY_SIZE` | `25MB` | Caddy request body limit for `/api/v1/*` |
| `NUXT_API_INTERNAL_URL` | `http://127.0.0.1:8000` | FastAPI as seen from the Nuxt server during SSR (set by the `frontend` service). Browsers never use it: they call `/api/v1` and `/ws` on the public origin through Caddy |
| `SETUP_TOKEN` | empty | While the database has no users, the first-run setup (`/setup`) is open to anyone who reaches the site; set this (e.g. `openssl rand -hex 16`) and the setup also asks for it. Meaningless once the first user exists |
| `APP_VERSION`, `GIT_SHA` | baked in | Set by the build; do not override |

`compose.yaml` forces `DEBUG=False`, `COOKIE_SECURE=True` and the in-network database/Redis addresses for the app.

## Compose

| File | Use |
|---|---|
| `compose.yaml` | Production: `app` (from `APP_IMAGE`), `db` (PostgreSQL 18), `redis` (Redis 8, AOF). Healthchecks, log rotation (json-file, 5 × 10 MB), stop grace periods. Only the app port is published |
| `compose.dokploy.yaml` | Optional [Dokploy](#docker-hub-and-dokploy) stack: the same services, the app image from Docker Hub (`APP_IMAGE` required), no host ports, `app` on Dokploy's `dokploy-network` |
| `compose.override.yaml` | Local development only, merged automatically by `docker compose`: `db` on `127.0.0.1:$SQL_PORT`, `redis` on `127.0.0.1:$REDIS_PORT`, `app` buildable. Never copied to servers |

Development uses `docker compose up -d db redis`; `make docker-run` uses `-f compose.yaml` only.

## CI/CD

One workflow, [`.github/workflows/ci.yaml`](../.github/workflows/ci.yaml):

```
pull_request / push to main
  changes ──┬─ backend     (if backend/**, Makefile, .python-version: PostgreSQL 18 + Redis services, make check-backend)
            ├─ frontend    (if frontend/**, .nvmrc: make check-frontend)
            ├─ pre-commit  (always, make check-hygiene: yaml, eol, whitespace, large files, pyupgrade, bandit, uv lock, pyproject-fmt;
            │               gitleaks over the new commits)
            └─ image       (if any code or infra changed: buildx + GHA cache, nuxt build, compose smoke test, Trivy)
                 └─ gate   (always; the only required check; path-skipped jobs are allowed)
push to main only:
  gate ─ release ─ publish (Yandex CR and/or Docker Hub) ─ deploy
```

- Pull requests run only the jobs their paths need (compared with the base branch). Pushes to `main` compare with the last `vX.Y.Z` tag: everything changed since the last release is checked again, so every release was checked on `main`, while a docs-only push right after a release skips backend, frontend and image. Manual runs and a repository without tags run everything.
- Concurrency: one run per ref; pull request runs cancel older ones, `main` runs never do.
- The image job builds the image with `load: true` (the only `nuxt build` in CI), starts `compose.yaml` with it (PostgreSQL + Redis), waits for the healthcheck, then checks `/healthz`, that `/` renders the Nuxt app, that a `/_nuxt/*` asset is immutable-cached, and that `/api/v1/auth/me` returns the backend's 401 JSON. Trivy fails the job on CRITICAL vulnerabilities that have a fix; it scans every image on `main`, and on pull requests only when `Dockerfile`, `docker/` or a lockfile changes.
- Build cache: one GitHub Actions cache scope (`app-image`, `mode=max`). Only runs on `main` write it (the export takes about a minute); pull requests and `publish` only read it. A cache export error never fails the build.

Other workflows:

| Workflow | Does |
|---|---|
| `pr-title.yaml` | PR title must be a conventional commit (`type(scope): subject`); squash merges make it the commit message |
| `security.yaml` | Weekly (and manual) Trivy scan of the repository: dependencies, secrets, misconfiguration. Secrets in new commits are checked by gitleaks in the CI `pre-commit` job and by the local pre-commit hook |
| `rollback.yaml` | Manual: redeploy a release by its image digest |

Dependabot (`.github/dependabot.yml`) opens grouped minor/patch PRs: uv and npm weekly; GitHub Actions, the Dockerfile and compose images monthly; each after a short cooldown. It never proposes a new Python minor (3.16) or Node major for the Dockerfile, nor a PostgreSQL/Redis major: those change the runtime or need a data migration, so bump them by hand (with `.python-version` / `.nvmrc`). Keep the uv image in the Dockerfile, `UV_VERSION` in `ci.yaml` and the `uv-pre-commit` rev on one version, and the CI service images in `ci.yaml` on the versions in `compose.yaml`. Third-party actions are pinned by commit SHA with the version in a comment; Dependabot keeps both in sync.

## Releases

On every push to `main` that passes the gate, the `release` job:

1. Stops quietly (notice, success) if `main` has moved past the tested commit — the newer commit's run releases.
2. Computes the next version with [git-cliff](https://git-cliff.org) (`cliff.toml`) from the conventional commits since the last `vX.Y.Z` tag:

   | Commits since the last tag | Bump |
   |---|---|
   | any `!` (`feat!:`) or `BREAKING CHANGE:` footer | major |
   | `feat` | minor |
   | `fix`, `perf`, `revert`, `build`, `chore(deps)` / `chore(deps-dev)` | patch |
   | only `docs`, `chore`, `ci`, `refactor`, `style`, `test` | no release |

3. Writes the version to `version.json`, regenerates `CHANGELOG.md`, commits `chore(release): vX.Y.Z [skip ci]`, creates an annotated tag and pushes both atomically. If the push loses a race with another merge it skips quietly; any other rejection fails the job. `backend/pyproject.toml` and `frontend/package.json` keep a fixed `0.0.0`: the release commit touches nothing in the Docker build context, so `publish` reuses every cached layer. The running app gets its version from the `APP_VERSION` build argument.
4. Creates the GitHub Release with that version's changelog section.

The release commit carries `[skip ci]`, so it does not start another pipeline. Version files are never edited by hand.

`publish` checks out the tag, builds the image once from the CI build cache and pushes it to every configured registry: Yandex Container Registry as `cr.yandex/<YC_REGISTRY_ID>/<IMAGE_NAME>` and/or [Docker Hub](#docker-hub-and-dokploy) (`DOCKERHUB_USERNAME`). Tags: `X.Y.Z`, `X.Y`, `sha-<short>` and `latest`. Attestations are decided per registry: Yandex CR does not accept attestation manifests (the push fails with `Cannot read manifest data`), so it always gets a plain image; Docker Hub gets SBOM and provenance attestations by default. `ATTESTATIONS` applies to Docker Hub only: `registry` (default), `ghcr` (plain images, an attested copy goes to `ghcr.io/<owner>/<repo>:X.Y.Z`) or `off`. With both registries the job pushes Yandex CR first and Docker Hub second from the same build (a cache hit), so the two digests differ when Docker Hub carries attestations; `deploy` and [Rollback](#rollback) use the Yandex CR digest when it is configured, else the Docker Hub one. The job summary shows each registry's digest and the tags.

*Run workflow* on **CI** with `republish` set to a tag (`v1.4.2`) skips the checks and the release and runs only `publish` for that tag, e.g. after configuring a new registry. Republishing a tag that is not the newest moves neither `latest` nor `X.Y` and does not deploy (use [Rollback](#rollback)).

`deploy` runs for the newest release only. It runs [`.github/actions/deploy`](../.github/actions/deploy/action.yml) in the `production` environment (one at a time, never cancelled): it uploads `compose.yaml` to the server over SSH, sets `APP_IMAGE=<image>@<digest>` in the server's `.env` (the Yandex CR image, or the Docker Hub one when that is the only registry), pulls and runs `docker compose up -d --wait`. If the new container does not become healthy within 5 minutes, it restores the previous `APP_IMAGE` and fails. Each deploy is appended to `deploy-history.log` next to the compose file. To deploy elsewhere (Kubernetes, a managed service), replace that action and keep its inputs.

Migrations run when the new container starts, before it serves traffic, while the old container is already stopped: a single-server deploy has a short restart gap. Keep migrations backward compatible with the previous release (expand, then contract in a later release) so the automatic restore and `rollback.yaml` stay safe.

### Rollback

Actions → **Rollback** → *Run workflow* with the release tag (`v1.4.2`). It resolves the digest of `<image>:1.4.2` in the registry the deploy job uses (Yandex CR, or Docker Hub when that is the only one) and deploys it with that release's `compose.yaml`, through the same deploy action and lock as `deploy`. Database migrations are not reversed.

## Setup checklist (repository owner)

Repository **variables** (Settings → Secrets and variables → Actions → Variables):

| Variable | Needed for | Example |
|---|---|---|
| `YC_REGISTRY_ID` | publish | `crp1a2b3c4d5e6f7g8h9` |
| `IMAGE_NAME` | publish | `my-app` |
| `YC_SA_ID` | publish, keyless (optional) | service account id for [workload identity federation](https://yandex.cloud/en/docs/iam/tutorials/wlif-github-integration) |
| `ATTESTATIONS` | publish (optional) | Docker Hub only: `registry` (default), `ghcr` or `off`. Yandex CR always gets images without attestations (it rejects them) |
| `RELEASE_APP_CLIENT_ID` | release past branch protection | GitHub App client id |
| `DEPLOY_ENABLED` | deploy, rollback | `true` |
| `DEPLOY_PATH` | deploy (optional) | `/opt/app` (default) |

**Secrets** (repository, or the `production` environment for the `DEPLOY_*` ones):

| Secret | Needed for |
|---|---|
| `YC_KEY_JSON` | publish, rollback — authorized key JSON of a service account with `container-registry.images.pusher` (not needed with `YC_SA_ID`) |
| `RELEASE_APP_PRIVATE_KEY` | release — private key of the GitHub App |
| `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_SSH_KEY` | deploy, rollback — SSH target; the user must be in the `docker` group |
| `DEPLOY_KNOWN_HOSTS` | deploy, rollback — output of `ssh-keyscan <host>`; without it the host key is trusted on first use (warning) |

Docker Hub (`DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`, optional `DOCKERHUB_IMAGE` and `DOKPLOY_DEPLOY_WEBHOOK`): see [Docker Hub and Dokploy](#docker-hub-and-dokploy).

Without a registry (`YC_REGISTRY_ID`/`IMAGE_NAME` or `DOCKERHUB_USERNAME`) the pipeline still releases (tag, changelog, GitHub Release) and skips publish and deploy; without `DEPLOY_ENABLED=true` it publishes and skips deploy.

### Branch protection and the release bypass

1. Protect `main` with a ruleset: require pull requests, require the status check **CI gate** (and **Conventional PR title**), allow squash merges only.
2. The release job pushes a commit and a tag to `main`. `GITHUB_TOKEN` cannot bypass rules, so create a GitHub App (permissions: *Contents: read and write*; no webhook), install it on the repository, and add it to the ruleset's **bypass list**. Store its client id in `RELEASE_APP_CLIENT_ID` and a private key in `RELEASE_APP_PRIVATE_KEY`. Without them the job uses `GITHUB_TOKEN`, which works only while `main` is unprotected.
3. If tags are protected by a ruleset, add the same app to that bypass list.

### Server

1. Install Docker Engine with the Compose plugin; create the deploy user in the `docker` group.
2. Let the server pull from Yandex CR: attach a service account with `container-registry.images.puller` to the VM and configure the [Docker credential helper](https://yandex.cloud/en/docs/container-registry/operations/authentication), or `docker login cr.yandex` once with a pull-only key. The pipeline never copies its push credentials to the server.
3. Create `DEPLOY_PATH` with a `.env` built from `.env.example`: real `SECRET_KEY`, `ENCRYPTION_KEY`, `PASSWORD_PEPPER`, `SQL_PASSWORD`, `REDIS_PASSWORD` and `COMPOSE_PROJECT_NAME`. The first deploy adds `APP_IMAGE` and `compose.yaml`.
4. Terminate TLS in front of `APP_ENTRY_PORT` (host Caddy/nginx or a cloud load balancer) and set HSTS there.
5. First user: open the site and complete «Первый запуск» (`/setup`); it is open only while there are no users, and the API logs a warning at startup until then. Set `SETUP_TOKEN` in `.env` if the site is reachable by others before you finish. Shell alternative: `docker compose exec -w /app/backend app python -m manage create_superuser`.

---

## Docker Hub and Dokploy

An optional, simpler alternative to the registry + SSH deploy: the CI `publish` job pushes each release image to Docker Hub ([`ci.yaml`](../.github/workflows/ci.yaml)) and [Dokploy](https://dokploy.com) runs [`compose.dokploy.yaml`](../compose.dokploy.yaml) from this repository (app from Docker Hub + PostgreSQL + Redis, no host ports; Dokploy's Traefik terminates TLS).

**Docker Hub publishing.** Docker Hub is one more target of `publish` and stays off until `DOCKERHUB_USERNAME` is set, so forks that do not use it see no failures. Each new release is pushed (the same build and digest as the Yandex CR image when both are on) unless Docker Hub already has that version; commits that make no release push nothing. *Run workflow* on **CI** with `republish` = a tag pushes that release again; an older tag does not move `latest`. Repository → Settings → Secrets and variables → Actions:

| Kind | Name | Value |
|---|---|---|
| Variable | `DOCKERHUB_USERNAME` | Docker Hub user or organization; turns Docker Hub publishing on |
| Secret | `DOCKERHUB_TOKEN` | Docker Hub personal access token, scope *Read & Write* |
| Variable (optional) | `DOCKERHUB_IMAGE` | repository; a bare name gets the user's namespace. Default `<DOCKERHUB_USERNAME>/fastapi-nuxt-template` (`DOCKERHUB_REPOSITORY` in `ci.yaml` and `rollback.yaml`; `make init` renames it) |
| Secret (optional) | `DOKPLOY_DEPLOY_WEBHOOK` | the Dokploy service's deploy webhook; called after a push that moved `latest`, so Dokploy redeploys with the new image |

Tags: `X.Y.Z`, `X.Y`, `sha-<short>` and `latest`, with the same build arguments and OCI labels as the registry image. A private Docker Hub repository also needs its credentials in Dokploy (Settings → Registry).

**Dokploy.**

1. *Create Service* → **Compose**; provider GitHub, this repository, branch `main`, compose path `./compose.dokploy.yaml`. Keep *Autodeploy* off when `DOKPLOY_DEPLOY_WEBHOOK` is set: a push would redeploy before the new image exists.
2. *Environment* (Dokploy writes it to `.env` next to the compose file): `APP_IMAGE` (`<DOCKERHUB_USERNAME>/fastapi-nuxt-template:latest`, or a version tag to pin), `SECRET_KEY` (≥ 64 chars), `ENCRYPTION_KEY` (exactly 32 chars), `PASSWORD_PEPPER`, `SQL_PASSWORD`, `REDIS_PASSWORD` (URL-safe), plus any other setting from `.env.example` the product needs (`AWS_*`, `BACKEND_WORKERS`, `TASKIQ_WORKERS`). Never change `SECRET_KEY`, `ENCRYPTION_KEY` or `PASSWORD_PEPPER` after the first deploy.
3. *Domains*: the host, service `app`, container port **8080**, HTTPS (Let's Encrypt). Set HSTS in Traefik if needed.
4. Deploy. Migrations run when the container starts; `app` is healthy once the image `HEALTHCHECK` passes.
5. First user: open the domain and complete «Первый запуск» (`/setup`; add `SETUP_TOKEN` to the environment to protect it), or *Terminal* of the `app` container → `cd /app/backend && python -m manage create_superuser`.

Back up the `postgres_data` volume (Dokploy volume backups or a scheduled `pg_dump`). Rollback: set `APP_IMAGE` to the previous version tag and redeploy; migrations are not reversed.
