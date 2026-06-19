$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Stage 1 验收脚本" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# Step 1: 启动 Docker 容器
Write-Host "`n[1/5] 启动 PostgreSQL 与 Redis ..." -ForegroundColor Yellow
& "$repoRoot\scripts\dev-up.ps1"

# Step 2: 运行数据库迁移
Write-Host "`n[2/5] 执行数据库迁移 ..." -ForegroundColor Yellow
& "$repoRoot\scripts\migrate.ps1"

# Step 3: 启动 API 服务（后台）
Write-Host "`n[3/5] 启动 API 服务 ..." -ForegroundColor Yellow
$apiDir = Join-Path $repoRoot "servicespi"
Push-Location $apiDir
$envPath = Join-Path $repoRoot "deploy\.env"
if (Test-Path $envPath) {
    Get-Content $envPath | ForEach-Object {
        if ($_ -match "^\s*([^#][^=]+)=(.*)$") {
            Set-Item -Path "Env:$($matches[1].Trim())" -Value $matches[2].Trim()
        }
    }
}
Start-Process -FilePath ".\.venv\Scripts\python.exe" `
    -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000" `
    -WindowStyle Hidden
Pop-Location

Write-Host "等待 API 启动 ..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Step 4: 验证 Health 接口
Write-Host "`n[4/5] 验证 Health 接口 ..." -ForegroundColor Yellow
try {
    $resp = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/health" -Method GET
    $json = $resp | ConvertTo-Json
    Write-Host "Health 响应: $json" -ForegroundColor Green

    if ($resp.status -eq "ok") {
        Write-Host "  状态: OK" -ForegroundColor Green
    } else {
        Write-Host "  状态: $($resp.status) (可能降级)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  Health 检查失败: $_" -ForegroundColor Red
}

# Step 5: 运行 Python 测试
Write-Host "`n[5/5] 运行 Python 集成测试 ..." -ForegroundColor Yellow
Push-Location $apiDir
.\.venv\Scripts\python.exe test_stage1.py
Pop-Location

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "验收完成！请检查以上输出。" -ForegroundColor Cyan
Write-Host "Postman 集合位于: $repoRoot\docs\postman_collection.json" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
