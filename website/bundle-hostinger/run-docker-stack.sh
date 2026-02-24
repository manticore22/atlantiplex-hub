#!/usr/bin/env bash
set -euo pipefail
docker-compose up -d --build
echo "Docker stack started. Access gateway: http://<host>/, Atlantiplex: http://<host>/atlantiplex"
