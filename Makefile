# Reads one key from .env without executing it: tolerates comments, `export`, quotes and a missing file.
# Precedence: command line > environment > .env > default below.
dotenv = $(shell [ -f .env ] && awk -v key='$(1)' '{ sub(/^[ \t]*export[ \t]+/, "") } index($$0, "=") { k = substr($$0, 1, index($$0, "=") - 1); gsub(/[ \t]/, "", k); if (k == key) v = substr($$0, index($$0, "=") + 1) } END { sub(/[ \t]+\#.*$$/, "", v); gsub(/^[ \t"\047]+|[ \t"\047]+$$/, "", v); printf "%s", v }' .env)

UV := uv
PNPM := pnpm

BACKEND_DIR := backend
FRONTEND_DIR := frontend

BACKEND_APP := app.main:app
BACKEND_HOST ?= 0.0.0.0
BACKEND_PORT ?= $(or $(call dotenv,BACKEND_PORT),9000)
FRONTEND_HOST ?= 0.0.0.0
FRONTEND_PORT ?= $(or $(call dotenv,FRONTEND_PORT),9001)

TASKIQ_WORKERS ?= $(or $(call dotenv,TASKIQ_WORKERS),1)
TASKIQ_UPDATE_INTERVAL ?= $(or $(call dotenv,TASKIQ_UPDATE_INTERVAL),10)

# Docker image for docker-build / docker-run (production services run under s6-overlay, see docker/).
IMAGE ?= fastapi-nuxt-template:local
APP_VERSION ?= $(shell sed -n 's/.*"version"[^"]*"\([^"]*\)".*/\1/p' version.json)
GIT_SHA ?= $(shell git rev-parse HEAD 2>/dev/null || echo unknown)
# Extra `docker build` flags, e.g. DOCKER_BUILD_FLAGS="--platform linux/amd64 --no-cache".
DOCKER_BUILD_FLAGS ?=
SMOKE_PROJECT ?=$(or $(call dotenv,COMPOSE_PROJECT_NAME),fastapi-nuxt-template)-smoke

# Extra pytest args for check-backend / test-backend, e.g. PYTEST_ARGS=--sqlite when Postgres is not running.
PYTEST_ARGS ?= --keepdb
# BUILD=1 adds the Nuxt production build to check-frontend.
BUILD ?=

# ----------- SHORT COMMANDS ----------- #

rb: run-backend ## short run backend api
rf: run-frontend ## short run frontend dev
rt: run-taskiq ## short run taskiq

mm: make-migrations ## short run make migrations
m: migrate ## short run migrate
t: test ## short run backend tests

# ----------- SETUP ----------- #

install: install-backend install-frontend ## install all dependencies

install-backend: ## install backend dependencies via uv
	$(UV) sync --project $(BACKEND_DIR) --locked

install-frontend: ## install frontend dependencies via pnpm
	$(PNPM) --dir $(FRONTEND_DIR) install

make-migrations: ## create migrations from model changes
	cd $(BACKEND_DIR) && $(UV) run python -m tortoise makemigrations

migrate: ## run migrations
	cd $(BACKEND_DIR) && $(UV) run python -m tortoise migrate

createsuperuser: ## create the first user (interactive)
	cd $(BACKEND_DIR) && $(UV) run manage.py create_superuser

init: ## turn a fresh template copy into a new product: make init name=<kebab-name> [title="Название"] [force=1]
	@test -n "$(name)" || { echo 'usage: make init name=<kebab-name> [title="Название"] [force=1]'; exit 2; }
	$(UV) run --no-project python scripts/bootstrap/init.py "$(name)" $(if $(title),--title "$(title)") $(if $(force),--force)

new-domain: ## scaffold a backend domain + frontend feature: make new-domain name=<snake_name> [title="Проекты"] [item_title="Проект"] [plural=...]
	@test -n "$(name)" || { echo 'usage: make new-domain name=<snake_name> [title="Проекты"] [item_title="Проект"] [plural=<snake_plural>]'; exit 2; }
	$(UV) run --no-project python scripts/scaffold/new_domain.py "$(name)" $(if $(title),--title "$(title)") \
		$(if $(item_title),--item-title "$(item_title)") $(if $(plural),--plural "$(plural)")

prepare: ## prepare project
	cd $(FRONTEND_DIR) && pnpm nuxt prepare

openapi: ## write the OpenAPI schema to frontend/openapi.json (no database needed)
	cd $(BACKEND_DIR) && $(UV) run manage.py openapi --output ../$(FRONTEND_DIR)/openapi.json

gen-client: openapi ## regenerate the typed frontend API client (frontend/app/shared/api/generated) from the schema
	$(PNPM) --dir $(FRONTEND_DIR) run gen:api

shell: ## run backend shell
	cd $(BACKEND_DIR) && $(UV) run python -m manage shell

# ----------- DEVELOPMENT ----------- #

run-backend: ## run FastAPI with reload
	cd $(BACKEND_DIR) && $(UV) run uvicorn $(BACKEND_APP) --reload --host $(BACKEND_HOST) --port $(BACKEND_PORT)

run-frontend: ## run Nuxt dev server
	cd $(FRONTEND_DIR) && pnpm dev --port $(FRONTEND_PORT)

run-taskiq: ## Run both scheduler and worker
	$(MAKE) -j2 run-taskiq-scheduler run-taskiq-worker

run-taskiq-worker: ## Run taskiq worker
	cd $(BACKEND_DIR) && $(UV) run python -m taskiq worker app.core.broker:broker --fs-discover --tasks-pattern "app/**/tasks.py" --workers $(TASKIQ_WORKERS)

run-taskiq-scheduler: ## Run taskiq scheduler
	cd $(BACKEND_DIR) && $(UV) run python -m taskiq scheduler app.core.broker:scheduler --fs-discover --tasks-pattern "app/**/tasks.py" --update-interval $(TASKIQ_UPDATE_INTERVAL)

test: test-backend ## run backend tests

test-backend: ## run backend pytest suite (PYTEST_ARGS=--sqlite without Postgres)
	cd $(BACKEND_DIR) && $(UV) run manage.py test $(PYTEST_ARGS)

# ----------- DOCKER ----------- #

docker-build: ## build the production image (IMAGE, APP_VERSION from version.json, GIT_SHA from git)
	docker build --build-arg APP_VERSION=$(APP_VERSION) --build-arg GIT_SHA=$(GIT_SHA) \
		--build-arg BUILD_DATE=$$(date -u +%Y-%m-%dT%H:%M:%SZ) $(DOCKER_BUILD_FLAGS) -t $(IMAGE) .

docker-run: ## run IMAGE with PostgreSQL + Redis from compose.yaml, wait until healthy (project <name>-smoke)
	APP_IMAGE=$(IMAGE) docker compose -f compose.yaml -p $(SMOKE_PROJECT) up -d --wait --wait-timeout 180

docker-stop: ## stop the docker-run stack and delete its volumes
	docker compose -f compose.yaml -p $(SMOKE_PROJECT) down -v

# ----------- QUALITY ----------- #

.PHONY: init new-domain createsuperuser openapi gen-client check check-backend check-frontend lint lint-backend lint-frontend fmt test test-backend help docker-build docker-run docker-stop

check: check-backend check-frontend ## run every CI check without changing files

# Repository tooling outside backend/ that runs on the backend's Python: scaffolder, bootstrap, Claude Code hooks.
TOOLING := ../scripts ../.claude/hooks

check-backend: ## ruff, ruff format --check, ty, pytest (PYTEST_ARGS=--sqlite without Postgres), tooling tests
	cd $(BACKEND_DIR) && $(UV) run ruff check . $(TOOLING)
	cd $(BACKEND_DIR) && $(UV) run ruff format --check . $(TOOLING)
	cd $(BACKEND_DIR) && $(UV) run ty check
	cd $(BACKEND_DIR) && $(UV) run manage.py test $(PYTEST_ARGS)
	cd $(BACKEND_DIR) && $(UV) run pytest ../scripts/tests -q -p no:cacheprovider

check-frontend: ## pnpm check (fmt, lint, typecheck, test, architecture); BUILD=1 adds nuxt build
	$(PNPM) --dir $(FRONTEND_DIR) run check
ifneq ($(BUILD),)
	$(PNPM) --dir $(FRONTEND_DIR) run build
endif

lint: lint-backend lint-frontend ## fix lint issues and format backend+frontend

lint-backend: ## ruff check --fix + ruff format (backend and tooling)
	cd $(BACKEND_DIR) && $(UV) run ruff check --fix . $(TOOLING)
	cd $(BACKEND_DIR) && $(UV) run ruff format . $(TOOLING)

lint-frontend: ## oxfmt + oxlint/eslint --fix
	$(PNPM) --dir $(FRONTEND_DIR) run fmt
	$(PNPM) --dir $(FRONTEND_DIR) run lint:fix

fmt: ## format backend+frontend (ruff format, oxfmt)
	cd $(BACKEND_DIR) && $(UV) run ruff format . $(TOOLING)
	$(PNPM) --dir $(FRONTEND_DIR) run fmt

# ----------- HELPERS ----------- #

help: ## show this help
	@echo "Usage: make <target>"
	@awk 'BEGIN {FS = ":.*##"} /^[0-9a-zA-Z_-]+:.*?## / { printf "  * %-20s - %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
