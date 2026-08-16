#!/usr/bin/env bash

CONTAINER_NAME="pm-kanban-app"

echo "Stopping container ${CONTAINER_NAME}..."
docker stop ${CONTAINER_NAME} 2>/dev/null || true
docker rm ${CONTAINER_NAME} 2>/dev/null || true

echo "Container stopped and removed."
