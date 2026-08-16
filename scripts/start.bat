@echo off
set CONTAINER_NAME=pm-kanban-app
set IMAGE_NAME=pm-kanban-app:latest

echo Building Docker image %IMAGE_NAME%...
docker build -t %IMAGE_NAME% .

echo Stopping existing container if present...
docker stop %CONTAINER_NAME% >nul 2>&1
docker rm %CONTAINER_NAME% >nul 2>&1

echo Starting container %CONTAINER_NAME% on port 8000...
docker run -d --name %CONTAINER_NAME% -p 8000:8000 --env-file backend/.env %IMAGE_NAME%

echo App running successfully at http://localhost:8000
