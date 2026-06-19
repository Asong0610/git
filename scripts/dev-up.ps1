$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$composeFile = Join-Path $repoRoot "deploy\docker-compose.dev.yml"

Write-Host "启动 PostgreSQL 与 Redis ..."
docker compose -f $composeFile up -d

Write-Host "等待服务就绪 ..."
Start-Sleep -Seconds 5
docker compose -f $composeFile ps
