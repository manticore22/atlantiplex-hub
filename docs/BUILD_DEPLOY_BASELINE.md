Build and Deploy Baseline (New Monorepo Layout)

Overview
- Establish a clean, scalable monorepo structure and a safe, incremental path to move all pieces (website, studio, matrix, etc.) into well-defined apps/services folders.
- Stripe MVP wiring stays behind env keys; images are built and pushed to Docker Hub; docker-compose references updated accordingly.

New Repo Layout (high level)
- apps/website: website frontend assets and code
- apps/gateway: signup/login/billing UI (gateway app)
- services/studio: Atlantiplex Studio frontend/backend
- services/matrix: studio backend (matrix) and related services
- infra/docker: production/dev/test docker-compose files
- infra/nginx: nginx configs
- core: shared libraries and utilities
- tests: end-to-end and unit tests
- docs: runbooks and architecture notes (this file lives here)
- ops: deployment scripts and CI templates

Phase plan (high-level)
- Phase A: Scaffold and baseline
  - Create top-level folders, READMEs, and a root map of where things live
  - Update references to new paths in core scripts
- Phase B: Move components incrementally
  - Phase 1: Move website under apps/website
  - Phase 2: Move studio/matrix under services, update docker-compose paths
  - Phase 3: Move infra assets under infra/
- Phase C: Stripe MVP wiring
  - Env-based Stripe keys and price IDs; public-key and plan endpoints
- Phase D: Validation and tests
  - Build, deploy, health, and end-to-end tests; CI integration
- Phase E: Rollback and QA
  - Ensure rollback plan exists in PRs and CI

Key commands (typical path)
- Build images (website and studio, multi-arch):
  docker login docker.io
  docker buildx create --use --name atlantiplex-builder
  docker buildx build --platform linux/amd64,linux/arm64 -t docker.io/manticore313/website_and_studio:website-latest -f apps/website/Dockerfile .
  docker buildx build --platform linux/amd64,linux/arm64 -t docker.io/manticore313/website_and_studio:studio-latest -f services/studio/Dockerfile .
  docker push docker.io/manticore313/website_and_studio:website-latest
  docker push docker.io/manticore313/website_and_studio:studio-latest

- Start stack:
  docker-compose -f infra/docker/docker-compose.prod.yml up -d

- Health checks:
  curl -f http://verilysovereign.online/health
  curl -f http://website.verilysovereign.online/health
  curl -f http://studio.verilysovereign.online/health

- Tests:
  npm audit
  pip audit

Notes
- All secrets must live in CI secrets or environment variables; never in repo.
- This document outlines the high-level plan and the concrete commands you’ll run in order. Adjust paths as you actually migrate components.

This file is intended to serve as a single source of truth for how we reorganize and deploy the system going forward.
