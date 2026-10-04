#!/usr/bin/env bash
# Adapted from CDS212 woche-06-continuous-deployment-cloud/code/smoke-test.sh.
# Usage: ./scripts/smoke-test.sh https://shelfops-example.onrender.com
# Requires bash, curl and Python 3 (activate .venv or set PYTHON).
# Creates labelled demo records; returns the loan but does not delete records.
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "usage: $0 <base-url>" >&2
  exit 2
fi
BASE_URL="${1%/}"
case "$BASE_URL" in
  http://?*|https://?*) ;;
  *) echo "Expected an http:// or https:// base URL." >&2; exit 2 ;;
esac
PYTHON="${PYTHON:-python3}"
HEALTH_RETRIES="${HEALTH_RETRIES:-12}"
BACKOFF_SECONDS="${BACKOFF_SECONDS:-5}"
EXPECTED_COMMIT="${EXPECTED_COMMIT:-}"
if [ -n "$EXPECTED_COMMIT" ] && ! [[ "$EXPECTED_COMMIT" =~ ^[0-9a-f]{40}$ ]]; then
  echo "EXPECTED_COMMIT must be a full lowercase Git commit SHA." >&2
  exit 2
fi
for value in "$HEALTH_RETRIES" "$BACKOFF_SECONDS"; do
  case "$value" in
    ''|*[!0-9]*) echo "Retry settings must be whole numbers." >&2; exit 2 ;;
  esac
done
# Force decimal interpretation, including values with leading zeroes.
HEALTH_RETRIES=$((10#$HEALTH_RETRIES))
BACKOFF_SECONDS=$((10#$BACKOFF_SECONDS))
if [ "$HEALTH_RETRIES" -lt 1 ]; then
  echo "HEALTH_RETRIES must be at least 1." >&2
  exit 2
fi
command -v curl >/dev/null || { echo "curl is required." >&2; exit 2; }
command -v "$PYTHON" >/dev/null || { echo "Python 3 is required (set PYTHON)." >&2; exit 2; }
CURL_OPTS=(--silent --show-error --connect-timeout 10 --max-time 60)
STATUS=""
BODY=""

fail() { echo "FAIL: $*" >&2; exit 1; }

# Preserve response bodies on HTTP errors; do not follow redirects or retry POSTs.
request() {
  local method="$1" path="$2" raw
  shift 2
  raw="$(curl "${CURL_OPTS[@]}" -X "$method" "$@" \
    -w $'\n%{http_code}' "${BASE_URL}${path}")" || return 1
  STATUS="${raw##*$'\n'}"
  BODY="${raw%$'\n'*}"
}

expect_status() {
  [ "$STATUS" = "$1" ] || fail "HTTP $STATUS (expected $1); body: $BODY"
}

# Parse actual JSON. For arrays select exactly our record, never assume ID 1.
# Arguments: record ID (0 = response object), field, expected JSON value.
check_json() {
  printf '%s' "$BODY" | "$PYTHON" -c '
import json, sys
try:
    value = json.load(sys.stdin)
    record_id = int(sys.argv[1])
    if record_id:
        if not isinstance(value, list):
            raise ValueError("Expected a JSON array")
        matches = [v for v in value if isinstance(v, dict) and v.get("id") == record_id]
        if len(matches) != 1:
            raise ValueError("Expected exactly one matching record")
        value = matches[0]
    field, expected = sys.argv[2], json.loads(sys.argv[3])
    if not isinstance(value, dict) or field not in value or value[field] != expected:
        raise ValueError(f"Unexpected or missing field: {field}")
except (ValueError, TypeError) as error:
    print(error, file=sys.stderr)
    sys.exit(1)
' "$@"
}

created_id() {
  printf '%s' "$BODY" | "$PYTHON" -c '
import json, sys
try:
    value = json.load(sys.stdin)
    identifier = value.get("id") if isinstance(value, dict) else None
    if type(identifier) is not int or identifier < 1:
        raise ValueError("Expected a positive integer ID")
    print(identifier)
except (ValueError, TypeError) as error:
    print(error, file=sys.stderr)
    sys.exit(1)
'
}

echo "Target: $BASE_URL"
echo "This test creates a book, copy, member and loan; records remain after the test."
echo "== 1/5 waiting for /health (tolerates a cold start) =="
healthy=0
for ((attempt=1; attempt<=HEALTH_RETRIES; attempt++)); do
  if request GET /health && [ "$STATUS" = 200 ] && check_json 0 status '"ok"'; then
    if [ -z "$EXPECTED_COMMIT" ] || check_json 0 commit "\"$EXPECTED_COMMIT\""; then
      echo "  /health OK (attempt $attempt): $BODY"
      healthy=1
      break
    fi
    echo "  Healthy instance has not reported the expected commit yet."
  fi
  if [ "$attempt" -lt "$HEALTH_RETRIES" ]; then
    wait_for=$((BACKOFF_SECONDS * attempt))
    echo "  not healthy yet ($attempt/$HEALTH_RETRIES); waiting ${wait_for}s..."
    sleep "$wait_for"
  fi
done
[ "$healthy" -eq 1 ] || fail "/health did not become healthy with the expected commit"

echo "== 2/5 checking /ready =="
request GET /ready || fail "GET /ready request failed"
expect_status 200
check_json 0 status '"ready"' || fail "Readiness body is invalid"

echo "== 3/5 creating and reading book, copy and member =="
label="smoke-test-$(date -u +%Y%m%dT%H%M%SZ)-$$-$RANDOM"
request POST /books -H 'Content-Type: application/json' \
  -d "{\"title\":\"$label\",\"author\":\"ShelfOps smoke test\"}" || fail "Create book failed"
expect_status 201
book_id=$(created_id) || fail "Invalid book ID"
request POST /copies -H 'Content-Type: application/json' \
  -d "{\"book_id\":$book_id}" || fail "Create copy failed"
expect_status 201
copy_id=$(created_id) || fail "Invalid copy ID"
request POST /members -H 'Content-Type: application/json' \
  -d "{\"name\":\"$label\"}" || fail "Create member failed"
expect_status 201
member_id=$(created_id) || fail "Invalid member ID"
request GET /books || fail "Read books failed"
expect_status 200
check_json "$book_id" title "\"$label\"" || fail "Book missing or incorrect"
request GET /members || fail "Read members failed"
expect_status 200
check_json "$member_id" name "\"$label\"" || fail "Member missing or incorrect"
request GET /copies || fail "Read copies failed"
expect_status 200
check_json "$copy_id" book_id "$book_id" || fail "Copy belongs to wrong book"
check_json "$copy_id" status '"available"' || fail "New copy is not available"
echo "  created book=$book_id copy=$copy_id member=$member_id ($label)"

echo "== 4/5 borrowing the copy and checking its status =="
request POST /loans -H 'Content-Type: application/json' \
  -d "{\"copy_id\":$copy_id,\"member_id\":$member_id}" || fail "Create loan failed"
expect_status 201
loan_id=$(created_id) || fail "Invalid loan ID"
check_json 0 copy_id "$copy_id" || fail "Wrong loan copy"
check_json 0 member_id "$member_id" || fail "Wrong loan member"
check_json 0 returned_at null || fail "New loan is already returned"
echo "  created loan=$loan_id; if this test aborts, this loan may remain open."
request GET /copies || fail "Read borrowed copy failed"
expect_status 200
check_json "$copy_id" status '"on_loan"' || fail "Copy is not on loan"

echo "== 5/5 returning the copy and checking its status =="
request POST "/loans/$loan_id/return" || fail "Return request failed"
expect_status 200
check_json 0 id "$loan_id" || fail "Wrong returned loan"
returned_at=$(printf '%s' "$BODY" | "$PYTHON" -c '
import json, sys
from datetime import datetime
try:
    value = json.load(sys.stdin)["returned_at"]
    if datetime.fromisoformat(value).utcoffset() is None:
        raise ValueError("Return timestamp has no timezone")
    print(json.dumps(value))
except (ValueError, TypeError, KeyError) as error:
    print(error, file=sys.stderr)
    sys.exit(1)
') || fail "Missing or invalid return timestamp"
request GET /loans || fail "Read loan history failed"
expect_status 200
check_json "$loan_id" returned_at "$returned_at" || fail "Return was not persisted"
request GET /copies || fail "Read returned copy failed"
expect_status 200
check_json "$copy_id" status '"available"' || fail "Returned copy is not available"
echo "  returned loan=$loan_id; copy=$copy_id is available again."
echo
echo "SMOKE TEST PASSED"
