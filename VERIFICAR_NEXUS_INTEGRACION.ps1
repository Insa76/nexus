$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$desktop = [Environment]::GetFolderPath("Desktop")
$report = Join-Path $desktop ("NEXUS_INTEGRACION_RESULTADOS_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".txt")
function Section([string]$Title) { "`r`n=== $Title ===" | Tee-Object -FilePath $report -Append }
Set-Location $root
"NEXUS V1 — Verificación de integración" | Tee-Object -FilePath $report
"Fecha: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Tee-Object -FilePath $report -Append
"Proyecto: $root" | Tee-Object -FilePath $report -Append
Section "1/4 Validación de rutas y manifest"
$required = @("server.py", "apps\console\package.json", "apps\console\package-lock.json", "electron\package.json", "electron\package-lock.json", "electron\main.js", "start-nexus-desktop-dev.ps1")
foreach ($rel in $required) { if (!(Test-Path (Join-Path $root $rel))) { throw "Falta archivo: $rel" }; "OK: $rel" | Tee-Object -FilePath $report -Append }
$ep = Get-Content (Join-Path $root "electron\package.json") -Raw | ConvertFrom-Json
if ($ep.main -ne "main.js") { throw "electron/package.json debe tener main=main.js; actual: $($ep.main)" }
if ($ep.devDependencies.electron -ne "^40.6.0") { throw "electron/package.json no coincide con el lock de Electron esperado." }
Section "2/4 Compilación sintáctica Python"
uv run python -m compileall -q .\packages .\tests .\server.py .\nexus_http_security.py 2>&1 | Tee-Object -FilePath $report -Append
$cc = $LASTEXITCODE
"Código compilación: $cc" | Tee-Object -FilePath $report -Append
if ($cc -ne 0) { throw "Falló compileall. Informe: $report" }
Section "3/4 Suite Python"
uv run pytest -q --ignore=backups --ignore=dist --ignore=build 2>&1 | Tee-Object -FilePath $report -Append
$tc = $LASTEXITCODE
"Código pytest: $tc" | Tee-Object -FilePath $report -Append
if ($tc -ne 0) { throw "Falló pytest. Informe: $report" }
Section "4/4 Build de apps/console"
$console = Join-Path $root "apps\console"
$npm = Get-Command npm -ErrorAction Stop
$npmCmd = Join-Path (Split-Path $npm.Source -Parent) "npm.cmd"
if (!(Test-Path $npmCmd)) { $npmCmd = "npm.cmd" }
Push-Location $console
try {
    if (!(Test-Path ".\node_modules\vite\bin\vite.js")) { & $npmCmd ci 2>&1 | Tee-Object -FilePath $report -Append; if ($LASTEXITCODE -ne 0) { throw "npm ci falló en apps/console" } }
    & $npmCmd run build 2>&1 | Tee-Object -FilePath $report -Append
    $bc = $LASTEXITCODE
    "Código build React: $bc" | Tee-Object -FilePath $report -Append
    if ($bc -ne 0) { throw "Falló el build React. Informe: $report" }
} finally { Pop-Location }
Section "Resultado"
"COMPILACIÓN PYTHON: OK`nSUITE PYTHON: OK`nBUILD REACT: OK" | Tee-Object -FilePath $report -Append
Write-Host "Verificación completada. Informe: $report" -ForegroundColor Green
