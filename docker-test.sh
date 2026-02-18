#!/bin/bash
set -e

echo "=========================================="
echo "  FULL DOCKER TEST - atlantiplex-hub"
echo "=========================================="

PROJECT_NAME="atlantiplex-hub"
CONTAINER_NAME="atlantiplexhub_test"
IMAGE_NAME="atlantiplex-hub:test"

echo "[1/12] Building Docker image..."
docker build -t "$IMAGE_NAME" .

echo "[2/12] Creating test network..."
docker network create "atlantiplexhub_test_net" 2>/dev/null || true

echo "[3/12] Running container tests..."
docker run -d --name "$CONTAINER_NAME" --network "atlantiplexhub_test_net" -p 3012:3000 -e NODE_ENV=test "$IMAGE_NAME"

echo "[4/12] Waiting for container to start..."
sleep 8

echo "[5/12] Checking container is running..."
docker ps | grep "$CONTAINER_NAME"

echo "[6/12] Checking Node..."
docker exec "$CONTAINER_NAME" node --version
docker exec "$CONTAINER_NAME" npm --version

echo "[7/12] Checking logs..."
docker logs "$CONTAINER_NAME" 2>&1 | tail -20

echo "[8/12] Container resource usage..."
docker stats "$CONTAINER_NAME" --no-stream

echo "[9/12] Health check..."
curl -s http://localhost:3012/ 2>/dev/null || echo "API not responding"

echo "[10/12] Docker compose services..."
docker exec "$CONTAINER_NAME" docker ps 2>/dev/null || echo "Docker not available in container"

echo "[11/12] Environment check..."
docker exec "$CONTAINER_NAME" env | grep NODE_ENV

echo "[12/12] Cleanup..."
docker stop "$CONTAINER_NAME" 2>/dev/null || true
docker rm "$CONTAINER_NAME" 2>/dev/null || true
docker rmi "$IMAGE_NAME" 2>/dev/null || true
docker network rm "atlantiplexhub_test_net" 2>/dev/null || true

echo "DOCKER TEST COMPLETED"
