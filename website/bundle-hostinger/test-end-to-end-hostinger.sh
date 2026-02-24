#!/usr/bin/env bash
set -euo pipefail

DOMAIN=${1:-verilysovereign.org}

echo "Running end-to-end smoke tests for $DOMAIN..."
curl -sS -I https://"$DOMAIN" | head -n 1
curl -sS https://"$DOMAIN"/ | head -n 3
curl -sS https://"$DOMAIN"/atlantiplex | head -n 3

echo "PM2 status (if PM2 is installed) ->"
pm2 status | head -n 6 || true

echo "End of tests."
