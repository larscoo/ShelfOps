#!/bin/sh
# Use an automatically assigned localhost port to avoid existing app containers.
set -eu
image=${1:-shelfops:ci}
container=$(docker run -d -p 127.0.0.1::8000 "$image")
cleanup() {
  docker rm -f "$container" >/dev/null
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
test "$(docker exec "$container" id -u)" != "0"
binding=$(docker port "$container" 8000/tcp)
for attempt in $(seq 1 30); do
  if curl --fail --silent --show-error --max-time 2 "http://$binding/health"; then
    echo "Health check passed; container runs as non-root."
    exit 0
  fi
  sleep 1
done
docker logs "$container"
echo "Health check failed." >&2
exit 1
