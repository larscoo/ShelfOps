#!/bin/sh
# Run the same tests against memory and a disposable PostgreSQL 16 database.
set -eu
python_command=${1:-.venv/bin/python}
if [ "$#" -gt 0 ]; then shift; fi
project="shelfops-tests-$$"
compose_file="docker-compose.test.yml"
cleanup() {
  docker compose -p "$project" -f "$compose_file" down >/dev/null
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
docker compose -p "$project" -f "$compose_file" up -d --wait --wait-timeout 60
binding=$(docker compose -p "$project" -f "$compose_file" port db 5432)
port=${binding##*:}
export TEST_DATABASE_URL="postgresql://shelfops_test:shelfops-test-only@127.0.0.1:$port/shelfops_test"
"$python_command" -m pytest "$@"
