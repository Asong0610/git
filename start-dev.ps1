# 校园共享设备 - 本地开发环境启动脚本
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  校园共享设备 - 本地开发环境启动" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$WORKSPACE = "D:\xxqWORK"

# 1. 启动 Docker 容器（MySQL + Redis）
Write-Host "[1/4] 启动 Docker 容器 (MySQL + Redis)..." -ForegroundColor Yellow
Set-Location "$WORKSPACE\deploy"
docker-compose -f docker-compose.dev.yml up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker 容器启动失败，请检查 Docker 是否运行" -ForegroundColor Red
    exit 1
}
Write-Host "Docker 容器启动成功！" -ForegroundColor Green
Write-Host ""

# 2. 等待数据库就绪
Write-Host "[2/4] 等待数据库就绪..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
Write-Host "数据库已就绪！" -ForegroundColor Green
Write-Host ""

# 3. 启动后端 API 服务
Write-Host "[3/4] 启动后端 API 服务 (端口 8000)..." -ForegroundColor Yellow
Set-Location "$WORKSPACE\services\api"
$env:DATABASE_URL = "mysql+pymysql://campus:campus@127.0.0.1:3306/campus_device"
$env:REDIS_URL = "redis://127.0.0.1:6379/0"
$env:JWT_SECRET = "dev-secret-key-change-in-production"
$env:APP_ENV = "development"
$env:APP_DEBUG = "true"

# 使用后台进程启动 uvicorn
$uvicornJob = Start-Job -ScriptBlock {
    Set-Location $using:WORKSPACE\services\api
    $env:DATABASE_URL = "mysql+pymysql://campus:campus@127.0.0.1:3306/campus_device"
    $env:REDIS_URL = "redis://127.0.0.1:6379/0"
    $env:JWT_SECRET = "dev-secret-key-change-in-production"
    $env:APP_ENV = "development"
    $env:APP_DEBUG = "true"
    & python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
}
Write-Host "后端 API 服务已启动 (后台运行)..." -ForegroundColor Green
Write-Host ""

# 4. 启动管理后台 Web 服务
Write-Host "[4/4] 启动管理后台 Web 服务 (端口 3000)..." -ForegroundColor Yellow
Set-Location "$WORKSPACE\apps\admin"

# 检查 node_modules 是否存在
if (-not (Test-Path "node_modules")) {
    Write-Host "正在安装依赖..." -ForegroundColor Yellow
    npm install
}

# 使用后台进程启动 vite dev
$viteJob = Start-Job -ScriptBlock {
    Set-Location $using:WORKSPACE\apps\admin
    & npm run dev
}
Write-Host "管理后台 Web 服务已启动 (后台运行)..." -ForegroundColor Green
Write-Host ""

# 等待服务启动
Write-Host "等待服务启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 8

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  所有服务已启动！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  管理后台 Web:  http://localhost:3000" -ForegroundColor Cyan
Write-Host "  后端 API:      http://localhost:8000" -ForegroundColor Cyan
Write-Host "  API 文档：      http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  MySQL:         127.0.0.1:3306" -ForegroundColor Cyan
Write-Host "  Redis:         127.0.0.1:6379" -ForegroundColor Cyan
Write-Host ""
Write-Host "按任意键停止所有服务..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# 停止服务
Write-Host ""
Write-Host "正在停止所有服务..." -ForegroundColor Yellow
Stop-Job -Id $uvicornJob
Stop-Job -Id $viteJob
Remove-Job -Id $uvicornJob
Remove-Job -Id $viteJob
Set-Location "$WORKSPACE\deploy"
docker-compose -f docker-compose.dev.yml down
Write-Host "所有服务已停止" -ForegroundColor Green
