$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$apiDir = Join-Path $repoRoot "services\api"
$envFile = Join-Path $repoRoot "deploy\.env"

if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match "^\s*([^#][^=]+)=(.*)$") {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            Set-Item -Path "Env:$name" -Value $value
        }
    }
}

Push-Location $apiDir
try {
    Write-Host "启动逾期订单扫描..."
    & ".\venv\Scripts\python.exe" -m app.tasks.overdue_scanner
} finally {
    Pop-Location
}
