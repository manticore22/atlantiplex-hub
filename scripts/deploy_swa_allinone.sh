#!/usr/bin/env bash
set -euo pipefail
# Path A MVP: Deploy a single-application stack to Azure Static Web Apps (SWA)
# Frontend + API behind a single hosting surface with a clean domain mapping.
# This script creates or updates a Static Web App for Atlantiplex Studio.
# Usage: set environment vars as needed and run the script.
# - REPO_URL: GitHub repo URL to connect SWA to
# - BRANCH: Branch to deploy (default: main)
# - APP_LOCATION: Path to frontend in repo
# - API_LOCATION: Path to API (serverless functions)
# - OUTPUT_LOCATION: Frontend build output folder (e.g. build or dist)
# - REGION (AZ region): eastus, eastus2, etc
# - RG: Resource group name
# - SWA_NAME: Static Web App name

REGION="${AZ_REGION:-eastus}"
RG="${AZ_SWA_RG:-verily-swa-rg}"
SWA_NAME="${AZ_SWA_NAME:-atlantiplex-studio-swa}"
REPO_URL="${REPO_URL:-https://github.com/yourorg/atlantiplex-studio}"
BRANCH="${BRANCH:-main}"
APP_LOCATION="${APP_LOCATION:-matrix-studio/web/frontend}"
API_LOCATION="${API_LOCATION:-matrix-studio/web/api}"
OUTPUT_LOCATION="${OUTPUT_LOCATION:-build}"

echo "== Path A MVP SWA Deploy =="
echo "Region: $REGION"
echo "Resource Group: $RG"
echo "SWA Name: $SWA_NAME"
echo "Repo: $REPO_URL (branch: $BRANCH)"
echo "App location: $APP_LOCATION"
echo "API location: $API_LOCATION"
echo "Output: $OUTPUT_LOCATION"

echo "== Logging in to Azure =="
az login --output none

echo "== Creating Resource Group (if needed) =="
az group create -l "$REGION" -n "$RG" >/dev/null 2>&1 || true

echo "== Creating/updating Static Web App =="
az staticwebapp create -n "$SWA_NAME" -g "$RG" -l "$REGION" \
  --source "$REPO_URL" \
  --branch "$BRANCH" \
  --app-location "$APP_LOCATION" \
  --api-location "$API_LOCATION" \
  --output-location "$OUTPUT_LOCATION" \
  >/tmp/swa-create.log 2>&1 || true

echo "SWA creation attempted. Check /tmp/swa-create.log for details."
echo "If you already have SWA, consider updating through the portal or re-run this once the repo structure is confirmed."

echo "Done. Next: Bind custom domain in Azure SWA portal (www.verilysovereign.org)."
