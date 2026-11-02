$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$consoleDir = Join-Path $root "apps\console"
$electronDir = Join-Path $root "electron"
$logsDir = Join-Path $env:TEMP "NEXUS_V1_DESKTOP_LOGS"
New-Item -ItemType Directory -Force -Path $logsDir | Out-Null
$apiOut = Join-Path $logsDir "runtime.stdout.log"
$apiErr = Join-Path $logsDir "runtime.stderr.log"
$uiOut = Join-Path $logsDir "console.stdout.log"
$uiErr = Join-Path $logsDir "console.stderr.log"
$electronOut = Join-Path $logsDir "electron.stdout.log"
$electronErr = Join-Path $logsDir "electron.stderr.log"

function Test-HttpEndpoint([string]$Url) {
    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2
        return ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500)
    } catch { return $false }
}
function Wait-HttpEndpoint([string]$Url, [int]$Seconds, [string]$Name) {
    $deadline = (Get-Date).AddSeconds($Seconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-HttpEndpoint $Url) { return }
        Start-Sleep -Milliseconds 750
    }
    throw "No se pudo validar $Name en $Url dentro de $Seconds segundos. Logs: $logsDir"
}

foreach ($required in @(
    (Join-Path $root "server.py"),
    (Join-Path $consoleDir "package.json"),
    (Join-Path $consoleDir "package-lock.json"),
    (Join-Path $electronDir "package.json"),
    (Join-Path $electronDir "package-lock.json"),
    (Join-Path $electronDir "main.js")
)) { if (!(Test-Path $required)) { throw "Falta un archivo necesario: $required" } }

$npm = Get-Command npm -ErrorAction Stop
$npmCmd = Join-Path (Split-Path $npm.Source -Parent) "npm.cmd"
if (!(Test-Path $npmCmd)) { $npmCmd = "npm.cmd" }

if (!(Test-Path (Join-Path $consoleDir "node_modules\vite\bin\vite.js"))) {
    Write-Host "Instalando dependencias de la consola..." -ForegroundColor Cyan
    Push-Location $consoleDir
    try { & $npmCmd ci; if ($LASTEXITCODE -ne 0) { throw "npm ci falló en apps/console." } }
    finally { Pop-Location }
}
if (!(Test-Path (Join-Path $electronDir "node_modules\electron\dist\electron.exe"))) {
    Write-Host "Instalando dependencias de Electron..." -ForegroundColor Cyan
    Push-Location $electronDir
    try { & $npmCmd ci; if ($LASTEXITCODE -ne 0) { throw "npm ci falló en electron." } }
    finally { Pop-Location }
}

if (!(Test-HttpEndpoint "http://127.0.0.1:8765/api/status")) {
    $uv = Get-Command uv -ErrorAction SilentlyContinue
    if (!$uv) { throw "No se encontró uv en PATH. Activá el entorno de NEXUS o instalá uv." }
    Write-Host "Iniciando runtime modular (8765)..." -ForegroundColor Cyan
    Start-Process -FilePath $uv.Source -ArgumentList @("run", "python", "-u", "server.py") -WorkingDirectory $root -RedirectStandardOutput $apiOut -RedirectStandardError $apiErr | Out-Null
}
Wait-HttpEndpoint "http://127.0.0.1:8765/api/status" 60 "runtime NEXUS"

if (!(Test-HttpEndpoint "http://127.0.0.1:5173/")) {
    Write-Host "Iniciando consola React (5173)..." -ForegroundColor Cyan
    Start-Process -FilePath $env:ComSpec -ArgumentList @("/c", "`"$npmCmd`" run dev -- --host 127.0.0.1 --port 5173 --strictPort") -WorkingDirectory $consoleDir -RedirectStandardOutput $uiOut -RedirectStandardError $uiErr | Out-Null
}
Wait-HttpEndpoint "http://127.0.0.1:5173/" 60 "consola React"
$status = Invoke-RestMethod -Uri "http://127.0.0.1:8765/api/status" -TimeoutSec 5
if ($status.status -ne "online") { throw "El runtime no informa estado online: $($status.status)" }

Write-Host "Iniciando Electron..." -ForegroundColor Green
Start-Process -FilePath $env:ComSpec -ArgumentList @("/c", "`"$npmCmd`" start") -WorkingDirectory $electronDir -RedirectStandardOutput $electronOut -RedirectStandardError $electronErr | Out-Null
Write-Host "NEXUS Desktop iniciado." -ForegroundColor Green
Write-Host "Runtime: http://127.0.0.1:8765/api/status"
Write-Host "Consola: http://127.0.0.1:5173/assistant"
Write-Host "Logs: $logsDir"
