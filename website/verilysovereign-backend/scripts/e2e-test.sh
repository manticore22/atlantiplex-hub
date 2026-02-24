#!/usr/bin/env bash
set -euo pipefail

echo "Starting end-to-end test (Stage 1 then Stage 2)"

# Stage 1: start gateway/api
docker-compose -f docker-compose.stage1.yml up -d --build
echo "Stage 1 started. Waiting..."
sleep 15

# 1) Sign up test user (Stage 1)
SIGNUP='{"email":"e2e-user@example.com","password":"P@ssw0rd123"}'
TOKEN=$(curl -s -X POST http://localhost:3000/api/auth/signup -H "Content-Type: application/json" -d "$SIGNUP" | jq -r '.token')
echo "Stage 1 user token: ${TOKEN}"

# 2) Access account/subscription (Stage 1, none yet)
curl -s -H "Authorization: Bearer ${TOKEN}" http://localhost:3000/api/user/subscription | head -n 2

# 3) Stage 2: start Atlantiplex
docker-compose -f docker-compose.stage2.yml up -d --build
echo "Stage 2 started. Waiting..."
sleep 20

# 4) Admin metrics (with a generated admin token)
ADMIN_TOKEN=$(node ./gen-admin-token.js)
echo "Admin token: ${ADMIN_TOKEN}"
curl -sS -H "Authorization: Bearer ${ADMIN_TOKEN}" http://localhost:3000/api/admin/metrics | head -n 5

echo "Done. Review Stage 2 endpoints: /atlantiplex and /admin-login.html"
