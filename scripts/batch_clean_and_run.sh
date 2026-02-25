#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)

DRY=false
TEST_ONLY=false
CLEAN_ONLY=false

while (( "$#" )); do
  case "$1" in
    --dry-run) DRY=true; shift ;;
    --test-only) TEST_ONLY=true; shift ;;
    --clean-only) CLEAN_ONLY=true; shift ;;
    *) break ;;
  esac
done

log() { echo "[BATCH] $*"; }

if [ "$CLEAN_ONLY" = true ]; then
  log "Cleaning project artifacts (node_modules, dist, caches)..."
  rm -rf website/node_modules website/dist website/build __pycache__ .pytest_cache tests/reports || true
  rm -rf AtlantiplexStudio/node_modules AtlantiplexStudio/dist AtlasStudio/build || true
  log "Clean complete."
  exit 0
fi

if $DRY; then log "Dry run: no actions will be executed."; fi

log "Starting batch run: registry-based deployment will require docker login if pushing."

if [ -f docker-compose.prod.yml ]; then
  log "Bringing stack up..."
  if ! $DRY; then docker-compose -f docker-compose.prod.yml up -d; fi
fi

log "Running E2E tests..."
if ! $DRY; then
  node tests/e2e-theme-playwright.js
  node tests/e2e-theme-playwright-mobile.js
  node tests/e2e-download.js
fi

log "Running health checks..."
if ! $DRY; then python3 tests/test_endpoints.py || true; fi

log "Teardown stack..."
if ! $DRY; then docker-compose -f docker-compose.prod.yml down; fi

log "Batch run finished."
