
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$consoleDir = Join-Path $root "apps\console"
$electronDir = Join-Path $root "electron"

$logsDir = Join-Path $env:TEMP "NEXUS_V1_DESKTOP_LOGS"

New-Item -ItemType Directory -Force -Path $logsDir | Out-Null

$electronOut = Join-Path $logsDir "electron.stdout.log"
$electronErr = Join-Path $logsDir "electron.stderr.log"

function Resolve-Npm {
    $npm = Get-Command npm -ErrorAction Stop
    $npmCmd = Join-Path (Split-Path $npm.Source -Parent) "npm.cmd"

    if (Test-Path $npmCmd) {
        return $npmCmd
    }

    return "npm.cmd"
}

$npmCmd = Resolve-Npm

foreach ($required in @(
    (Join-Path $root "server.py"),
    (Join-Path $consoleDir "package.json"),
    (Join-Path $consoleDir "package-lock.json"),
    (Join-Path $electronDir "package.json"),
    (Join-Path $electronDir "package-lock.json"),
    (Join-Path $electronDir "main.js"),
    (Join-Path $electronDir "preload.js")
)) {
    if (!(Test-Path $required)) {
        throw "Falta un archivo necesario: $required"
    }
}

if (!(Get-Command uv -ErrorAction SilentlyContinue)) {
    throw "No se encontró uv en PATH."
}

if (!(Test-Path (Join-Path $consoleDir "node_modules\vite\bin\vite.js"))) {
    Write-Host "Instalando dependencias de la consola..." -ForegroundColor Cyan

    Push-Location $consoleDir

    try {
        & $npmCmd ci

        if ($LASTEXITCODE -ne 0) {
            throw "npm ci falló en apps/console."
        }
    }
    finally {
        Pop-Location
    }
}

if (!(Test-Path (Join-Path $electronDir "node_modules\electron\dist\electron.exe"))) {
    Write-Host "Instalando dependencias de Electron..." -ForegroundColor Cyan

    Push-Location $electronDir

    try {
        & $npmCmd ci

        if ($LASTEXITCODE -ne 0) {
            throw "npm ci falló en electron."
        }
    }
    finally {
        Pop-Location
    }
}

Write-Host ""
Write-Host "Iniciando NEXUS Desktop..." -ForegroundColor Green
Write-Host "Electron administrará el runtime y la consola."
Write-Host "Los registros estarán en: $logsDir"
Write-Host ""

Push-Location $electronDir

try {
    Start-Process `
        -FilePath $npmCmd `
        -ArgumentList @("start") `
        -WorkingDirectory $electronDir `
        -RedirectStandardOutput $electronOut `
        -RedirectStandardError $electronErr `
        -WindowStyle Hidden

    Write-Host "NEXUS Desktop iniciado." -ForegroundColor Green
}
finally {
    Pop-Location
}
