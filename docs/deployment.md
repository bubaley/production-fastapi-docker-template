# Image, CI/CD and deployment

How the production image is built, how a commit on `main` becomes a release, and how a release reaches the server. Local development without Docker for the app itself is in [README.md](../README.md).

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

`make docker-run` reads `.env` like production does; set `NUXT_PUBLIC_BASE_URL=http://127.0.0.1:8080` there to sign in through the container at `http://127.0.0.1:8080`.

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
| `NUXT_PUBLIC_BASE_URL` | — | Public origin of the API (e.g. `https://app.example.com`); the Nitro auth proxy calls it during SSR until [roadmap](roadmap.md) stage 5 removes that proxy |
| `APP_VERSION`, `GIT_SHA` | baked in | Set by the build; do not override |

`compose.yaml` forces `DEBUG=False`, `COOKIE_SECURE=True` and the in-network database/Redis addresses for the app.

## Compose

| File | Use |
|---|---|
| `compose.yaml` | Production: `app` (from `APP_IMAGE`), `db` (PostgreSQL 18), `redis` (Redis 8, AOF). Healthchecks, log rotation (json-file, 5 × 10 MB), stop grace periods. Only the app port is published |
| `compose.override.yaml` | Local development only, merged automatically by `docker compose`: `db` on `127.0.0.1:$SQL_PORT`, `redis` on `127.0.0.1:$REDIS_PORT`, `app` buildable. Never copied to servers |

Development uses `docker compose up -d db redis`; `make docker-run` uses `-f compose.yaml` only.

## CI/CD

One workflow, [`.github/workflows/ci.yaml`](../.github/workflows/ci.yaml):

```
pull_request / push to main
  changes ──┬─ backend     (if backend/**, Makefile, .python-version: PostgreSQL 18 + Redis services, make check-backend)
            ├─ frontend    (if frontend/**, .nvmrc: make check-frontend BUILD=1)
            ├─ pre-commit  (always: yaml, eol, whitespace, large files, pyupgrade, bandit, uv lock, pyproject-fmt)
            └─ image       (if any code or infra changed: buildx + GHA cache, compose smoke test, Trivy)
                 └─ gate   (always; the only required check; path-skipped jobs are allowed)
push to main only:
  gate ─ release ─ publish ─ deploy
```

- Pull requests run only the jobs their paths need; pushes to `main` run everything.
- Concurrency: one run per ref; pull request runs cancel older ones, `main` runs never do.
- The image job builds the image with `load: true`, starts `compose.yaml` with it (PostgreSQL + Redis), waits for the healthcheck, then checks `/healthz`, that `/` renders the Nuxt app, that a `/_nuxt/*` asset is immutable-cached, and that `/api/v1/auth/me` returns the backend's 401 JSON. Trivy fails the job on CRITICAL vulnerabilities that have a fix.

Other workflows:

| Workflow | Does |
|---|---|
| `pr-title.yaml` | PR title must be a conventional commit (`type(scope): subject`); squash merges make it the commit message |
| `security.yaml` | gitleaks on the commits of every PR and push to `main`; weekly Trivy scan of the repository (dependencies, secrets, misconfiguration) |
| `rollback.yaml` | Manual: redeploy a release by its image digest |

Dependabot (`.github/dependabot.yml`) opens weekly grouped minor/patch PRs for uv, npm, GitHub Actions, the Dockerfile and compose images. Third-party actions are pinned by commit SHA with the version in a comment; Dependabot keeps both in sync.

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

3. Writes the version to `version.json`, `backend/pyproject.toml` (+ `uv.lock`, via `uv version`) and `frontend/package.json`, regenerates `CHANGELOG.md`, commits `chore(release): vX.Y.Z [skip ci]`, creates an annotated tag and pushes both atomically. If the push loses a race with another merge it skips quietly; any other rejection fails the job.
4. Creates the GitHub Release with that version's changelog section.

The release commit carries `[skip ci]`, so it does not start another pipeline. Version files are never edited by hand.

`publish` checks out the tag and pushes the image to Yandex Container Registry as `cr.yandex/<YC_REGISTRY_ID>/<IMAGE_NAME>` with tags `X.Y.Z`, `X.Y`, `sha-<short>` and `latest`, reusing the CI build cache. SBOM and provenance attestations are attached by default. If the registry rejects attestation manifests, set `ATTESTATIONS=ghcr`: the Yandex image is pushed without them and an attested copy goes to `ghcr.io/<owner>/<repo>:X.Y.Z` (`ATTESTATIONS=off` disables both). The job summary shows `image@digest`.

`deploy` runs [`.github/actions/deploy`](../.github/actions/deploy/action.yml) in the `production` environment (one at a time, never cancelled): it uploads `compose.yaml` to the server over SSH, sets `APP_IMAGE=<image>@<digest>` in the server's `.env`, pulls and runs `docker compose up -d --wait`. If the new container does not become healthy within 5 minutes, it restores the previous `APP_IMAGE` and fails. Each deploy is appended to `deploy-history.log` next to the compose file. To deploy elsewhere (Kubernetes, a managed service), replace that action and keep its inputs.

Migrations run when the new container starts, before it serves traffic, while the old container is already stopped: a single-server deploy has a short restart gap. Keep migrations backward compatible with the previous release (expand, then contract in a later release) so the automatic restore and `rollback.yaml` stay safe.

### Rollback

Actions → **Rollback** → *Run workflow* with the release tag (`v1.4.2`). It resolves the digest of `IMAGE:1.4.2` in the registry and deploys it with that release's `compose.yaml`, through the same deploy action and lock as `deploy`. Database migrations are not reversed.

## Setup checklist (repository owner)

Repository **variables** (Settings → Secrets and variables → Actions → Variables):

| Variable | Needed for | Example |
|---|---|---|
| `YC_REGISTRY_ID` | publish | `crp1a2b3c4d5e6f7g8h9` |
| `IMAGE_NAME` | publish | `my-app` |
| `YC_SA_ID` | publish, keyless (optional) | service account id for [workload identity federation](https://yandex.cloud/en/docs/iam/tutorials/wlif-github-integration) |
| `ATTESTATIONS` | publish (optional) | `registry` (default), `ghcr` or `off` |
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

Without `YC_REGISTRY_ID`/`IMAGE_NAME` the pipeline still releases (tag, changelog, GitHub Release) and skips publish and deploy; without `DEPLOY_ENABLED=true` it publishes and skips deploy.

### Branch protection and the release bypass

1. Protect `main` with a ruleset: require pull requests, require the status check **CI gate** (and **Conventional PR title**), allow squash merges only.
2. The release job pushes a commit and a tag to `main`. `GITHUB_TOKEN` cannot bypass rules, so create a GitHub App (permissions: *Contents: read and write*; no webhook), install it on the repository, and add it to the ruleset's **bypass list**. Store its client id in `RELEASE_APP_CLIENT_ID` and a private key in `RELEASE_APP_PRIVATE_KEY`. Without them the job uses `GITHUB_TOKEN`, which works only while `main` is unprotected.
3. If tags are protected by a ruleset, add the same app to that bypass list.

### Server

1. Install Docker Engine with the Compose plugin; create the deploy user in the `docker` group.
2. Let the server pull from Yandex CR: attach a service account with `container-registry.images.puller` to the VM and configure the [Docker credential helper](https://yandex.cloud/en/docs/container-registry/operations/authentication), or `docker login cr.yandex` once with a pull-only key. The pipeline never copies its push credentials to the server.
3. Create `DEPLOY_PATH` with a `.env` built from `.env.example`: real `SECRET_KEY`, `ENCRYPTION_KEY`, `PASSWORD_PEPPER`, `SQL_PASSWORD`, `REDIS_PASSWORD`, `NUXT_PUBLIC_BASE_URL`, and `COMPOSE_PROJECT_NAME`. The first deploy adds `APP_IMAGE` and `compose.yaml`.
4. Terminate TLS in front of `APP_ENTRY_PORT` (host Caddy/nginx or a cloud load balancer) and set HSTS there.
5. Create the first user: `docker compose exec -w /app/backend app python -m manage create_superuser`.
