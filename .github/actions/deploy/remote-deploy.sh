#!/usr/bin/env bash
# Runs on the server: remote-deploy.sh <dir> <image@digest>.
# Pins APP_IMAGE in <dir>/.env, pulls, restarts and waits for the healthcheck.
# If the new container does not become healthy, the previous image is restored.
set -euo pipefail

dir="$1"
image="$2"
cd "$dir"

if [ ! -f .env ]; then
    echo "deploy: ${dir}/.env is missing; create it from .env.example first (docs/deployment.md)" >&2
    exit 1
fi

compose() { docker compose -f compose.yaml "$@"; }

set_image() {
    if grep -q '^APP_IMAGE=' .env; then
        sed -i "s|^APP_IMAGE=.*|APP_IMAGE=$1|" .env
    else
        printf '\nAPP_IMAGE=%s\n' "$1" >> .env
    fi
}

previous=$(sed -n 's/^APP_IMAGE=//p' .env | tail -n 1)

set_image "$image"
compose pull --quiet app
if compose up -d --remove-orphans --wait --wait-timeout 300; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) deployed ${image} (previous: ${previous:-none})" >> deploy-history.log
    docker image prune -f > /dev/null || true
    echo "deploy: ${image} is healthy"
    exit 0
fi

echo "deploy: ${image} did not become healthy" >&2
compose logs --no-color --tail 200 app >&2 || true
if [ -n "$previous" ] && [ "$previous" != "$image" ]; then
    echo "deploy: restoring ${previous}" >&2
    set_image "$previous"
    compose up -d --remove-orphans --wait --wait-timeout 300 || true
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) failed ${image}, restored ${previous}" >> deploy-history.log
fi
exit 1
