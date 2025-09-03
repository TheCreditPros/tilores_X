#!/usr/bin/env bash
set -euo pipefail

BASE_URL=${BASE_URL:-"http://localhost:8080"}
ADMIN_EMAIL=${ADMIN_EMAIL:-"admin@example.com"}
ADMIN_PASSWORD=${ADMIN_PASSWORD:-"ChangeMe123!"}
RATING_WEBHOOK=${RATING_WEBHOOK:-"https://tilores-x.up.railway.app/webhooks/openwebui-rating"}

echo "Waiting for Open WebUI to be ready at ${BASE_URL}..."
for i in {1..60}; do
  if curl -sSf -m 2 "${BASE_URL}/" >/dev/null; then
    echo "Open WebUI is up"; break
  fi
  sleep 2
done

echo "Registering admin (if not exists)"
curl -sS -m 5 -X POST "${BASE_URL}/api/auth/register" \
  -H 'Content-Type: application/json' \
  -d "{\"email\":\"${ADMIN_EMAIL}\",\"password\":\"${ADMIN_PASSWORD}\"}" >/dev/null || true

echo "Logging in to get token"
TOKEN=$(curl -sS -m 5 -X POST "${BASE_URL}/api/auth/login" -H 'Content-Type: application/json' \
  -d "{\"email\":\"${ADMIN_EMAIL}\",\"password\":\"${ADMIN_PASSWORD}\"}" | jq -r .token)

if [ -z "${TOKEN}" ] || [ "${TOKEN}" = "null" ]; then
  echo "Failed to obtain token" >&2; exit 1
fi

auth() { echo -H "Authorization: Bearer ${TOKEN}"; }

add_model() {
  local name="$1"
  echo "Creating model ${name}"
  curl -sS -m 10 -X POST "${BASE_URL}/api/admin/models" \
    -H 'Content-Type: application/json' $(auth) \
    -d "{\"name\":\"${name}\",\"provider\":\"openai\",\"base_url\":\"https://tilores-x.up.railway.app\",\"api_key\":\"dummy\"}" >/dev/null || true
}

add_model "Tilores/custom/gpt-4o-mini"
add_model "Tilores/custom/gpt-4o"

echo "Setting default model"
curl -sS -m 10 -X POST "${BASE_URL}/api/admin/settings" \
  -H 'Content-Type: application/json' $(auth) \
  -d '{"default_model":"Tilores/custom/gpt-4o-mini"}' >/dev/null || true

echo "Registering rating webhook"
curl -sS -m 10 -X POST "${BASE_URL}/api/admin/webhooks" \
  -H 'Content-Type: application/json' $(auth) \
  -d "{\"event\":\"rating.created\",\"url\":\"${RATING_WEBHOOK}\"}" >/dev/null || true

echo "Bootstrap complete."

