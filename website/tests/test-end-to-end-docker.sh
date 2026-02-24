#!/usr/bin/env bash
set -euo pipefail

DOMAIN=${1:-localhost}

echo "[TEST] End-to-end Docker test for domain: ${DOMAIN}"

# Detect docker-compose wrapper
if command -v docker-compose >/dev/null 2>&1; then
  DC="docker-compose"
elif command -v docker >/dev/null 2>&1; then
  DC="docker compose"
else
  echo "Docker Compose not found. Install docker and compose."; exit 1
fi

# Bring up services
echo "Starting services..."
${DC} up -d --build

echo "Waiting for gateway to respond..."
TIMEOUT=${TIMEOUT:-120}
COUNTER=0
while ! curl -sS http://${DOMAIN} >/dev/null; do
  sleep 2
  COUNTER=$((COUNTER+2))
  if [ ${COUNTER} -ge ${TIMEOUT} ]; then
    echo "Gateway did not respond within timeout"; ${DC} ps; exit 1
  fi
done

echo "Checking endpoints..."
echo "Gateway root:"; curl -sS http://${DOMAIN} | head -n 5
echo "Atlantiplex path:"; curl -sS http://${DOMAIN}/atlantiplex | head -n 5

echo "Container status (gateway/atlantiplex/db/nginx)"
${DC} ps gateway atlantiplex db nginx || true

echo "End-to-end docker test completed."
