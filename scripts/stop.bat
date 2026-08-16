@echo off
set CONTAINER_NAME=pm-kanban-app

echo Stopping container %CONTAINER_NAME%...
docker stop %CONTAINER_NAME% >nul 2>&1
docker rm %CONTAINER_NAME% >nul 2>&1

echo Container stopped and removed.
