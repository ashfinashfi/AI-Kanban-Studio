#!/usr/bin/env bash
set -e

CONTAINER_NAME="pm-kanban-app"
IMAGE_NAME="pm-kanban-app:latest"

echo "Building Docker image ${IMAGE_NAME}..."
docker build -t ${IMAGE_NAME} .

echo "Stopping any existing container named ${CONTAINER_NAME}..."
docker stop ${CONTAINER_NAME} 2>/dev/null || true
docker rm ${CONTAINER_NAME} 2>/dev/null || true

echo "Starting container ${CONTAINER_NAME} on port 8000..."
docker run -d \
  --name ${CONTAINER_NAME} \
  -p 8000:8000 \
  --env-file backend/.env \
  ${IMAGE_NAME}

echo "App running successfully at http://localhost:8000"
