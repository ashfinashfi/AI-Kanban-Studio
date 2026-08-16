$ContainerName = "pm-kanban-app"

Write-Host "Stopping container ${ContainerName}..."
docker stop ${ContainerName} 2>$null | Out-Null
docker rm ${ContainerName} 2>$null | Out-Null

Write-Host "Container stopped and removed."
