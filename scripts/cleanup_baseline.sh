#!/usr/bin/env bash
set -euo pipefail
echo "Cleaning repo artifacts..."
rm -rf node_modules dist build __pycache__ .pytest_cache logs/**/*.log tests/**/*.log
if [ -f .env ]; then
  rm .env
  echo ".env removed from repo";
fi
git rm -f --cached .env || true
git status
echo "Baseline cleanup complete."
