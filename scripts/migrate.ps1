$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$apiDir = Join-Path $repoRoot "services\api"
$envFile = Join-Path $repoRoot "deploy\.env"

if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            Set-Item -Path "Env:$name" -Value $value
        }
    }
}

if (-not $env:DATABASE_URL) {
    $env:DATABASE_URL = "mysql+pymysql://campus:campus@127.0.0.1:3306/campus_device"
}

Push-Location $apiDir
try {
    Write-Host "执行数据库迁移 ..."
    alembic upgrade head
} finally {
    Pop-Location
}
