#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
TAG="latest"
if [ -n "${1-}" ]; then
  TAG="$1"
fi

echo "[BUILD] Tag: $TAG" | tee -a "$ROOT_DIR/build_and_push.log"
docker login docker.io

BUILD_PLATFORMS="linux/amd64,linux/arm64"
export DOCKER_CLI_EXPERIMENTAL=enabled

echo "[BUILD] Building website..." | tee -a "$ROOT_DIR/build_and_push.log"
docker buildx create --use --name atlantiplex-builder || true
docker buildx build --platform ${BUILD_PLATFORMS} -t docker.io/manticore313/website_and_studio:website-$TAG -f website/Dockerfile .

echo "[BUILD] Building studio..." | tee -a "$ROOT_DIR/build_and_push.log"
docker buildx build --platform ${BUILD_PLATFORMS} -t docker.io/manticore313/website_and_studio:studio-$TAG -f AtlantiplexStudio/Dockerfile .

echo "[BUILD] Building stage..." | tee -a "$ROOT_DIR/build_and_push.log"
docker buildx build --platform ${BUILD_PLATFORMS} -t docker.io/manticore313/website_and_studio:stage-$TAG -f matrix-studio/web/stage/Dockerfile .

echo "[BUILD] Building flask..." | tee -a "$ROOT_DIR/build_and_push.log"
docker buildx build --platform ${BUILD_PLATFORMS} -t docker.io/manticore313/website_and_studio:flask-$TAG -f matrix-studio/Dockerfile.python .

echo "[BUILD] Pushing images..." | tee -a "$ROOT_DIR/build_and_push.log"
docker push docker.io/manticore313/website_and_studio:website-$TAG
docker push docker.io/manticore313/website_and_studio:studio-$TAG
docker push docker.io/manticore313/website_and_studio:stage-$TAG
docker push docker.io/manticore313/website_and_studio:flask-$TAG

echo "[BUILD] Done." | tee -a "$ROOT_DIR/build_and_push.log"
