#!/usr/bin/env bash
set -euo pipefail
DOMAIN=${1:-verilysovereign.org}
echo "Health check for ${DOMAIN}"
curls=$(curl -sS -I https://${DOMAIN} | head -n 1)
echo "$curls"
curl -sS http://${DOMAIN}/ | head -n 2
curl -sS http://${DOMAIN}/atlantiplex | head -n 2
