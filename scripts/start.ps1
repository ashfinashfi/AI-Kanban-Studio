$ContainerName = "pm-kanban-app"
$ImageName = "pm-kanban-app:latest"

Write-Host "Building Docker image ${ImageName}..."
docker build -t ${ImageName} .

Write-Host "Stopping any existing container named ${ContainerName}..."
docker stop ${ContainerName} 2>$null | Out-Null
docker rm ${ContainerName} 2>$null | Out-Null

Write-Host "Starting container ${ContainerName} on port 8000..."
docker run -d --name ${ContainerName} -p 8000:8000 --env-file backend/.env ${ImageName}

Write-Host "App running successfully at http://localhost:8000"
