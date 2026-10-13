
#!/usr/bin/env bash
# Adapted from CDS212 week 09 for ShelfOps.
# Usage: bash scripts/last-erzeugen.sh [BASE_URL] [ITERATIONS]
set -euo pipefail

BASE_URL="${1:-http://localhost:8000}"
BASE_URL="${BASE_URL%/}"
ITERATIONS="${2:-200}"

if ! [[ "$ITERATIONS" =~ ^[1-9][0-9]*$ ]]; then
  echo "ITERATIONS muss eine positive ganze Zahl sein." >&2
  exit 1
fi

request() {
  local path="$1"
  local expected="$2"
  local actual

  actual=$(curl --silent --show-error --max-time 5 \
    --output /dev/null --write-out '%{http_code}' \
    "${BASE_URL}${path}")

  if [[ "$actual" != "$expected" ]]; then
    echo "${path}: HTTP ${actual}, erwartet ${expected}" >&2
    exit 1
  fi
}

echo "Last gegen ${BASE_URL}: ${ITERATIONS} Durchläufe"

for ((i = 1; i <= ITERATIONS; i++)); do
  request "/books" 200
  request "/copies" 200
  request "/health" 200

  if (( i % 5 == 0 )); then
    request "/does-not-exist" 404
  fi

  sleep 0.1
done

echo "Fertig. Prometheus jetzt 15–30 Sekunden zum Abrufen geben."
